# routers/game.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from core.session_manager import session
from core.game_state import GameMode, GameResult
from save_load import save_game, load_game

router = APIRouter()


# ── Request schemas ────────────────────────────────────────────────

class NewGameRequest(BaseModel):
    mode:        GameMode
    ai_engine:   Optional[str] = None
    ai_plays_as: Optional[str] = "black"
    clock_ms:    Optional[int] = None

class MoveRequest(BaseModel):
    uci: str  # e.g. "e2e4"

class SaveRequest(BaseModel):
    filename: str  # e.g. "my_game"

class LoadRequest(BaseModel):
    filename: str


# ── Endpoints ──────────────────────────────────────────────────────

@router.post("/game/new")
def new_game(req: NewGameRequest):
    if req.mode == GameMode.VS_AI and not req.ai_engine:
        raise HTTPException(status_code=400, detail="ai_engine required when mode is vs_ai.")
    state = session.new_game(
        mode        = req.mode,
        ai_engine   = req.ai_engine,
        ai_plays_as = req.ai_plays_as,
        clock_ms    = req.clock_ms,
    )
    return _serialize(state)


@router.get("/game/state")
def get_state():
    try:
        return _serialize(session.get_state())
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/game/move")
def make_move(req: MoveRequest):
    try:
        state = session.apply_move(req.uci)
        return _serialize(state)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/game/legal-moves/{square}")
def legal_moves_from(square: str):
    from core.rule_engine import RuleEngine
    try:
        fen   = session.get_state().fen
        moves = RuleEngine().get_legal_moves_from(fen, square)
        return {"square": square, "moves": moves}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/game/undo")
def undo_move():
    try:
        state = session.get_state()
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    history = state.move_history
    if not history:
        raise HTTPException(status_code=400, detail="No moves to undo.")

    import chess
    board = chess.Board()
    # pop last move (or last two if vs AI)
    moves_to_replay = history[:-1]
    if state.mode == GameMode.VS_AI and len(history) >= 2:
        moves_to_replay = history[:-2]

    for uci in moves_to_replay:
        board.push(chess.Move.from_uci(uci))

    state.fen          = board.fen()
    state.move_history = moves_to_replay
    state.result       = GameResult.ONGOING
    return _serialize(state)


@router.post("/game/save")
def save(req: SaveRequest):
    try:
        state = session.get_state()
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    save_game(state, req.filename)
    return {"saved": req.filename}


@router.post("/game/load")
def load(req: LoadRequest):
    try:
        state = load_game(req.filename)
        session.load_state(state)
        return _serialize(state)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Save '{req.filename}' not found.")


@router.get("/game/saves")
def list_saves():
    import os
    saves_dir = "saves"
    files = [
        f.replace(".json", "")
        for f in os.listdir(saves_dir)
        if f.endswith(".json")
    ]
    return {"saves": files}


# ── Serializer ─────────────────────────────────────────────────────

def _serialize(state):
    return {
        "fen":          state.fen,
        "turn":         "white" if "w" in state.fen.split()[1] else "black",
        "mode":         state.mode,
        "ai_engine":    state.ai_engine,
        "ai_plays_as":  state.ai_plays_as,
        "result":       state.result,
        "move_history": state.move_history,
        "clock":        {
            "white_ms": state.clock.white_ms,
            "black_ms": state.clock.black_ms,
        } if state.clock else None,
    }