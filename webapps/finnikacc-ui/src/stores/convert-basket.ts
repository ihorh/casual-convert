import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import Decimal from 'decimal.js'
import type { View } from '@/types-and-utils/model'

const MAIN_BASE_CURRENCY = 'USD'
const MAIN_BASE_AMOUNT_DEFAULT = Decimal(100)

const MAIN_BASE_CONV_RATES: { [key: string]: Decimal } = {
    EUR: new Decimal(0.86),
    GBP: new Decimal(0.75),
    PLN: new Decimal(3.7),
    UAH: new Decimal(41.71),
}

export const useConvertBasketStore = defineStore('convert-basket', () => {
    const convRows = ref<View.CurrencyConvRow[]>([createMainBaseRow()])

    const awailableCurrencies = computed(() =>
        Object.keys(MAIN_BASE_CONV_RATES).filter((c) => !contains(c)),
    )
    const mainBaseCurrency = computed(() => convRows.value.filter((row) => row.isMainBase)[0])
    const currenBaseCurrency = computed(() => convRows.value.filter((row) => row.isCurrentBase)[0])

    function contains(currency: String): boolean {
        return convRows.value.some((row) => row.currency == currency)
    }

    function supports(currency: string): boolean {
        return currency in MAIN_BASE_CONV_RATES || currency === MAIN_BASE_CURRENCY
    }

    function canRemove(currency: string): boolean {
        return currency !== MAIN_BASE_CURRENCY
    }

    function addConvRow(currency: string) {
        if (contains(currency) || !supports(currency)) {
            throw new Error('Unexpected error')
        }
        convRows.value.push(createQuoteRowDefaults(currency))
        updateAllRows()
    }

    function removeConvRow(currency: string) {
        console.log('removeConvRow: ', currency)
        if (currency === MAIN_BASE_CURRENCY) {
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
        supports,
        canRemove,
        addConvRow,
        removeConvRow,
        updateAmount,
    }
})

const createMainBaseRow = (): View.CurrencyConvRow => ({
    currency: MAIN_BASE_CURRENCY,
    convRateMainBase: Decimal(1),
    convRateCurrentBase: Decimal(1),
    amount: MAIN_BASE_AMOUNT_DEFAULT,
    isMainBase: true,
    isCurrentBase: true,
})

const createQuoteRowDefaults = (currency: string): View.CurrencyConvRow => ({
    currency: currency,
    amount: Decimal(0),
    convRateMainBase: MAIN_BASE_CONV_RATES[currency],
    convRateCurrentBase: MAIN_BASE_CONV_RATES[currency],
    isMainBase: false,
    isCurrentBase: false,
})
