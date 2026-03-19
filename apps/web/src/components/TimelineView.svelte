<script lang="ts">
  import type { Event } from '../lib/types';

  export let events: Event[] = [];
  export let selectedEvent: Event | null = null;
  export let onSelect: (event: Event) => void;
</script>

<section>
  <h3>Timeline</h3>
  <ul>
    {#each events as event}
      <li>
        <button class:selected={selectedEvent?.id === event.id} on:click={() => onSelect(event)}>
          <strong>{event.title}</strong>
          <div>{event.event_date ? new Date(event.event_date).toLocaleDateString() : 'Undated'}</div>
          <small>{event.description}</small>
        </button>
      </li>
    {/each}
  </ul>
</section>

<style>
  ul { list-style: none; margin: 0; padding: 0; display: grid; gap: 0.5rem; }
  li button { width: 100%; text-align: left; border: 1px solid #ddd; border-radius: 8px; padding: 0.75rem; }
  .selected { border-color: #2563eb; background: #eff6ff; }
  small { color: #666; }
</style>
