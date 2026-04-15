# engines/base.py

from abc import ABC, abstractmethod

class AIEngine(ABC):

    @abstractmethod
    def get_move(self, fen: str) -> str:
        """
        Given a FEN string, return a UCI move string e.g. "e2e4".
        """
        ...