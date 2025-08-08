import Decimal from 'decimal.js'
import { defineStore } from 'pinia'
import { computed } from 'vue'
import type { Data } from '@/types-and-utils/model'

const useMock = import.meta.env.MODE === 'preview'

const MAIN_BASE_CURRENCY = 'USD'

const _MAIN_BASE_CONV_RATES: { [key: string]: Decimal } = {
    USD: new Decimal(1),
    EUR: new Decimal(0.86),
    GBP: new Decimal(0.75),
    PLN: new Decimal(3.7),
    UAH: new Decimal(41.71),
}

const MAIN_BASE_CONV_RATES: Data.CurrencyConvertRateModel[] = [
    { baseCurrency: 'USD', quoteCurrency: 'USD', convertRate: Decimal(1) },
    { baseCurrency: 'USD', quoteCurrency: 'EUR', convertRate: Decimal(0.86) },
    { baseCurrency: 'USD', quoteCurrency: 'GBP', convertRate: Decimal(0.75) },
    { baseCurrency: 'USD', quoteCurrency: 'PLN', convertRate: Decimal(3.7) },
    { baseCurrency: 'USD', quoteCurrency: 'UAH', convertRate: Decimal(41.71) },
]

export const useConvertRatesStore = defineStore('convert-rates', () => {
    const supportedCurrencies = computed(() => MAIN_BASE_CONV_RATES)

    const mainBaseCurrency = computed(() => getConvRateModel(MAIN_BASE_CURRENCY))

    function supports(currency: string): boolean {
        return supportedCurrencies.value.some((r) => r.quoteCurrency === currency)
    }

    function getConvRateModel(currency: string): Data.CurrencyConvertRateModel {
        return supportedCurrencies.value.find((r) => r.quoteCurrency === currency)!
    }

    return { supportedCurrencies, mainBaseCurrency, getConvRateModel, supports }
})
