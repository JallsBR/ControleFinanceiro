<template>
  <Dialog
    v-model:visible="modelValue"
    modal
    :closable="false"
    :dismissableMask="false"
    :closeOnEscape="false"
    :style="{ width }"
  >
    <!-- HEADER -->
    <template #header>
      <div class="app-dialog__header">
        <div class="app-dialog__icon">
          <i :class="icone"></i>
        </div>

        <div class="app-dialog__titles">
          <h2 class="app-dialog__title">
            {{ titulo }}
          </h2>

          <p
            v-if="subtitulo"
            class="app-dialog__subtitle"
          >
            {{ subtitulo }}
          </p>
        </div>
      </div>
    </template>

    <!-- BODY -->
    <div class="app-dialog__body">
      <slot />
    </div>

    <!-- FOOTER -->
    <template #footer>
      <div class="app-dialog__footer">

        <!-- AÇÕES CUSTOM -->
        <div class="app-dialog__actions">
          <slot name="actions" />
        </div>
      </div>
    </template>
  </Dialog>
</template>
  
  <script setup>
  import { computed } from "vue";
  import Dialog from 'primevue/dialog';

  const props = defineProps({
    modelValue: Boolean,
    titulo: String,
    subtitulo: String,
    icone: {
      type: String,
      default: "pi pi-info-circle"
    },
    width: {
      type: String,
      default: "35rem"
    }
  });
  
  const emit = defineEmits(["update:modelValue"]);
  
  const modelValue = computed({
    get: () => props.modelValue,
    set: (value) => emit("update:modelValue", value)
  });
  </script>
  <style scoped>
  .app-dialog__header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
  }

  .app-dialog__icon {
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--bg-primario);
    border-radius: 8px;
    padding: 0.5rem;
    min-width: 2.5rem;
    min-height: 2.5rem;
  }

  .app-dialog__icon i {
    color: var(--texto-secundario);
    font-size: 1.25rem;
  }

  .app-dialog__titles {
    display: flex;
    flex-direction: column;
  }

  .app-dialog__title {
    margin: 0;
    font-size: 2.3rem;
    font-weight: 600;
  }

  .app-dialog__subtitle {
    margin: 0 0 0;
    font-size: 0.875rem;
    color: var(--texto-secundario);
  }

  /* Container geral do Dialog */
  :deep(.p-dialog) {
    border-radius: 12px;
    overflow: hidden;
  }

  /* HEADER */
  :deep(.p-dialog-header) {
    background: var(--bg-secundario);
    border-bottom: 1px solid color-mix(in srgb, var(--texto-secundario) 25%, transparent);
    padding: 1.25rem 1.5rem;
  }

  /* BODY */
  :deep(.p-dialog-content) {
    padding: 1.5rem;
    background: var(--bg-secundario);
  }

  /* FOOTER */
  .app-dialog__footer {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: 0.75rem;
    width: 100%;
  }

  .app-dialog__actions {
    display: flex;
    justify-content: flex-end;
    gap: 0.5rem;
    width: 100%;
  }

  :deep(.p-dialog-footer) {
    border-top: 1px solid color-mix(in srgb, var(--texto-secundario) 25%, transparent);
    padding: 1rem 1.5rem;
    background: var(--bg-primario);
  }

  /* Overlay levemente escuro */
  :deep(.p-dialog-mask) {
    backdrop-filter: blur(2px);
    background-color: rgba(0, 0, 0, 0.4);
  }

  </style>


  <!-- Exemplos de uso
     <DialogFinancas v-model:visible="visible" titulo="Edit Profile" subtitulo="Update your information." icone="pi pi-user" width="25rem">
        <div class="flex items-center gap-4 mb-4">
            <label for="username" class="font-semibold w-24">Username</label>
            <InputText id="username" class="flex-auto" autocomplete="off" />
        </div>
        <div class="flex items-center gap-4 mb-8">
            <label for="email" class="font-semibold w-24">Email</label>
            <InputText id="email" class="flex-auto" autocomplete="off" />
        </div>
        <div class="flex justify-end gap-2">
            <Button type="button" label="Cancel" severity="secondary" @click="visible = false"></Button>
            <Button type="button" label="Save" @click="visible = false"></Button>
        </div>
    </DialogFinancas>
  
    <Button label="Show" @click="visible = true" />
  -->
  