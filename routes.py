"""
Tous les endpoints API — couche mince qui délègue aux steps/.
"""

import json
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, StreamingResponse

from core.client import client
from core.models import PatientRequest, ValidationRequest, AnalysisRequest, ChatRequest  # ChatRequest → /chat-stream uniquement
from core.rate_limit import check_rate_limit
from steps.patient import build_patient_prompt, extract_patient_target
from steps.validation import build_validation_prompt, extract_scenario, extract_validation_conclusion
from steps.analysis import build_analysis_prompt, extract_conclusions, extract_table
from steps.chat import build_chat_messages

router = APIRouter()


@router.get("/")
async def root():
    with open("static/index.html", encoding="utf-8") as f:
        return HTMLResponse(f.read())


@router.post("/analyze-patient")
async def analyze_patient(request: PatientRequest, http_request: Request):
    check_rate_limit(http_request.client.host)
    prompt = build_patient_prompt(request.patient, request.correction)
    try:
        response = client.responses.create(
            model="gpt-4.1-mini",
            tools=[{"type": "web_search"}],
            input=prompt,
            temperature=0.1,
        )
        full_text = response.output_text
        target = extract_patient_target(full_text)
        return {
            "analysis": full_text,
            "weight_kg": target["poids_retenu_kg"],
            "target_g_per_kg": target["target_g_per_kg"],
            "total_target_g": target["total_target_g"],
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/validate-journal")
async def validate_journal(request: ValidationRequest, http_request: Request):
    check_rate_limit(http_request.client.host)
    prompt = build_validation_prompt(request.journal, request.correction)
    try:
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=prompt,
            temperature=0.1,
        )
        full_text = response.output_text
        scenario = extract_scenario(full_text)
        conclusion = extract_validation_conclusion(full_text)
        return {"scenario": scenario or full_text, "conclusion": conclusion or scenario or full_text}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze")
async def analyze(request: AnalysisRequest, http_request: Request):
    check_rate_limit(http_request.client.host)
    prompt = build_analysis_prompt(request.journal, request.patient_context, request.correction)
    try:
        response = client.responses.create(
            model="gpt-4.1-mini",
            tools=[{"type": "web_search"}],
            input=prompt,
            temperature=0.1,
        )
        full_text = response.output_text
        conclusions = extract_conclusions(full_text)
        table = extract_table(full_text)
        return {
            "conclusion_finale": conclusions["finale"],
            "table_markdown": table,
            "full_response": full_text,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.post("/chat-stream")
async def chat_stream(request: ChatRequest, http_request: Request):
    check_rate_limit(http_request.client.host)
    messages = build_chat_messages(request.analysis_context, request.history, request.question)

    def generate():
        try:
            stream = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=messages,
                temperature=0.3,
                stream=True,
            )
            for chunk in stream:
                content = chunk.choices[0].delta.content
                if content:
                    yield f"data: {json.dumps({'content': content})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
