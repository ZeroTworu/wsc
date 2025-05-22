<template>
  <v-alert
    v-if="!isWsConnected"
    type="info"
    border="start"
    colored-border
    class="mb-4 d-flex align-center"
  >
    <v-progress-circular indeterminate size="20" class="mr-2"/>
    Соединение потеряно, переподключаемся...
    <v-spacer/>
  </v-alert>
</template>
<script setup lang="ts">
import {useStore} from "vuex";
import {computed} from "vue";

const store = useStore();
const isWsConnected = computed(() => store.getters['messages/isWsConnected']);
</script>

<style scoped>

</style>
