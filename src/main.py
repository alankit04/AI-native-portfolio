from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException
from sqlmodel import Session
import strawberry
from strawberry.fastapi import GraphQLRouter
from db import init_db, get_session
from models import Case, Job
from storage import save_case_document

app = FastAPI(title="Clinical Auth Copilot")

@app.on_event("startup")
def startup():
    init_db()

@app.post("/v1/cases")
def create_case(
    case_id: str = Form(...),
    patient_name: str = Form(...),
    payer: str = Form(...),
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
):
    if session.get(Case, case_id):
        raise HTTPException(400, "case exists")
    save_case_document(case_id, file.file.read())
    case = Case(id=case_id, patient_name=patient_name, payer=payer)
    session.add(case)
    session.commit()
    return {"id": case.id, "status": case.status}

@app.post("/v1/cases/{case_id}/generate", status_code=202)
def generate(case_id: str, session: Session = Depends(get_session)):
    case = session.get(Case, case_id)
    if not case:
        raise HTTPException(404, "not found")
    if case.status in {"queued", "running"}:
        return {"accepted": True, "case_id": case_id, "status": case.status}
    job = Job(case_id=case_id)
    case.status = "queued"
    session.add(case)
    session.add(job)
    session.commit()
    return {"accepted": True, "case_id": case_id, "status": "queued"}

@app.get("/v1/cases/{case_id}")
def get_case(case_id: str, session: Session = Depends(get_session)):
    case = session.get(Case, case_id)
    if not case:
        raise HTTPException(404, "not found")
    return case

@strawberry.type
class CaseType:
    id: str
    patient_name: str
    payer: str
    status: str
    draft_text: str | None

@strawberry.type
class Query:
    @strawberry.field
    def case(self, id: str) -> CaseType | None:
        from db import engine
        with Session(engine) as session:
            c = session.get(Case, id)
            if not c:
                return None
            return CaseType(id=c.id, patient_name=c.patient_name, payer=c.payer, status=c.status, draft_text=c.draft_text)

graphql_app = GraphQLRouter(strawberry.Schema(query=Query))
app.include_router(graphql_app, prefix="/graphql")
