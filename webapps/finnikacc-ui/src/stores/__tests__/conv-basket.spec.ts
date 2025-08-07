import { describe, it, expect, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useConvertBasketStore } from '../convert-basket'

describe('Convert Basket Store', () => {
    beforeEach(() => {
        setActivePinia(createPinia()) // Create fresh Pinia for each test
    })

    it('should initialize with only main base', () => {
        const store = useConvertBasketStore()
        expect(store.convRows.length).toBe(1)
        let mainBase = store.convRows[0]
        expect(mainBase.currency).toBe("USD")
        expect(mainBase.isCurrentBase).toBe(true)
        expect(mainBase.isMainBase).toBe(true)
    })
})