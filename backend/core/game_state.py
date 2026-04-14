
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum

class GameMode(str, Enum):
    """
    An enum class with TWO_PLAYER and VS_AI describing againt who is playing
    """
    TWO_PLAYER = "two_player"
    VS_AI      = "vs_ai"

class GameResult(str, Enum):
    """
    How the game result is stores. 
    note that It does not diffenrenciate types of DRAW
    """
    ONGOING    = "ongoing"
    WHITE_WINS = "white_wins"
    BLACK_WINS = "black_wins"
    DRAW       = "draw"

@dataclass
class ClockState:
    """
    Stores per player the time in ms
    """
    white_ms: int  # in miliseconds
    black_ms: int

@dataclass
class GameState:
    """
    Manages all important game states but does not manage moves itself
    """
    # Board
    fen: str = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1" ##Initual state

    # Game setup
    mode: GameMode               = GameMode.TWO_PLAYER
    ai_engine: Optional[str]     = None   # "random" | "minimax" | "stockfish" | "ml" 
    ai_plays_as: Optional[str]   = None   # "black" | "white"

    # Progress
    result: GameResult           = GameResult.ONGOING
    move_history: list[str]      = field(default_factory=list)  # UCI strings e.g. "e2e4"

    # Clock (None = no clock)
    clock: Optional[ClockState]  = None