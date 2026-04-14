# core/rule_engine.py

import chess
from typing import Optional

class RuleEngine:

    def get_board(self, fen: str) -> chess.Board:
        return chess.Board(fen)

    def is_legal_move(self, fen: str, uci: str) -> bool:
        board = self.get_board(fen)
        try:
            move = chess.Move.from_uci(uci)
            return move in board.legal_moves
        except ValueError:
            return False

    def apply_move(self, fen: str, uci: str) -> str:
        board = self.get_board(fen)
        move  = chess.Move.from_uci(uci)
        board.push(move)
        return board.fen()

    def get_legal_moves(self, fen: str) -> list[str]:
        board = self.get_board(fen)
        return [m.uci() for m in board.legal_moves]

    def get_legal_moves_from(self, fen: str, square: str) -> list[str]:
        board  = self.get_board(fen)
        sq     = chess.parse_square(square)  # e.g. "e2" -> 12
        return [
            m.uci() for m in board.legal_moves
            if m.from_square == sq
        ]

    def get_result(self, fen: str) -> Optional[str]:
        board = self.get_board(fen)
        if not board.is_game_over():
            return None
        outcome = board.outcome()
        if outcome.winner == chess.WHITE:
            return "white_wins"
        if outcome.winner == chess.BLACK:
            return "black_wins"
        return "draw"

    def is_check(self, fen: str) -> bool:
        return self.get_board(fen).is_check()

    def whose_turn(self, fen: str) -> str:
        return "white" if self.get_board(fen).turn == chess.WHITE else "black"