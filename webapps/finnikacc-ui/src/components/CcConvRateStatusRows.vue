<template>
    <template v-if="status === View.ConversionRatesStatus.VERY_OUTDATED">
        <p></p>
        <div class="text-atomic-tangerine-400 col-span-2 text-sm">
            Some conversion rates are signifficantly out of date.
        </div>
        <p></p>
    </template>
    <template v-else-if="status === View.ConversionRatesStatus.JUST_OUTDATED">
        <p></p>
        <div class="text-atomic-tangerine-700 col-span-2 text-sm">
            Some conversion rates are older than one day
        </div>
        <p></p>
    </template>
    <template v-else-if="status === View.ConversionRatesStatus.SLIGHTLY_OUTDATED">
        <p></p>
        <div class="text-tiffany-blue-400 col-span-2 text-sm">
            Some conversion rates may be slightly outdated.
        </div>
        <p></p>
    </template>

    <template v-if="convStore.isError">
        <p></p>
        <div class="text-atomic-tangerine-400 col-span-2 text-sm">
            API error: {{ convStore.error }}
        </div>
        <p></p>
    </template>

    <template v-if="status != View.ConversionRatesStatus.OK || convStore.isError">
        <p v-for="_ in 4">&nbsp;</p>
    </template>
</template>

<script setup lang="ts">
import { useConvertRatesStore } from '@/stores/convert-rates'
import { computed } from 'vue'
import { View } from '@/types-and-utils/model'

const convStore = useConvertRatesStore()
const status = computed(() => convStore.ratesStatus)
</script>
