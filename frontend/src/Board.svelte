<!-- src/Board.svelte -->

<script lang="ts">
  import { api, type GameState } from "./api";

  export let state:          GameState;
  export let onStateChange:  (s: GameState) => void;

  // ── FEN parsing ───────────────────────────────────────────────────

  type Piece = { color: "w" | "b"; type: string } | null;

  function fenToBoard(fen: string): Piece[][] {
    const rows = fen.split(" ")[0].split("/");
    return rows.map(row => {
      const squares: Piece[] = [];
      for (const ch of row) {
        if (isNaN(Number(ch))) {
          squares.push({
            color: ch === ch.toUpperCase() ? "w" : "b",
            type:  ch.toUpperCase(),
          });
        } else {
          for (let i = 0; i < Number(ch); i++) squares.push(null);
        }
      }
      return squares;
    });
  }

  const PIECES: Record<string, string> = {
    wK: "♔", wQ: "♕", wR: "♖", wB: "♗", wN: "♘", wP: "♙",
    bK: "♚", bQ: "♛", bR: "♜", bB: "♝", bN: "♞", bP: "♟",
  };

  function pieceGlyph(piece: Piece): string {
    if (!piece) return "";
    return PIECES[`${piece.color}${piece.type}`] ?? "";
  }

  // ── Square naming ─────────────────────────────────────────────────

  function squareName(row: number, col: number): string {
    return `${"abcdefgh"[col]}${8 - row}`;
  }

  // ── Click handling ────────────────────────────────────────────────

  let selected:    string | null = null;   // square name e.g. "e2"
  let highlights:  string[]      = [];     // legal target squares
  let error:       string        = "";

  async function handleSquareClick(row: number, col: number) {
    if (state.result !== "ongoing") return;

    const square = squareName(row, col);
    const board  = fenToBoard(state.fen);
    const piece  = board[row][col];

    // if a target square is clicked → make the move
    if (selected && highlights.includes(square)) {
      const uci = `${selected}${square}`;
      error      = "";
      try {
        const newState = await api.makeMove(uci);
        onStateChange(newState);
      } catch (e: any) {
        error = e.message;
      } finally {
        selected   = null;
        highlights = [];
      }
      return;
    }

    // if own piece is clicked → fetch legal moves
    const isOwnPiece =
      piece &&
      ((state.turn === "white" && piece.color === "w") ||
       (state.turn === "black" && piece.color === "b"));

    if (isOwnPiece) {
      selected = square;
      try {
        const res  = await api.getLegalMoves(square);
        highlights = res.moves.map(uci => uci.slice(2, 4));
      } catch {
        highlights = [];
      }
      return;
    }

    // clicked empty or opponent square with nothing selected → deselect
    selected   = null;
    highlights = [];
  }

  // ── Board colors ──────────────────────────────────────────────────

  function squareColor(row: number, col: number): string {
    return (row + col) % 2 === 0 ? "light" : "dark";
  }

  function squareClass(row: number, col: number): string {
    const name   = squareName(row, col);
    const base   = squareColor(row, col);
    const sel    = name === selected   ? "selected"    : "";
    const hl     = highlights.includes(name) ? "highlight" : "";
    return [base, sel, hl].filter(Boolean).join(" ");
  }

  $: board = fenToBoard(state.fen);
</script>

<div class="board-wrap">
  <div class="board">
    {#each board as row, ri}
      {#each row as piece, ci}
        <button
            class="square {squareClass(ri, ci)}"
            on:click={() => handleSquareClick(ri, ci)}
        >
      {/each}
    {/each}
  </div>

  <!-- Rank labels -->
  <div class="ranks">
    {#each [8,7,6,5,4,3,2,1] as r}
      <span>{r}</span>
    {/each}
  </div>

  <!-- File labels -->
  <div class="files">
    {#each ["a","b","c","d","e","f","g","h"] as f}
      <span>{f}</span>
    {/each}
  </div>

  {#if error}
    <p class="error">{error}</p>
  {/if}
</div>

<style>

button.square {
  border: none;
  padding: 0;
  font-family: inherit;
  background: inherit;
}

  .board-wrap {
    position: relative;
    display: inline-block;
  }

  .board {
    display: grid;
    grid-template-columns: repeat(8, 1fr);
    width: 480px;
    height: 480px;
    border: 2px solid #555;
  }

  .square {
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    font-size: 2.4rem;
    position: relative;
  }

  .light    { background: #f0d9b5; }
  .dark     { background: #b58863; }
  .selected { background: #7fc97f; }
  .highlight::after {
    content: "";
    position: absolute;
    width: 28%;
    height: 28%;
    border-radius: 50%;
    background: rgba(0, 0, 0, 0.25);
  }

  .piece       { line-height: 1; user-select: none; }
  .piece.white { filter: drop-shadow(0 1px 1px rgba(0,0,0,0.5)); }
  .piece.black { filter: drop-shadow(0 1px 1px rgba(0,0,0,0.3)); }

  .ranks {
    position: absolute;
    top: 0; left: -18px;
    height: 480px;
    display: flex;
    flex-direction: column;
    justify-content: space-around;
    font-size: 0.75rem;
    color: #555;
  }

  .files {
    position: absolute;
    bottom: -20px; left: 0;
    width: 480px;
    display: flex;
    justify-content: space-around;
    font-size: 0.75rem;
    color: #555;
  }

  .error {
    margin-top: 0.5rem;
    color: #c0392b;
    font-size: 0.85rem;
  }
</style>