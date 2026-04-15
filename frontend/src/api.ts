// src/api.ts

const BASE = "http://localhost:8000";

// ── Types ──────────────────────────────────────────────────────────

export type GameMode   = "two_player" | "vs_ai";
export type GameResult = "ongoing" | "white_wins" | "black_wins" | "draw";

export interface ClockState {
  white_ms: number;
  black_ms: number;
}

export interface GameState {
  fen:          string;
  turn:         "white" | "black";
  mode:         GameMode;
  ai_engine:    string | null;
  ai_plays_as:  string | null;
  result:       GameResult;
  move_history: string[];
  clock:        ClockState | null;
}

// ── Requests ───────────────────────────────────────────────────────

export interface NewGameRequest {
  mode:         GameMode;
  ai_engine?:   string;
  ai_plays_as?: string;
  clock_ms?:    number;
}

// ── API calls ──────────────────────────────────────────────────────

async function request<T>(
  method:  string,
  path:    string,
  body?:   unknown,
): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    method,
    headers: { "Content-Type": "application/json" },
    body:    body ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail ?? "Unknown error");
  }
  return res.json();
}

export const api = {

  newGame: (req: NewGameRequest): Promise<GameState> =>
    request("POST", "/game/new", req),

  getState: (): Promise<GameState> =>
    request("GET", "/game/state"),

  makeMove: (uci: string): Promise<GameState> =>
    request("POST", "/game/move", { uci }),

  getLegalMoves: (square: string): Promise<{ square: string; moves: string[] }> =>
    request("GET", `/game/legal-moves/${square}`),

  undo: (): Promise<GameState> =>
    request("POST", "/game/undo"),

  save: (filename: string): Promise<{ saved: string }> =>
    request("POST", "/game/save", { filename }),

  load: (filename: string): Promise<GameState> =>
    request("POST", "/game/load", { filename }),

  listSaves: (): Promise<{ saves: string[] }> =>
    request("GET", "/game/saves"),

};