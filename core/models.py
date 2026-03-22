from pydantic import BaseModel


class PatientRequest(BaseModel):
    patient: str
    correction: str = ""


class ValidationRequest(BaseModel):
    journal: str
    correction: str = ""


class AnalysisRequest(BaseModel):
    journal: str
    patient_context: str
    correction: str = ""


class ChatRequest(BaseModel):
    analysis_context: str
    history: list
    question: str
