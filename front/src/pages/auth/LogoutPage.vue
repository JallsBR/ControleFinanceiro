<template>
    <div>Saindo...</div>
  </template>
  
  <script>
  export default {
    mounted() {
      this.$store.dispatch('logout');
      this.$router.push('/');
    }
  }
  </script>