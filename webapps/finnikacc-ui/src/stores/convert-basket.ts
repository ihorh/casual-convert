import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import Decimal from 'decimal.js'
import type { Data, View } from '@/types-and-utils/model'
import { useConvertRatesStore } from './convert-rates'

const MAIN_BASE_AMOUNT_DEFAULT = Decimal(100)

export const useConvertBasketStore = defineStore('convert-basket', () => {
    const convStore = useConvertRatesStore()

    const convRows = ref<View.CurrencyConvRow[]>([
        createQuoteRowDefaults(convStore.mainBaseCurrency, MAIN_BASE_AMOUNT_DEFAULT, true, true),
    ])

    const awailableCurrencies = computed(() =>
        convStore.supportedCurrencies.filter((c) => !contains(c.quoteCurrency)),
    )

    function contains(currency: String): boolean {
        return convRows.value.some((row) => row.currency === currency)
    }

    function canRemove(currency: string): boolean {
        return currency !== convStore.mainBaseCurrency.quoteCurrency
    }

    function addConvRow(currency: string) {
        if (contains(currency) || !convStore.supports(currency)) {
            throw new Error('Unexpected error')
        }
        convRows.value.push(createQuoteRowDefaults(convStore.getConvRateModel(currency)))
        updateAllRows()
    }

    function removeConvRow(currency: string) {
        console.log('removeConvRow: ', currency)
        if (!canRemove(currency)) {
            throw new Error('Unexpected error')
        }
        convRows.value = convRows.value.filter((row) => row.currency !== currency)
    }

    function setNewCurrenBase(currency: string) {
        let curr = convRows.value.find((row) => row.currency === currency)
        if (!curr) return
        curr.isCurrentBase = true
        curr.convRateCurrentBase = Decimal(1)
        for (const i of convRows.value) {
            if (i.currency !== currency) {
                i.isCurrentBase = false
                i.convRateCurrentBase = i.convRateMainBase.div(curr.convRateMainBase)
                i.amount = curr.amount.times(i.convRateCurrentBase)
            }
        }
    }

    function updateAllRows() {
        let curr = convRows.value.find((row) => row.isCurrentBase)
        if (!curr) return
        setNewCurrenBase(curr.currency)
    }

    function updateAmount(currency: string, amount: Decimal) {
        setNewCurrenBase(currency)
    }

    return {
        convRows,
        awailableCurrencies,
        contains,
        canRemove,
        addConvRow,
        removeConvRow,
        updateAmount,
    }
})

const createQuoteRowDefaults = (
    currency: Data.CurrencyConvertRateModel,
    amount: Decimal = Decimal(0),
    isMainBase: boolean = false,
    isCurrentBase: boolean = false,
): View.CurrencyConvRow => ({
    currency: currency.quoteCurrency,
    amount: amount,
    convRateMainBase: currency.convertRate,
    convRateCurrentBase: currency.convertRate,
    isMainBase: isMainBase,
    isCurrentBase: isCurrentBase,
})
