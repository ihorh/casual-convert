import { defineStore } from 'pinia'
import { computed } from 'vue'
import { type Data, View } from '@/types-and-utils/model'
import { useCurrencyRatesQuery } from './queries'
import { useCurrentTime } from '@/types-and-utils/useCurrentTime'
import { differenceInHours } from 'date-fns'

const useMock = import.meta.env.MODE === 'preview'

const MAIN_BASE_CURRENCY = 'USD'
const QUOTE_CURRENCIES = ['EUR', 'PLN', 'GBP', 'UAH']

export const useConvertRatesStore = defineStore('convert-rates', () => {
    const {
        isError,
        data: supportedCurrencies,
        error,
    } = useCurrencyRatesQuery([MAIN_BASE_CURRENCY, ...QUOTE_CURRENCIES].sort())

    const now = useCurrentTime(55000)

    const mainBaseCurrency = computed(() => getConvRateModel(MAIN_BASE_CURRENCY))
    const oldestRateByDate = computed(() =>
        supportedCurrencies.value.reduce((min, item) => {
            if (item.rateAt === undefined) return item
            else if (min.rateAt === undefined) return min
            else return item.rateAt < min.rateAt ? item : min
        }),
    )
    const oldestRateDate = computed(() => oldestRateByDate.value.rateAt ?? new Date(0))
    const hoursSinceOldesRate = computed(
        () => differenceInHours(now.value, oldestRateDate.value) ?? 1000,
    )

    const ratesStatus = computed(() => {
        if (hoursSinceOldesRate.value > 48) {
            return View.ConversionRatesStatus.VERY_OUTDATED
        } else if (hoursSinceOldesRate.value > 24) {
            return View.ConversionRatesStatus.JUST_OUTDATED
        } else if (hoursSinceOldesRate.value > 4) {
            return View.ConversionRatesStatus.SLIGHTLY_OUTDATED
        } else {
            return View.ConversionRatesStatus.OK
        }
    })

    function supports(currency: string): boolean {
        return supportedCurrencies.value.some((r) => r.quoteCurrency === currency)
    }

    function getConvRateModel(currency: string): Data.CurrencyConvertRateModel {
        return supportedCurrencies.value.find((r) => r.quoteCurrency === currency)!
    }

    return {
        supportedCurrencies,
        mainBaseCurrency,
        getConvRateModel,
        supports,
        error,
        isError,
        oldestRateByDate,
        ratesStatus,
    }
})
