<template>
  <footer class="footer-app">
    <span class="footer-text">Todos os direitos reservados - 2026 - O5o software house -
    Apoie esse projeto</span>
    <a href="mailto:oswaldojales@gmail.com" class="footer-email">oswaldojales@gmail.com</a>
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
  background-color: #212529;
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
  color: #adb5bd;
  font-size: 0.95rem;
}

.footer-email {
  color: #20c997;
  text-decoration: none;
  font-size: 0.95rem;
  transition: color 0.2s ease;
}

.footer-email:hover {
  color: #38d9a9;
}
</style>
