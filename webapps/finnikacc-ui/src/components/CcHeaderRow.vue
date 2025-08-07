<template>
    <p></p>
    <v-text-field readonly density="compact">
        <template #append-inner><p class="text-xs text-nowrap">x-rate</p></template>
        Currency
    </v-text-field>
    <v-text-field readonly density="compact" reverse> Amount </v-text-field>
    <p></p>

    <p></p>
    <hr />
    <hr />
    <p></p>

    <p></p>
    <p>&puncsp;</p>
    <p></p>
    <p></p>
</template>

<style lang="css" scoped>
@reference "@/assets/style.css";

hr {
    @apply text-atomic-tangerine-500;
}
</style>
