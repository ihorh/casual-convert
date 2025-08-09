<template>
    <div class="grid grid-cols-[auto_auto_auto_auto] gap-x-4 gap-y-0 items-center-safe">
        <cc-header-row />
        <template v-for="item in store.convRows" :key="item.currency">
            <cc-row
                :row-item="item"
                @amount-update="(amount) => store.updateAmount(item.currency, amount)"
                @delete="store.removeConvRow(item.currency)"
                :can-remove="store.canRemove(item.currency)"
            />
        </template>
        <cc-row-new
            :items="store.awailableCurrencies"
            :key="`new-row-${newRowKey}`"
            @currency-selected="handleCurrencySelectedNew"
        />
        <cc-conv-rate-status-rows />
    </div>
</template>

<script setup lang="ts">
import CcRow from './CcRow.vue'
import CcRowNew from './CcRowNew.vue'
import CcHeaderRow from './CcHeaderRow.vue'
import CcConvRateStatusRows from './CcConvRateStatusRows.vue'
import { useConvertBasketStore } from '@/stores/convert-basket'
import { ref } from 'vue'

const store = useConvertBasketStore()

const newRowKey = ref(0)

function handleCurrencySelectedNew(currency: string) {
    console.log(`selected new: ${currency}`)
    store.addConvRow(currency)
    newRowKey.value++
}
</script>
