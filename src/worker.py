import os
import time
from sqlmodel import Session, select
from db import engine, init_db
from models import Job, Case
from storage import load_case_document
from ai import generate_prior_auth_draft


def process_one_job() -> bool:
    with Session(engine) as session:
        job = session.exec(select(Job).where(Job.status == "queued")).first()
        if not job:
            return False
        job.status = "running"
        job.attempts += 1
        session.add(job)
        session.commit()

        case = session.get(Case, job.case_id)
        if not case:
            job.status = "failed"
            job.error = "case not found"
            session.add(job)
            session.commit()
            return True

        case.status = "running"
        session.add(case)
        session.commit()

        try:
            chunks = [c.strip() for c in load_case_document(case.id).split("\n") if c.strip()]
            draft, cites = generate_prior_auth_draft(case.patient_name, case.payer, chunks)
            case.draft_text = draft
            case.citations = "||".join(cites)
            case.status = "generated"
            job.status = "done"
            session.add(case)
            session.add(job)
            session.commit()
        except Exception as e:
            job.status = "failed"
            job.error = str(e)
            case.status = "failed"
            session.add(case)
            session.add(job)
            session.commit()
        return True


def run_forever():
    poll = float(os.getenv("WORKER_POLL_SECONDS", "1.0"))
    init_db()
    while True:
        processed = process_one_job()
        if not processed:
            time.sleep(poll)


if __name__ == "__main__":
    run_forever()
