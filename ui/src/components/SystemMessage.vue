<template>
<div
    v-if="showSystemMessage"
    class="system-notification"
    :class="{ 'system-notification-visible': showSystemMessage }"
  >
    {{ currentSystemMessage }}
  </div>
</template>

<script setup lang="ts">
import {computed, ref, watch} from "vue";

import {useStore} from "vuex";
const store = useStore();

const systemMessage = computed(() => store.getters['messages/systemMessage']());
const showSystemMessage = ref(false);
const currentSystemMessage = ref('');

watch(
  () => systemMessage.value,
  (newMessage) => {
    if (newMessage) {
      currentSystemMessage.value = newMessage;
      showSystemMessage.value = true;
      setTimeout(() => {
        showSystemMessage.value = false;
      }, 3000);
    }
  }
);
</script>

<style scoped>
.system-notification {
  position: sticky;
  top: 16px;
  z-index: 10;
  background: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 8px 16px;
  border-radius: 20px;
  margin: 0 auto 16px;
  max-width: max-content;
  opacity: 0;
  transform: translateY(-20px);
  transition: all 0.3s ease;
  font-size: 0.9em;
  backdrop-filter: blur(5px);
}

.system-notification-visible {
  opacity: 1;
  transform: translateY(0);
}

/* Для темной темы */
.theme--dark .system-notification {
  background: rgba(255, 255, 255, 0.15);
  color: rgba(255, 255, 255, 0.9);
}
</style>
