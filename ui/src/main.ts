import { createApp } from 'vue'

// Vuetify
import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import '@mdi/font/css/materialdesignicons.css';
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import axios from "axios";
import router from "./router";
import store from "./store";
import { AuthInterceptor } from "./api/auth.interceptor"

import App from './App.vue'

const vuetify = createVuetify({
    components,
    directives,
    icons: {
        defaultSet: 'mdi',
    },
})

axios.defaults.baseURL = import.meta.env.VITE_API_BASE_URL;
axios.interceptors.request.use(AuthInterceptor.request);
const app = createApp(App);

app.use(vuetify);
app.use(store);
app.use(router);

app.mount("#app");
