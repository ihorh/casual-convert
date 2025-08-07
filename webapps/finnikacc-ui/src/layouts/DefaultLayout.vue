<script lang="ts">
import { defineComponent } from 'vue';

export default defineComponent({
    name: 'DefaultLayout',
});
</script>

<template>
    <div class="flex justify-center">
        <div class="min-h-screen flex flex-col w-xl">
            <header class="text-white flex flex-col items-start px-4">
                <slot name="header"></slot>
            </header>
            <main class="flex-grow px-4 py-4">
                <slot></slot>
            </main>
            <footer class="bg-gray-800 text-white px-4">
                <slot name="footer"></slot>
            </footer>
        </div>
    </div>
</template>
