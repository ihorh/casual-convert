<template>
    <p></p>
    <v-autocomplete  :items="items" density="compact" @update:model-value="onSelect" placeholder="select one more">
        <template #append-inner>
            <!-- {{ model.rate?.conversionRate ?? 1 }}  -->
        </template>
    </v-autocomplete>
    <c-input-decimal density="compact" v-model="amount">text</c-input-decimal>
    <p></p>
</template>

<script setup lang="ts">

import CInputDecimal from "@/components/CInputDecimal.vue"
import Decimal from "decimal.js";

defineProps<{
    items: string[],
}>()

const amount = defineModel<Decimal>("amount", { default: Decimal(0) })
const emit = defineEmits<{
    (e: 'currencySelected', currency: string): void
}>()


function onSelect(value: string | null) {
    if (!value) return
    emit("currencySelected", value)
}
</script>
