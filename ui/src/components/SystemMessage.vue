<template>
  <div
    v-if="showSystemMessage && asSys"
    class="system-notification"
    :class="{ 'system-notification-visible': showSystemMessage }"
  >
    {{ currentSystemMessage }}
  </div>
  <div v-if="showSys && !asSys" class="system-message">
    <v-icon small class="mr-2">mdi-information</v-icon>
    {{ systemMessage }}
  </div>
</template>

<script setup lang="ts">
import {computed, ref, watch, defineProps} from "vue";

import {useStore} from "vuex";
import {VIcon} from "vuetify/components";

const store = useStore();

const systemMessage = computed(() => store.getters['messages/systemMessage']());
const showSystemMessage = ref(false);
const currentSystemMessage = ref('');

defineProps({
  asSys: {
    type: Boolean,
    required: true
  },
  showSys: {
    type: Boolean,
    required: true
  },
});

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

.system-message {
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 8px auto;
  padding: 8px 16px;
  background: rgba(var(--v-theme-primary), 0.1);
  color: rgba(var(--v-theme-on-background), 0.8);
  border-radius: 16px;
  max-width: 80%;
  font-size: 0.9em;
  animation: fadeIn 0.3s ease;
}

</style>
