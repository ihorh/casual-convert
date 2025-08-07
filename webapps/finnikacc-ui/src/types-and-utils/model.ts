import type { Decimal } from "decimal.js"

export namespace View {

    export interface CurrencyConvRow {
        currency: string
        convRateMainBase: Decimal
        convRateCurrentBase: Decimal
        amount: Decimal
        isMainBase: boolean
        isCurrentBase: boolean
    }
}

export namespace Data {}