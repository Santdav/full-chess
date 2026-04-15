import chess
import random
from engines.base import AIEngine

class RandomEngine(AIEngine):

    def get_move(self, fen: str) -> str:
        board = chess.Board(fen)
        move  = random.choice(list(board.legal_moves))
        return move.uci()