from fastapi import FastAPI, Request, Header, HTTPException
import os
import json
import requests
from loggers.logger import get_logger
from models import InferenceRequest, InferenceResponse, Message


logger = get_logger()
app = FastAPI(title="Chutes Proxy")

CHUTES_API_KEY = os.getenv("CHUTES_API_KEY")
if not CHUTES_API_KEY:
    raise RuntimeError("CHUTES_API_KEY environment variable is required!")

CHUTES_API_URL = "https://llm.chutes.ai/v1/chat/completions"
DEFAULT_MODEL = "unsloth/gemma-3-12b-it"
# DEFAULT_MODEL = "deepseek-ai/DeepSeek-V3.1"
TIMEOUT = 300


@app.post("/inference", response_model=InferenceResponse)
async def inference(
    request: InferenceRequest,
    x_job_id: str = Header(default="unknown"),
    x_project_id: str = Header(default="unknown"),
):
    logger.info(f"Request from [J:{x_job_id}|P:{x_project_id}]")

    if not request.model:
        request.model = DEFAULT_MODEL

    headers = {
        "Authorization": f"Bearer {CHUTES_API_KEY}"
    }
    payload_dict = request.model_dump()

    try:
        logger.info(f"Sending request to Chutes")
        resp = requests.post(CHUTES_API_URL, headers=headers, json=payload_dict, timeout=TIMEOUT)
        resp.raise_for_status()

        # TODO: Add handling for errors, pass on some errors

    except requests.RequestException as e:
        logger.error(f"Chutes API error: {e} {resp.text}")
        raise HTTPException(status_code=502, detail=f"Chutes API error: {e}")

    resp_json = resp.json()
    logger.info(f"Received response from Chutes: {json.dumps(resp_json, indent=2)}")

    if "choices" in resp_json and len(resp_json["choices"]):
        choice_message = resp_json["choices"][0]["message"]
        response = {
            "content": choice_message["content"],
            "role": choice_message["role"],
            "input_tokens": resp_json["usage"]["prompt_tokens"],
            "output_tokens": resp_json["usage"]["completion_tokens"],
        }
        return response

    else:
        logger.error(f"No choices received: {resp_json}")
