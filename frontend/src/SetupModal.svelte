<!-- src/SetupModal.svelte -->

<script lang="ts">
  import { api, type NewGameRequest, type GameState } from "./api";

  export let onGameStarted: (state: GameState) => void;

  let mode: "two_player" | "vs_ai" = "two_player";
  let aiEngine    = "random";
  let aiPlaysAs   = "black";
  let useclock    = false;
  let clockMins   = 10;
  let error       = "";
  let loading     = false;

  const engines = [
    { value: "random",   label: "Random" },
    { value: "minimax",  label: "Minimax (classic)" },
    { value: "stockfish",label: "Stockfish" },
    { value: "ml",       label: "ML model" },
  ];

  async function start() {
    error   = "";
    loading = true;
    try {
      const req: NewGameRequest = {
        mode,
        ai_engine:   mode === "vs_ai" ? aiEngine   : undefined,
        ai_plays_as: mode === "vs_ai" ? aiPlaysAs  : undefined,
        clock_ms:    useclock ? clockMins * 60 * 1000 : undefined,
      };
      const state = await api.newGame(req);
      onGameStarted(state);
    } catch (e: any) {
      error = e.message;
    } finally {
      loading = false;
    }
  }
</script>

<div class="overlay">
  <div class="modal">
    <h2>New game</h2>

    <!-- Mode -->
    <fieldset>
      <legend>Mode</legend>
      <label>
        <input type="radio" bind:group={mode} value="two_player" />
        Two players
      </label>
      <label>
        <input type="radio" bind:group={mode} value="vs_ai" />
        vs AI
      </label>
    </fieldset>

    <!-- AI options -->
    {#if mode === "vs_ai"}
      <fieldset>
        <legend>Engine</legend>
        <select bind:value={aiEngine}>
          {#each engines as e}
            <option value={e.value}>{e.label}</option>
          {/each}
        </select>
      </fieldset>

      <fieldset>
        <legend>AI plays as</legend>
        <label>
          <input type="radio" bind:group={aiPlaysAs} value="black" />
          Black
        </label>
        <label>
          <input type="radio" bind:group={aiPlaysAs} value="white" />
          White
        </label>
      </fieldset>
    {/if}

    <!-- Clock -->
    <fieldset>
      <legend>Clock</legend>
      <label>
        <input type="checkbox" bind:checked={useclock} />
        Enable clock
      </label>
      {#if useclock}
        <label>
          Minutes per side
          <input type="number" bind:value={clockMins} min="1" max="180" />
        </label>
      {/if}
    </fieldset>

    {#if error}
      <p class="error">{error}</p>
    {/if}

    <button on:click={start} disabled={loading}>
      {loading ? "Starting…" : "Start game"}
    </button>
  </div>
</div>

<style>
  .overlay {
    position: absolute;
    inset: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(0, 0, 0, 0.45);
    z-index: 10;
  }

  .modal {
    background: white;
    border-radius: 12px;
    padding: 2rem;
    display: flex;
    flex-direction: column;
    gap: 1rem;
    min-width: 300px;
  }

  h2 { margin: 0; font-size: 1.2rem; }

  fieldset {
    border: 1px solid #ddd;
    border-radius: 8px;
    padding: 0.75rem 1rem;
    display: flex;
    flex-direction: column;
    gap: 0.4rem;
  }

  legend { font-size: 0.8rem; color: #666; padding: 0 4px; }

  select, input[type="number"] {
    margin-top: 4px;
    padding: 6px 8px;
    border: 1px solid #ddd;
    border-radius: 6px;
    font-size: 0.9rem;
    width: 100%;
  }

  button {
    padding: 0.6rem 1.2rem;
    border: none;
    border-radius: 8px;
    background: #333;
    color: white;
    font-size: 0.95rem;
    cursor: pointer;
  }

  button:disabled { opacity: 0.5; cursor: not-allowed; }

  .error { color: #c0392b; font-size: 0.85rem; margin: 0; }
</style>