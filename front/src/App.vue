<template>
  <div id="app">
    <Toast />
    <router-view v-slot="{ Component }">
      <transition name="fade" mode="out-in">
        <component :is="Component" />
      </transition>
    </router-view>
  </div>
</template>

<script>
import Toast from 'primevue/toast'

export default {
  name: 'App',
  components: { Toast }
}
</script>
