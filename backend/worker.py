from dotenv import load_dotenv
load_dotenv()

import asyncio
import json
import traceback
import time

from agents.analyzer_agents import run_pipeline
from config.database import SessionLocal
from config.redis_client import redis_client
from models.db_models import Job


async def run_worker():
    print("Worker started... waiting for jobs...")

    while True:

        # ZSET: check scheduled (delayed) jobs
        now = time.time()

        ready_jobs = redis_client.zrangebyscore(
            "delayed_jobs",
            0,
            now
        )

        for job_str in ready_jobs:
            job_data = json.loads(job_str)

            # move to main queue
            redis_client.lpush(
                "job_queue",
                json.dumps({"job_id": job_data["job_id"]})
            )

            # remove from delayed set
            redis_client.zrem("delayed_jobs", job_str)

            print(f"Moved scheduled job {job_data['job_id']} to main queue")

        db = SessionLocal()

        try:
            # non-blocking pop
            job_data = redis_client.brpop("job_queue", timeout=2)

            if not job_data:
                continue

            _, job_data = job_data
            job_data = json.loads(job_data)
            job_id = job_data["job_id"]

            print(f"Processing job: {job_id}")

            job = db.query(Job).filter(Job.id == job_id).first()

            if not job:
                print(f"Job {job_id} not found")
                continue

            # Prevent duplicate processing
            if job.status != "pending":
                continue

            job.status = "processing"
            db.commit()

            try:
                # Run AI pipeline
                await asyncio.sleep(5)
                result = await run_pipeline(job.submission.code)

                job.result = result
                job.status = "completed"
                db.commit()

                print(f"Job {job.id} completed")

            except Exception as e:
                MAX_RETRIES = 3

                job.retry_count = (job.retry_count or 0) + 1

                if job.retry_count < MAX_RETRIES:
                    print(f"Retrying job {job.id} ({job.retry_count})")

                    job.status = "pending"
                    db.commit()

                    delay = 2 ** job.retry_count

                    # ZSET scheduling
                    redis_client.zadd(
                        "delayed_jobs",
                        {
                            json.dumps({"job_id": job.id}): time.time() + delay
                        }
                    )

                    continue

                else:
                    print(f"Job {job.id} failed after retries")

                    job.status = "failed"
                    job.error = f"LLM failed after retries: {str(e)}"
                    db.commit()

                    traceback.print_exc()

        finally:
            db.close()


if __name__ == "__main__":
    asyncio.run(run_worker())