<template>
    <v-text-field
        :density="density"
        v-model="amountInput"
        @focus="inputHasFocus = true"
        @blur="onBlur"
        reverse
    >
    <template #prepend-inner>
        <v-spacer />
    </template>
    </v-text-field>
</template>

<script setup lang="ts">
import { parseDecimal } from '@/types-and-utils/utils'
import Decimal from 'decimal.js'
import { ref, watch } from 'vue'
import type { Density } from 'vuetify/lib/composables/density.mjs'

defineProps<{ density: Density }>()

const emit = defineEmits<{
    (e: 'userInput'): void
}>()

const decimalPlaces = 2
const amountDefault = Decimal(0)

const inputHasFocus = ref(false)

const amountDecimal = defineModel<Decimal>({ required: true })
const amountInput = ref(amountDecimal.value.toFixed(decimalPlaces))

function onBlur() {
    inputHasFocus.value = false
    amountInput.value = amountDecimal.value.toFixed(decimalPlaces)
}

watch(amountInput, (val) => {
    let dec = parseDecimal(val, amountDefault)
    if (dec) {
        amountDecimal.value = dec
        emit('userInput')
    }
})
watch(
    () => amountDecimal.value,
    (val) => {
        if (inputHasFocus.value) {
            // avoid jumping cursor while user enters data
            return
        }
        amountInput.value = amountDecimal.value.toFixed(decimalPlaces)
    },
)
</script>
