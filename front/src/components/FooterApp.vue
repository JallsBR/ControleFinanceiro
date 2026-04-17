<template>
  <footer class="footer-app">
    <span class="footer-text">Todos os direitos reservados - 2026 - O5o software house </span>
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
  padding: 1rem 20px;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.5rem;
  flex-wrap: wrap;
  z-index: 100;
}

.footer-text {
  color: var(--texto-secundario);
  font-size: 0.95rem;
}

.footer-email {
  color: var(--sucesso);
  text-decoration: none;
  font-size: 0.95rem;
  transition: color 0.2s ease;
}

.footer-email:hover {
  color: var(--sucesso);
  filter: brightness(1.15);
}
</style>
