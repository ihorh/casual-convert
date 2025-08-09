import { ref, onMounted, onUnmounted } from 'vue'

export function useCurrentTime(updateIntevalMs: number = 15000) {
    const now = ref(Date.now())

    let timerId: ReturnType<typeof setInterval> | undefined
    onMounted(() => {
        timerId = setInterval(() => {
            now.value = Date.now()
        }, updateIntevalMs)
    })
    onUnmounted(() => clearInterval(timerId))

    return now
}
