import logging
import os
from dotenv import load_dotenv
from fastapi import FastAPI, APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from schemas import AgentResponse, AgentConfig, GameResponse, Direction
from agent import GameAgent
from store import Store
from service import Service


formatter = logging.Formatter(
    "%(asctime)s %(levelname)s %(name)s: %(message)s")
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger = logging.getLogger("model.api")
logger.addHandler(handler)
logger.setLevel(logging.INFO)

load_dotenv()
router = APIRouter()
store = Store()
service = Service(store)
agent_config = AgentConfig(
    model=os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
    temperature=float(os.getenv("MODEL_TEMPERATURE", 0.2)),
)
agent = GameAgent(agent_config, store)


@router.patch("/restart", response_model=GameResponse)
def restart(request: Request):
    logger.info("/api/restart called; client=%s", request.client)
    response = GameResponse(board=service.restart_game(), status=None)
    return JSONResponse(response.model_dump())


@router.patch("/move/{direction}", response_model=GameResponse)
def move(direction: Direction, request: Request):
    logger.info("/api/move/%s called; client=%s",
                direction.name, request.client)
    board, result = service.make_move(direction)
    response = GameResponse(board=board, status=result)
    return JSONResponse(response.model_dump())


@router.post("/suggest/{num_suggestions}", response_model=AgentResponse)
def suggest(num_suggestions: int, request: Request):
    logger.info("/api/suggest called; client=%s", request.client)
    try:
        output: AgentResponse = agent.invoke(num_suggestions)
    except Exception as e:
        logger.exception("Agent invocation error: %s", e)
        raise HTTPException(status_code=500, detail="Agent invocation failed")
    return JSONResponse(output.model_dump())


app = FastAPI(title="2048 API")
app.include_router(router, prefix="/api")

origins = os.getenv("ALLOWED_ORIGINS", "").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
