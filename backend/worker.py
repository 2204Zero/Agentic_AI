from dotenv import load_dotenv
load_dotenv()

import asyncio
import time
import traceback

from agents.analyzer_agents import run_pipeline
from config.database import SessionLocal
from models.db_models import Job


async def run_worker():
    while True:
        db = SessionLocal()

        try:
            job = db.query(Job).filter(Job.status == "pending").first()

            if job:
                print(f"Processing job: {job.id}")

                job.status = "processing"
                db.commit()

                try:
                    # Run AI
                    result = await run_pipeline(job.submission.code)
                    print("RAW RESULT:", result)
                    # Save result
                    job.result = result
                    job.status = "completed"

                    db.commit()

                    print(f"Job {job.id} completed")

                except Exception as e:
                    job.status = "failed"
                    job.error = f"LLM failed: {str(e)}"
                    db.commit()

                    print(f"Job {job.id} failed")
                    traceback.print_exc()
            else:
                print("No pending jobs")

        finally:
            db.close()

        await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(run_worker())