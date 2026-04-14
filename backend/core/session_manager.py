# core/session_manager.py

from core.game_state import GameState, GameMode, GameResult
from core.rule_engine import RuleEngine
from engines.base import AIEngine
from engines.random_engine import RandomEngine

from typing import Optional

rule_engine = RuleEngine()

ENGINE_MAP: dict[str, type[AIEngine]] = {
    "random": RandomEngine,
}

class SessionManager:

    def __init__(self):
        self.state:  Optional[GameState] = None
        self.engine: Optional[AIEngine]  = None

    def new_game(
        self,
        mode:        GameMode,
        ai_engine:   Optional[str] = None,
        ai_plays_as: Optional[str] = "black",
        clock_ms:    Optional[int] = None,
    ) -> GameState:
        from core.game_state import ClockState

        clock = ClockState(white_ms=clock_ms, black_ms=clock_ms) if clock_ms else None

        self.state = GameState(
            mode        = mode,
            ai_engine   = ai_engine,
            ai_plays_as = ai_plays_as,
            clock       = clock,
        )

        self.engine = ENGINE_MAP[ai_engine]() if ai_engine else None
        return self.state

    def get_state(self) -> GameState:
        if not self.state:
            raise ValueError("No active game.")
        return self.state

    def apply_move(self, uci: str) -> GameState:
        state = self.get_state()

        if state.result != GameResult.ONGOING:
            raise ValueError("Game is already over.")

        if not rule_engine.is_legal_move(state.fen, uci):
            raise ValueError(f"Illegal move: {uci}")

        state.fen = rule_engine.apply_move(state.fen, uci)
        state.move_history.append(uci)

        result = rule_engine.get_result(state.fen)
        if result:
            state.result = GameResult(result)
            return state

        if self._ai_should_move():
            ai_uci        = self.engine.get_move(state.fen)
            state.fen     = rule_engine.apply_move(state.fen, ai_uci)
            state.move_history.append(ai_uci)

            result = rule_engine.get_result(state.fen)
            if result:
                state.result = GameResult(result)

        return state

    def load_state(self, state: GameState) -> GameState:
        ai_key      = state.ai_engine
        self.engine = ENGINE_MAP[ai_key]() if ai_key and ai_key in ENGINE_MAP else None
        self.state  = state
        return self.state

    def _ai_should_move(self) -> bool:
        state = self.state
        if state.mode != GameMode.VS_AI or not self.engine:
            return False
        current_turn = rule_engine.whose_turn(state.fen)
        return current_turn == state.ai_plays_as


session = SessionManager()