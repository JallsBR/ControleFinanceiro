import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import PrimeVue from 'primevue/config';
import Aura from '@primeuix/themes/aura';
import 'bootstrap/dist/css/bootstrap.min.css'
import './assets/theme-global.css'
import 'primeicons/primeicons.css';

const app = createApp(App)
app.use(PrimeVue, {
    // Default theme configuration
    theme: {
        preset: Aura,
        options: {
            prefix: 'p',
            darkModeSelector: 'system',          
        }
    }
 });
app.use(router)
app.use(store)

app.mount('#app')