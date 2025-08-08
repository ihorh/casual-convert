<template>
    <v-btn v-if="canRemove" class="px-0 invisible" min-width="0">
        <i class="fas fa-trash-can text-red-600"></i>
    </v-btn>
    <p v-else></p>
    <v-text-field :readonly="true" density="compact">
        <template #append-inner>
            <span class="text-sm">{{ rowItem.convRateMainBase }}</span>
        </template>
        {{ rowItem.currency }}
    </v-text-field>
    <c-input-decimal density="compact" v-model="amount" @user-input="handleAmountUpdate">
    </c-input-decimal>
    <v-btn v-if="canRemove" @click="handleDelete" class="px-0" min-width="0">
        <i class="fas fa-trash-can text-red-600"></i>
    </v-btn>
    <p v-else></p>
</template>

<script setup lang="ts">
import CInputDecimal from '@/components/CInputDecimal.vue'
import type { View } from '@/types-and-utils/model'
import Decimal from 'decimal.js'
import { computed } from 'vue'

const props = defineProps<{
    rowItem: View.CurrencyConvRow
    canRemove: boolean
}>()
const amount = computed({
    get: () => props.rowItem.amount,
    set: (val: Decimal) => (props.rowItem.amount = val),
})
const emit = defineEmits<{
    (e: 'delete', currency: string): void
    (e: 'amountUpdate', amount: Decimal): void
}>()

function handleDelete() {
    if (!props.rowItem.currency) return
    emit('delete', props.rowItem.currency)
}
function handleAmountUpdate() {
    emit('amountUpdate', amount.value)
}
</script>
