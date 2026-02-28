<template>
  
     <div> 
        <BarraNavegacao />
        <br />
        <div class="container mt-4">
            <router-view />
        </div>
    </div>
  </template>
  
  <script>
  import BarraNavegacao from '../components/BarraNavegacao.vue'
  export default {
    name: 'AuthLayout',
    components: {
      BarraNavegacao
    }
  }
  </script>