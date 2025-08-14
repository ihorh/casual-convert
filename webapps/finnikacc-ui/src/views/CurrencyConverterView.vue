<template>
    <DefaultLayout>
        <template #header>
            <h1>Finnika CC</h1>
            <h2>Your convenient currency converter</h2>
        </template>
        <template #footer>
            <Footer />
        </template>

        <hr />
        <div class="h-4"></div>

        <cc-basket />

        <hr />
        <div class="h-4"></div>

        <disclaimer />

        <br />
        <hr />
        <br />

        <div class="grid grid-cols-2 gap-4 w-max">
            <div>Env Key</div>
            <div>Value</div>
            <div>version</div>
            <div>{{ appVersion }}</div>
            <div>API version</div>
            <div>{{ apiServerVersion }}</div>
            <template v-for="(value, key) in env">
                <div>{{ key }}</div>
                <div>{{ value }}</div>
            </template>
        </div>
    </DefaultLayout>
</template>

<script lang="ts" setup>
import DefaultLayout from '@/layouts/DefaultLayout.vue'
import CcBasket from '@/components/CcBasket.vue'
import Disclaimer from '@/layouts/Disclaimer.vue'
import Footer from '@/layouts/Footer.vue'
import { useAPIServerStatus } from '@/stores/queries'
import { computed } from 'vue'

const ENV_MODE = import.meta.env.MODE
const BASE_URL = import.meta.env.BASE_URL
const PROD = import.meta.env.PROD
const DEV = import.meta.env.DEV
const SST = import.meta.env.SSR

const env = import.meta.env
const keys = Object.keys(import.meta.env)

const appVersion = __APP_VERSION__

const { isError, data: apiServerStatus, error } = useAPIServerStatus()

const apiServerVersion = computed(() =>
    apiServerStatus.value && apiServerStatus.value.version
        ? apiServerStatus.value.version
        : 'fetching...',
)
</script>
