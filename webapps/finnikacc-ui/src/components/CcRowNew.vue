<template>
    <p></p>
    <v-autocomplete
        :items="items"
        item-title="quoteCurrency"
        item-value="quoteCurrency"
        density="compact"
        @update:model-value="onSelect"
        placeholder="select one more"
    >
        <template v-slot:item="{ item, props }">
            <v-list-item v-bind="props">
                <template #append>
                    <span class="text-sm">{{ item.raw.convertRate }}</span>
                </template>
            </v-list-item>
        </template>
    </v-autocomplete>
    <c-input-decimal density="compact" v-model="amount">text</c-input-decimal>
    <p></p>
</template>

<script setup lang="ts">
import CInputDecimal from '@/components/CInputDecimal.vue'
import type { Data } from '@/types-and-utils/model'
import Decimal from 'decimal.js'

defineProps<{
    items: Data.CurrencyConvertRateModel[]
}>()

const amount = defineModel<Decimal>('amount', { default: Decimal(0) })
const emit = defineEmits<{
    (e: 'currencySelected', currency: string): void
}>()

function onSelect(value: string | null) {
    if (!value) return
    emit('currencySelected', value)
}
</script>
