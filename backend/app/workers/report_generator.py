"""
Report generator worker - generates test reports in various formats
"""
import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Dict
from uuid import UUID

from app.workers.celery_app import celery_app


@celery_app.task
def generate_html_report(execution_id: str) -> Dict:
    """Generate HTML report for an execution"""
    return asyncio.run(_generate_html_report_async(execution_id))


async def _generate_html_report_async(execution_id: str) -> Dict:
    """Generate HTML report"""
    from app.core.database import async_session_factory
    from app.models.task import TaskExecution, TestCaseResult
    from app.models.report import TestReport
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload
    from jinja2 import Template
    
    async with async_session_factory() as db:
        # Get execution with results
        result = await db.execute(
            select(TaskExecution)
            .where(TaskExecution.id == UUID(execution_id))
            .options(
                selectinload(TaskExecution.case_results),
                selectinload(TaskExecution.task)
            )
        )
        execution = result.scalar_one_or_none()
        
        if not execution:
            return {"success": False, "error": "Execution not found"}
        
        # Get or create report
        report_result = await db.execute(
            select(TestReport).where(TestReport.execution_id == execution.id)
        )
        report = report_result.scalar_one_or_none()
        
        if not report:
            return {"success": False, "error": "Report not found"}
        
        # Generate HTML
        html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>{{ report_name }}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background: #1890ff; color: white; padding: 20px; }
        .summary { display: flex; margin: 20px 0; }
        .summary-item { 
            flex: 1; 
            text-align: center; 
            padding: 20px;
            border: 1px solid #ddd;
            margin: 5px;
        }
        .passed { background: #52c41a; color: white; }
        .failed { background: #ff4d4f; color: white; }
        .skipped { background: #faad14; color: white; }
        table { width: 100%; border-collapse: collapse; }
        th, td { border: 1px solid #ddd; padding: 10px; text-align: left; }
        th { background: #fafafa; }
        .status-passed { color: #52c41a; }
        .status-failed { color: #ff4d4f; }
        .status-skipped { color: #faad14; }
        .status-error { color: #ff4d4f; }
    </style>
</head>
<body>
    <div class="header">
        <h1>{{ report_name }}</h1>
        <p>Generated: {{ generated_at }}</p>
    </div>
    
    <div class="summary">
        <div class="summary-item">
            <h2>{{ total }}</h2>
            <p>Total Cases</p>
        </div>
        <div class="summary-item passed">
            <h2>{{ passed }}</h2>
            <p>Passed</p>
        </div>
        <div class="summary-item failed">
            <h2>{{ failed }}</h2>
            <p>Failed</p>
        </div>
        <div class="summary-item skipped">
            <h2>{{ skipped }}</h2>
            <p>Skipped</p>
        </div>
    </div>
    
    <h2>Test Results</h2>
    <table>
        <thead>
            <tr>
                <th>Test Case</th>
                <th>Status</th>
                <th>Duration</th>
                <th>Error</th>
            </tr>
        </thead>
        <tbody>
            {% for case in cases %}
            <tr>
                <td>{{ case.name }}</td>
                <td class="status-{{ case.status }}">{{ case.status }}</td>
                <td>{{ case.duration }}ms</td>
                <td>{{ case.error or '-' }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</body>
</html>
        """
        
        template = Template(html_template)
        html_content = template.render(
            report_name=report.report_name,
            generated_at=datetime.now().isoformat(),
            total=report.total_cases,
            passed=report.passed,
            failed=report.failed,
            skipped=report.skipped,
            cases=[
                {
                    "name": r.case_name,
                    "status": r.status,
                    "duration": r.duration or 0,
                    "error": r.error_message
                }
                for r in execution.case_results
            ]
        )
        
        # Save HTML file (in production, upload to MinIO)
        html_path = f"/tmp/report_{execution_id}.html"
        with open(html_path, "w") as f:
            f.write(html_content)
        
        # Update report with path
        report.html_report_path = html_path
        await db.commit()
        
        return {"success": True, "path": html_path}


@celery_app.task
def generate_json_report(execution_id: str) -> Dict:
    """Generate JSON report for an execution"""
    return asyncio.run(_generate_json_report_async(execution_id))


async def _generate_json_report_async(execution_id: str) -> Dict:
    """Generate JSON report"""
    from app.core.database import async_session_factory
    from app.models.task import TaskExecution
    from app.models.report import TestReport
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload
    
    async with async_session_factory() as db:
        result = await db.execute(
            select(TaskExecution)
            .where(TaskExecution.id == UUID(execution_id))
            .options(selectinload(TaskExecution.case_results))
        )
        execution = result.scalar_one_or_none()
        
        if not execution:
            return {"success": False, "error": "Execution not found"}
        
        # Build JSON report
        report_data = {
            "execution_id": str(execution.id),
            "task_id": str(execution.task_id),
            "status": execution.status,
            "started_at": execution.started_at.isoformat() if execution.started_at else None,
            "finished_at": execution.finished_at.isoformat() if execution.finished_at else None,
            "duration": execution.duration,
            "summary": {
                "total": execution.total_cases,
                "passed": execution.passed_cases,
                "failed": execution.failed_cases,
                "skipped": execution.skipped_cases,
                "error": execution.error_cases,
                "pass_rate": execution.pass_rate
            },
            "environment": {
                "software_version": execution.software_version,
                "git_commit": execution.git_commit
            },
            "results": [
                {
                    "case_id": str(r.case_id) if r.case_id else None,
                    "case_name": r.case_name,
                    "status": r.status,
                    "duration": r.duration,
                    "error_message": r.error_message,
                    "error_stack": r.error_stack
                }
                for r in execution.case_results
            ]
        }
        
        # Save JSON file
        json_path = f"/tmp/report_{execution_id}.json"
        with open(json_path, "w") as f:
            json.dump(report_data, f, indent=2)
        
        # Update report
        report_result = await db.execute(
            select(TestReport).where(TestReport.execution_id == execution.id)
        )
        report = report_result.scalar_one_or_none()
        
        if report:
            report.json_report_path = json_path
            await db.commit()
        
        return {"success": True, "path": json_path}


@celery_app.task
def generate_daily_report(project_id: str, date: str) -> Dict:
    """Generate daily summary report for a project"""
    # TODO: Implement daily report generation
    return {"success": True, "message": "Daily report generated"}


@celery_app.task
def generate_weekly_report(project_id: str, week: str) -> Dict:
    """Generate weekly summary report for a project"""
    # TODO: Implement weekly report generation
    return {"success": True, "message": "Weekly report generated"}
