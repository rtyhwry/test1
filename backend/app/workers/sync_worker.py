"""
Sync worker - handles synchronization with external systems
"""
import asyncio
from typing import Dict, List
from uuid import UUID

from app.workers.celery_app import celery_app


@celery_app.task
def sync_alm_tasks() -> Dict:
    """Sync test tasks from ALM platform"""
    return asyncio.run(_sync_alm_tasks_async())


async def _sync_alm_tasks_async() -> Dict:
    """Async ALM sync logic"""
    from app.core.database import async_session_factory
    from app.models.integration import IntegrationConfig
    from sqlalchemy import select
    
    async with async_session_factory() as db:
        # Get ALM configurations
        result = await db.execute(
            select(IntegrationConfig).where(
                IntegrationConfig.integration_type == "alm",
                IntegrationConfig.is_enabled == True
            )
        )
        configs = result.scalars().all()
        
        synced_count = 0
        
        for config in configs:
            try:
                count = await _sync_from_alm_config(config, db)
                synced_count += count
            except Exception as e:
                print(f"ALM sync error for {config.name}: {e}")
        
        return {"synced": synced_count}


async def _sync_from_alm_config(config, db) -> int:
    """Sync from a specific ALM configuration"""
    from app.core.security import decrypt_string
    
    alm_config = config.config
    alm_url = alm_config.get("url")
    username = alm_config.get("username")
    password = decrypt_string(alm_config.get("password", ""))
    
    # TODO: Implement actual ALM API calls
    # 1. Authenticate with ALM
    # 2. Fetch test plans/cycles
    # 3. Fetch test cases
    # 4. Create/update local records
    
    return 0


@celery_app.task
def sync_alm_test_suite(suite_id: str, alm_suite_id: str) -> Dict:
    """Sync a specific test suite from ALM"""
    return asyncio.run(_sync_alm_test_suite_async(suite_id, alm_suite_id))


async def _sync_alm_test_suite_async(suite_id: str, alm_suite_id: str) -> Dict:
    """Sync test suite from ALM"""
    from app.core.database import async_session_factory
    from app.models.test_suite import TestSuite, TestCase
    from sqlalchemy import select
    
    async with async_session_factory() as db:
        result = await db.execute(
            select(TestSuite).where(TestSuite.id == UUID(suite_id))
        )
        suite = result.scalar_one_or_none()
        
        if not suite:
            return {"success": False, "error": "Suite not found"}
        
        # TODO: Fetch cases from ALM and sync
        
        return {"success": True, "synced_cases": 0}


@celery_app.task
def sync_gitlab_test_cases(suite_id: str) -> Dict:
    """Sync test cases from GitLab repository"""
    return asyncio.run(_sync_gitlab_test_cases_async(suite_id))


async def _sync_gitlab_test_cases_async(suite_id: str) -> Dict:
    """Discover and sync test cases from GitLab"""
    from app.core.database import async_session_factory
    from app.models.test_suite import TestSuite, TestCase
    from sqlalchemy import select
    
    async with async_session_factory() as db:
        result = await db.execute(
            select(TestSuite).where(TestSuite.id == UUID(suite_id))
        )
        suite = result.scalar_one_or_none()
        
        if not suite or not suite.git_repo:
            return {"success": False, "error": "Suite not found or no git repo"}
        
        # TODO: Clone/pull repo and discover test cases
        # 1. Clone repository
        # 2. Parse test files (pytest, robot, etc.)
        # 3. Extract test case metadata
        # 4. Create/update TestCase records
        
        discovered_cases = await _discover_tests_from_repo(suite)
        
        for case_info in discovered_cases:
            # Check if case exists
            existing = await db.execute(
                select(TestCase).where(
                    TestCase.suite_id == suite.id,
                    TestCase.script_path == case_info["script_path"],
                    TestCase.method_name == case_info["method_name"]
                )
            )
            existing_case = existing.scalar_one_or_none()
            
            if existing_case:
                # Update existing
                existing_case.name = case_info["name"]
                existing_case.description = case_info.get("description")
            else:
                # Create new
                new_case = TestCase(
                    suite_id=suite.id,
                    name=case_info["name"],
                    description=case_info.get("description"),
                    script_path=case_info["script_path"],
                    class_name=case_info.get("class_name"),
                    method_name=case_info["method_name"],
                    tags=case_info.get("tags", [])
                )
                db.add(new_case)
        
        await db.commit()
        
        return {"success": True, "discovered": len(discovered_cases)}


async def _discover_tests_from_repo(suite) -> List[Dict]:
    """Discover test cases from repository"""
    # TODO: Implement actual test discovery
    # This would parse Python files for pytest tests
    # or Robot Framework files, etc.
    
    return []


@celery_app.task
def sync_artifacts() -> Dict:
    """Sync artifacts from artifact repository"""
    return asyncio.run(_sync_artifacts_async())


async def _sync_artifacts_async() -> Dict:
    """Sync artifacts from Nexus/Artifactory"""
    from app.core.database import async_session_factory
    from app.models.integration import IntegrationConfig
    from app.models.artifact import ArtifactVersion
    from sqlalchemy import select
    
    async with async_session_factory() as db:
        # Get artifact repository configurations
        result = await db.execute(
            select(IntegrationConfig).where(
                IntegrationConfig.integration_type == "artifact",
                IntegrationConfig.is_enabled == True
            )
        )
        configs = result.scalars().all()
        
        synced_count = 0
        
        for config in configs:
            try:
                count = await _sync_from_artifact_repo(config, db)
                synced_count += count
            except Exception as e:
                print(f"Artifact sync error for {config.name}: {e}")
        
        return {"synced": synced_count}


async def _sync_from_artifact_repo(config, db) -> int:
    """Sync from artifact repository"""
    from app.core.security import decrypt_string
    from app.models.artifact import ArtifactVersion
    from sqlalchemy import select
    
    repo_config = config.config
    repo_type = repo_config.get("type")  # nexus, artifactory
    repo_url = repo_config.get("url")
    username = repo_config.get("username")
    password = decrypt_string(repo_config.get("password", ""))
    
    # TODO: Implement actual repository API calls
    # 1. Query repository for available artifacts
    # 2. Get version list
    # 3. Create/update ArtifactVersion records
    
    return 0


@celery_app.task
def push_results_to_alm(execution_id: str) -> Dict:
    """Push test results back to ALM"""
    return asyncio.run(_push_results_to_alm_async(execution_id))


async def _push_results_to_alm_async(execution_id: str) -> Dict:
    """Push execution results to ALM platform"""
    from app.core.database import async_session_factory
    from app.models.task import TaskExecution, TestCaseResult
    from app.models.test_suite import TestCase
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
        
        # TODO: Push results to ALM
        # 1. Get ALM configuration
        # 2. Map local results to ALM test run
        # 3. Update ALM test instances with results
        
        return {"success": True, "pushed_results": len(execution.case_results)}
