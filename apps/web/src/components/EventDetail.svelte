<script lang="ts">
  import type { Event } from '../lib/types';
  export let event: Event | null = null;
  export let onClose: () => void;
</script>

{#if event}
  <div class="overlay" on:click={onClose}></div>
  <aside class="panel">
    <header>
      <h3>Event detail</h3>
      <button on:click={onClose}>Close</button>
    </header>
    <p><strong>Title:</strong> {event.title}</p>
    <p><strong>Date:</strong> {event.event_date ? new Date(event.event_date).toLocaleDateString() : 'Undated'}</p>
    <p><strong>Description:</strong> {event.description}</p>
    <p><strong>Source:</strong> {event.source}</p>
    <p><strong>Excerpt:</strong> {event.source_excerpt}</p>
  </aside>
{/if}

<style>
  .overlay {
    position: fixed;
    inset: 0;
    background: rgba(15, 23, 42, 0.35);
    z-index: 40;
  }
  .panel {
    position: fixed;
    right: 0;
    top: 0;
    bottom: 0;
    width: min(420px, 90vw);
    background: white;
    padding: 1rem;
    box-shadow: -8px 0 24px rgba(0, 0, 0, 0.2);
    z-index: 50;
    overflow: auto;
  }
  header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
  }
</style>
