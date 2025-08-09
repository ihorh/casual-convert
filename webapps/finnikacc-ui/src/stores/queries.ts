import type { Data } from '@/types-and-utils/model'
import { useQuery } from '@tanstack/vue-query'
import axios from 'axios'
import Decimal from 'decimal.js'

const MAIN_BASE_CONV_RATES: Data.CurrencyConvertRateModel[] = [
    { baseCurrency: 'USD', quoteCurrency: 'USD', convertRate: Decimal(1) },
    { baseCurrency: 'USD', quoteCurrency: 'EUR', convertRate: Decimal(0.86) },
    { baseCurrency: 'USD', quoteCurrency: 'GBP', convertRate: Decimal(0.75) },
    { baseCurrency: 'USD', quoteCurrency: 'PLN', convertRate: Decimal(3.7) },
    { baseCurrency: 'USD', quoteCurrency: 'UAH', convertRate: Decimal(41.71) },
]

export function useCurrencyRatesQuery(currencies_sorted: string[]) {
    return useQuery({
        queryKey: ['userProjects', currencies_sorted],
        queryFn: async () => await fetchCurrencyRates(currencies_sorted),

        // Optional settings
        staleTime: 5 * 60 * 1000, // 5 minutes cache
        gcTime: 20 * 60 * 1000, // 20 minutes cache before garbage collected
        refetchOnWindowFocus: false,
        refetchInterval: (query) => {
            return query.state.status === 'error' ? 10 * 1000 : 15 * 60 * 1000
        },
        retryDelay: (attemptIndex) => Math.min(2000 * 2 ** attemptIndex, 150 * 1000),
        retry: 4,

        initialData: MAIN_BASE_CONV_RATES,
        initialDataUpdatedAt: 0, // let's say it is very old
    })
}

const api = axios.create({
    baseURL: 'http://localhost:8000/api-web-app',
})

async function fetchCurrencyRates(
    currencies_sorted: string[],
): Promise<Data.CurrencyConvertRateModel[]> {
    console.log('call fetchCurrencyRates')
    const response = await api.get<Data.CurrencyConvertRateModel[]>('/convert-rates')
    const data: Data.CurrencyConvertRateModel[] = response.data
    for (const r of data) {
        r.convertRate = Decimal(r.convertRate)
        // r.rateAt = r.rateAt ? new Date(r.rateAt) : new Date(0)
    }
    console.debug(response.data)
    return response.data
}
