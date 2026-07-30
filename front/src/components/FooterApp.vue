<template>
  <footer class="footer-app">
    <span class="footer-text">Todos os direitos reservados - 2026 - O5o software house</span>
  </footer>
</template>

<script setup>
</script>

<style scoped>
.footer-app {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  width: 100%;
  background-color: var(--bg-secundario);
  border: none;
  padding: 0.75rem 20px;
  padding-bottom: max(0.75rem, env(safe-area-inset-bottom, 0px));
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.5rem;
  flex-wrap: wrap;
  z-index: 100;
  box-sizing: border-box;
  min-height: 2.75rem;
}

.footer-text {
  color: var(--texto-secundario);
  font-size: 0.95rem;
  line-height: 1.35;
  text-align: right;
  max-width: 100%;
  overflow-wrap: anywhere;
  word-break: break-word;
}

@media (max-width: 900px) {
  .footer-app {
    justify-content: center;
    /* reserva espaço à direita para o FAB do menu (~3.25rem + margem) */
    padding-left: 1rem;
    padding-right: 4.5rem;
    min-height: 3rem;
  }

  .footer-text {
    text-align: center;
    font-size: 0.75rem;
    width: 100%;
  }
}
</style>
