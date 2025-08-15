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
    </DefaultLayout>
</template>

<script lang="ts" setup>
import DefaultLayout from '@/layouts/DefaultLayout.vue'
import CcBasket from '@/components/CcBasket.vue'
import Disclaimer from '@/layouts/Disclaimer.vue'
import Footer from '@/layouts/Footer.vue'
</script>
