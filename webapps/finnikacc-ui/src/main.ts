import './assets/style.css'

// Vuetify
import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import { VueQueryPlugin } from '@tanstack/vue-query'
import { configure } from 'vue-gtag'

import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'

import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'

const vuetify = createVuetify({
    components,
    directives,
})

const app = createApp(App)

app.use(createPinia())
app.use(VueQueryPlugin)
app.use(vuetify)

if (import.meta.env.PROD) {
    configure({
        tagId: 'G-7NNCH1RRNJ',
    })
}

app.mount('#app')
