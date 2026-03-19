<script lang="ts">
  import ChatPanel from './components/ChatPanel.svelte';
  import EventDetail from './components/EventDetail.svelte';
  import TimelineView from './components/TimelineView.svelte';
  import UploadPanel from './components/UploadPanel.svelte';
  import WorkspaceList from './components/WorkspaceList.svelte';
  import { api } from './lib/api';
  import type { ChatMessage, Document, Event, Workspace } from './lib/types';

  let workspaces: Workspace[] = [];
  let selectedWorkspace: Workspace | null = null;
  let documents: Document[] = [];
  let events: Event[] = [];
  let selectedEvent: Event | null = null;
  let messages: ChatMessage[] = [];
  let loading = false;
  let error = '';

  async function loadWorkspaces() {
    workspaces = await api.listWorkspaces();
    if (!selectedWorkspace && workspaces.length) {
      await selectWorkspace(workspaces[0]);
    }
  }

  async function selectWorkspace(workspace: Workspace) {
    selectedWorkspace = workspace;
    selectedEvent = null;
    messages = [];
    await Promise.all([loadDocuments(), loadEvents()]);
  }

  async function createWorkspace(name: string, description: string) {
    const workspace = await api.createWorkspace({ name, description: description || undefined });
    await loadWorkspaces();
    await selectWorkspace(workspace);
  }

  async function loadDocuments() {
    if (!selectedWorkspace) return;
    documents = await api.listDocuments(selectedWorkspace.id);
  }

  async function loadEvents() {
    if (!selectedWorkspace) return;
    events = await api.listEvents(selectedWorkspace.id);
  }

  async function uploadFiles(files: FileList) {
    if (!selectedWorkspace) return;
    loading = true;
    error = '';
    try {
      for (const file of Array.from(files)) {
        await api.uploadDocument(selectedWorkspace.id, file);
      }
      await loadDocuments();
    } catch (err) {
      error = (err as Error).message;
    } finally {
      loading = false;
    }
  }

  async function runExtraction() {
    if (!selectedWorkspace) return;
    loading = true;
    error = '';
    try {
      await api.extractEvents(selectedWorkspace.id);
      await loadEvents();
    } catch (err) {
      error = (err as Error).message;
    } finally {
      loading = false;
    }
  }

  async function sendMessage(content: string) {
    if (!selectedWorkspace) return;
    const response = await api.chat(selectedWorkspace.id, content);
    messages = [...messages, response.user_message, response.assistant_message];
  }

  loadWorkspaces();
</script>

<main>
  <header>
    <h1>Threadline</h1>
    <p>Turn messy evidence into a clear timeline.</p>
  </header>

  {#if error}
    <p class="error">{error}</p>
  {/if}

  <div class="layout">
    <aside class="left">
      <WorkspaceList
        {workspaces}
        selectedWorkspaceId={selectedWorkspace?.id ?? null}
        onSelect={selectWorkspace}
        onCreate={createWorkspace}
      />

      {#if selectedWorkspace}
        <h3>Documents</h3>
        <UploadPanel onFilesSelected={uploadFiles} disabled={loading} />
        <button on:click={runExtraction} disabled={loading}>Extract events</button>
        <ul>
          {#each documents as document}
            <li>{document.filename}</li>
          {/each}
        </ul>
      {/if}
    </aside>

    <section class="center">
      <TimelineView {events} {selectedEvent} onSelect={(event) => (selectedEvent = event)} />
    </section>

    <aside class="right">
      <ChatPanel {messages} onSend={sendMessage} disabled={!selectedWorkspace || loading} />
    </aside>
  </div>

  <EventDetail event={selectedEvent} onClose={() => (selectedEvent = null)} />
</main>

<style>
  :global(body) {
    margin: 0;
    font-family: Inter, system-ui, sans-serif;
    background: #f8fafc;
    color: #0f172a;
  }
  main { padding: 1rem; }
  header h1 { margin: 0; }
  .layout {
    display: grid;
    grid-template-columns: 320px 1fr 360px;
    gap: 1rem;
    margin-top: 1rem;
  }
  .left, .center, .right {
    background: white;
    border-radius: 12px;
    padding: 1rem;
    min-height: 70vh;
  }
  .error { color: #b91c1c; }
  ul { list-style: none; padding: 0; }
</style>
