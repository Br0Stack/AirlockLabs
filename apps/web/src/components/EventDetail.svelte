<script lang="ts">
  import type { Event } from '../lib/types';
  export let event: Event | null = null;
</script>

<section>
  <h3>Event detail</h3>
  {#if event}
    <p><strong>{event.title}</strong></p>
    <p>{event.source_excerpt}</p>
    <p>Confidence: {event.confidence_score.toFixed(2)}</p>
  {:else}
    <p>Select an event to see source context.</p>
  {/if}
</section>
