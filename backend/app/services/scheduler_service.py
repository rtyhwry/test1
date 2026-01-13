"""
Scheduler Service - Handle scheduled and cron tasks
"""
import asyncio
from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID
from croniter import croniter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.models.task import TestTask
from app.models.scheduled_job import ScheduledJob
from app.core.config import settings


class SchedulerService:
    """Service for scheduling test tasks"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_due_tasks(self) -> List[TestTask]:
        """Get tasks that are due for execution"""
        now = datetime.now(timezone.utc)
        
        # Get scheduled tasks that are due
        result = await self.db.execute(
            select(TestTask).where(
                and_(
                    TestTask.status == "pending",
                    TestTask.trigger_type == "scheduled",
                    TestTask.schedule_time <= now
                )
            )
        )
        scheduled_tasks = list(result.scalars().all())
        
        # Get cron tasks from scheduled_jobs
        job_result = await self.db.execute(
            select(ScheduledJob).where(
                and_(
                    ScheduledJob.is_enabled == True,
                    ScheduledJob.next_run_time <= now
                )
            )
        )
        due_jobs = job_result.scalars().all()
        
        # Get corresponding tasks for cron jobs
        for job in due_jobs:
            task_result = await self.db.execute(
                select(TestTask).where(
                    and_(
                        TestTask.id == job.task_id,
                        TestTask.status == "pending"
                    )
                )
            )
            task = task_result.scalar_one_or_none()
            if task:
                scheduled_tasks.append(task)
            
            # Update next run time for cron job
            await self._update_next_run_time(job)
        
        return scheduled_tasks
    
    async def create_scheduled_job(
        self,
        task_id: UUID,
        cron_expression: str,
        timezone: str = "Asia/Shanghai"
    ) -> ScheduledJob:
        """Create a scheduled job for a task"""
        # Calculate next run time
        cron = croniter(cron_expression, datetime.now())
        next_run = cron.get_next(datetime)
        
        job = ScheduledJob(
            task_id=task_id,
            job_type="cron",
            cron_expression=cron_expression,
            timezone=timezone,
            next_run_time=next_run,
            is_enabled=True
        )
        
        self.db.add(job)
        await self.db.commit()
        await self.db.refresh(job)
        
        return job
    
    async def _update_next_run_time(self, job: ScheduledJob) -> None:
        """Update the next run time for a cron job"""
        if job.cron_expression:
            cron = croniter(job.cron_expression, datetime.now())
            job.next_run_time = cron.get_next(datetime)
            job.last_run_time = datetime.now(timezone.utc)
            await self.db.commit()
    
    async def enable_job(self, job_id: UUID) -> None:
        """Enable a scheduled job"""
        result = await self.db.execute(
            select(ScheduledJob).where(ScheduledJob.id == job_id)
        )
        job = result.scalar_one_or_none()
        
        if job:
            job.is_enabled = True
            
            # Recalculate next run time
            if job.cron_expression:
                cron = croniter(job.cron_expression, datetime.now())
                job.next_run_time = cron.get_next(datetime)
            
            await self.db.commit()
    
    async def disable_job(self, job_id: UUID) -> None:
        """Disable a scheduled job"""
        result = await self.db.execute(
            select(ScheduledJob).where(ScheduledJob.id == job_id)
        )
        job = result.scalar_one_or_none()
        
        if job:
            job.is_enabled = False
            await self.db.commit()
    
    async def delete_job(self, job_id: UUID) -> None:
        """Delete a scheduled job"""
        result = await self.db.execute(
            select(ScheduledJob).where(ScheduledJob.id == job_id)
        )
        job = result.scalar_one_or_none()
        
        if job:
            await self.db.delete(job)
            await self.db.commit()


class SchedulerRunner:
    """Background runner for the scheduler"""
    
    def __init__(self):
        self.running = False
    
    async def start(self):
        """Start the scheduler loop"""
        self.running = True
        
        while self.running:
            try:
                await self._check_and_run_tasks()
            except Exception as e:
                print(f"Scheduler error: {e}")
            
            await asyncio.sleep(settings.SCHEDULER_CHECK_INTERVAL)
    
    async def stop(self):
        """Stop the scheduler loop"""
        self.running = False
    
    async def _check_and_run_tasks(self):
        """Check for due tasks and submit them for execution"""
        # This would typically use a database session from a pool
        # and submit tasks to a Celery queue
        pass
