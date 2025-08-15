<template>
    <div class="flex gap-x-2 text-sm">
        <div>&copy; Ihor H. 2025</div>
        <div>|</div>
        <div>
            <a
                href="https://github.com/ihorh/casual-convert"
                target="_blank"
                class="hover:underline hover:text-atomic-tangerine"
            >
                Project GitHub Page
            </a>
        </div>
        <div>|</div>
        <div>App Version: {{ appVersion }}</div>
        <div>|</div>
        <div>API Version: {{ apiServerVersion }}</div>
    </div>
</template>

<script lang="ts" setup>
import { useAPIServerStatus } from '@/stores/queries'
import { computed } from 'vue'

const appVersion = __APP_VERSION__

const { isError, data: apiServerStatus, error } = useAPIServerStatus()

const apiServerVersion = computed(() =>
    apiServerStatus.value && apiServerStatus.value.version
        ? apiServerStatus.value.version
        : 'fetching...',
)
</script>
