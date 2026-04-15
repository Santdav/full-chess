import json
import os
from core.game_state import GameState, GameMode, GameResult, ClockState

SAVES_DIR = "saves"

def save_game(state: GameState, filename: str) -> None:
    os.makedirs(SAVES_DIR, exist_ok=True)
    data = {
        "fen":          state.fen,
        "mode":         state.mode,
        "ai_engine":    state.ai_engine,
        "ai_plays_as":  state.ai_plays_as,
        "result":       state.result,
        "move_history": state.move_history,
        "clock": {
            "white_ms": state.clock.white_ms,
            "black_ms": state.clock.black_ms,
        } if state.clock else None,
    }
    with open(f"{SAVES_DIR}/{filename}.json", "w") as f:
        json.dump(data, f, indent=2)

def load_game(filename: str) -> GameState:
    path = f"{SAVES_DIR}/{filename}.json"
    if not os.path.exists(path):
        raise FileNotFoundError(filename)
    with open(path) as f:
        data = json.load(f)
    clock = ClockState(**data["clock"]) if data["clock"] else None
    return GameState(
        fen          = data["fen"],
        mode         = GameMode(data["mode"]),
        ai_engine    = data["ai_engine"],
        ai_plays_as  = data["ai_plays_as"],
        result       = GameResult(data["result"]),
        move_history = data["move_history"],
        clock        = clock,
    )