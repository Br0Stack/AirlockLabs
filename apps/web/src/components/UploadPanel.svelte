<script lang="ts">
  export let disabled = false;
  export let onFilesSelected: (files: FileList) => Promise<void>;

  async function onDrop(event: DragEvent) {
    event.preventDefault();
    if (!event.dataTransfer?.files?.length) return;
    await onFilesSelected(event.dataTransfer.files);
  }

  async function onChange(event: Event) {
    const target = event.target as HTMLInputElement;
    if (!target.files?.length) return;
    await onFilesSelected(target.files);
    target.value = '';
  }
</script>

<div class="dropzone" on:drop={onDrop} on:dragover|preventDefault>
  <p>Drop files here or select uploads.</p>
  <input type="file" multiple on:change={onChange} disabled={disabled} />
</div>

<style>
  .dropzone { border: 2px dashed #94a3b8; border-radius: 10px; padding: 1rem; text-align: center; }
</style>
