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


# ---------------- RECOVERY (IMPORTANT) ---------------- #

def recover_pending_jobs(db):
    print("Recovering pending jobs...")

    pending_jobs = db.query(Job).filter(Job.status == "pending").all()

    for job in pending_jobs:
        redis_client.lpush(
            "job_queue",
            json.dumps({"job_id": job.id})
        )

    print(f"Recovered {len(pending_jobs)} jobs")


# ---------------- WORKER ---------------- #

async def run_worker():
    print("Worker started... waiting for jobs...")

    db = SessionLocal()

    # 🔥 Recover jobs at startup
    recover_pending_jobs(db)

    while True:
        try:
            # ---------------- DELAYED JOBS ---------------- #

            now = time.time()

            ready_jobs = redis_client.zrangebyscore(
                "delayed_jobs",
                0,
                now
            )

            for job_str in ready_jobs:
                job_data = json.loads(job_str)

                redis_client.lpush(
                    "job_queue",
                    json.dumps({"job_id": job_data["job_id"]})
                )

                redis_client.zrem("delayed_jobs", job_str)

                print(f"Moved scheduled job {job_data['job_id']} to main queue")

            # ---------------- FETCH JOB ---------------- #

            job_data = redis_client.brpop("job_queue", timeout=2)

            if not job_data:
                continue

            _, job_data = job_data
            job_data = json.loads(job_data)
            job_id = job_data["job_id"]

            
            try:
                job = db.query(Job).filter(Job.id == job_id).first()
            except Exception as e:
                print("DB error while fetching job:", str(e))
                db.rollback()

                # requeue job so it's not lost
                redis_client.lpush(
                    "job_queue",
                    json.dumps({"job_id": job_id})
                )

                continue

            if not job:
                print(f"Job {job_id} not found")
                continue

            # Prevent duplicate processing
            if job.status != "pending":
                continue

            print(f"Processing job: {job_id}")

            job.status = "processing"

            try:
                db.commit()
            except Exception as e:
                print("DB commit error:", str(e))
                db.rollback()

                redis_client.lpush(
                    "job_queue",
                    json.dumps({"job_id": job.id})
                )

                continue

            # ---------------- PROCESS JOB ---------------- #

            try:
                # simulate delay (optional)
                # await asyncio.sleep(5)

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

                    redis_client.zadd(
                        "delayed_jobs",
                        {
                            json.dumps({"job_id": job.id}): time.time() + delay
                        }
                    )

                else:
                    print(f"Job {job.id} failed after retries")

                    job.status = "failed"
                    job.error = f"LLM failed after retries: {str(e)}"
                    db.commit()

                    redis_client.lpush(
                        "failed_jobs",
                        json.dumps({
                            "job_id": job.id,
                            "error": job.error,
                            "failed_at": time.time()
                        })
                    )

                    traceback.print_exc()

        except Exception as e:
            print("Worker loop error:", str(e))
            traceback.print_exc()

        finally:
            db.rollback()  # safety


# ---------------- ENTRY ---------------- #

if __name__ == "__main__":
    asyncio.run(run_worker())