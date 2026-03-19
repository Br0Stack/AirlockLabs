<script lang="ts">
  import type { Workspace } from '../lib/types';

  export let workspaces: Workspace[] = [];
  export let selectedWorkspaceId: number | null = null;
  export let onSelect: (workspace: Workspace) => void;
  export let onCreate: (name: string, description: string) => Promise<void>;

  let name = '';
  let description = '';

  async function submit() {
    if (!name.trim()) return;
    await onCreate(name.trim(), description.trim());
    name = '';
    description = '';
  }
</script>

<section>
  <h2>Workspaces</h2>
  <div class="create">
    <input bind:value={name} placeholder="Workspace name" />
    <textarea bind:value={description} placeholder="Short description"></textarea>
    <button on:click={submit}>Create workspace</button>
  </div>
  <ul>
    {#each workspaces as workspace}
      <li>
        <button class:selected={workspace.id === selectedWorkspaceId} on:click={() => onSelect(workspace)}>
          <strong>{workspace.name}</strong>
          <small>{workspace.description ?? 'No description'}</small>
        </button>
      </li>
    {/each}
  </ul>
</section>

<style>
  .create { display: grid; gap: 0.5rem; margin-bottom: 1rem; }
  ul { list-style: none; padding: 0; margin: 0; display: grid; gap: 0.5rem; }
  li button { width: 100%; text-align: left; border: 1px solid #ccc; padding: 0.75rem; border-radius: 8px; }
  .selected { border-color: #2563eb; background: #eff6ff; }
  small { display: block; color: #666; margin-top: 0.25rem; }
</style>
