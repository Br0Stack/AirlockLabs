<script lang="ts">
  import type { ChatMessage } from '../lib/types';

  export let messages: ChatMessage[] = [];
  export let disabled = false;
  export let onSend: (content: string) => Promise<void>;

  let content = '';

  async function submit() {
    if (!content.trim()) return;
    await onSend(content.trim());
    content = '';
  }
</script>

<section>
  <h3>Chat</h3>
  <div class="messages">
    {#each messages as message}
      <div class:assistant={message.role === 'assistant'} class:user={message.role === 'user'}>
        <strong>{message.role}</strong>
        <p>{message.content}</p>
      </div>
    {/each}
  </div>
  <div class="composer">
    <input bind:value={content} placeholder="Ask about this workspace..." disabled={disabled} />
    <button on:click={submit} disabled={disabled}>Send</button>
  </div>
</section>

<style>
  .messages { max-height: 340px; overflow: auto; display: grid; gap: 0.5rem; margin-bottom: 0.75rem; }
  .assistant, .user { border-radius: 8px; padding: 0.5rem; }
  .assistant { background: #f1f5f9; }
  .user { background: #e0f2fe; }
  .composer { display: grid; grid-template-columns: 1fr auto; gap: 0.5rem; }
</style>
