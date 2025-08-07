import { Decimal } from "decimal.js"

export function parseDecimal(value: string | null, default_value: Decimal): Decimal | null {
    if (!value) {
        return null
    }
    var val = value.replace(",", ".").replace(/[^\d.]/g, '');
    try {
        return val ? new Decimal(val) : default_value
    } catch {
        return default_value
    }
}
