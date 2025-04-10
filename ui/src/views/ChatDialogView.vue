<template>
  <v-container>
    <v-card>
      <v-toolbar flat color="white">
        <v-toolbar-title>Чат: {{ chat.chat_name }}</v-toolbar-title>
        <v-spacer />
        <v-btn @click="router.push({name: 'home'})" color="error">Покинуть чат</v-btn>
      </v-toolbar>

      <v-card-text class="chat-window">
        <div v-for="(msg, index) in messages" :key="index" class="message">
          <strong>{{ msg.username }}:</strong> {{ msg.content }}
        </div>
      </v-card-text>

      <v-divider />

      <v-card-actions>
        <v-text-field
          v-model="newMessage"
          placeholder="Введите сообщение..."
          class="flex-grow-1"
          @keyup.enter="sendMessage"
          clearable
        />
        <v-btn @click="sendMessage" color="primary">Отправить</v-btn>
      </v-card-actions>
    </v-card>
  </v-container>
</template>

<script setup lang="ts">
import { onMounted, onBeforeUnmount, ref, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useStore } from 'vuex';
import { EventType } from "@/store/stats";
import { eventBus } from "@/store/EventBus.ts";

const store = useStore();
const route = useRoute();
const router = useRouter();

const chatId = route.params.chat_id as string;
const messages = ref<{ username: string; content: string }[]>([]);
const newMessage = ref('');
const ws = computed(() => store.state.auth.ws);
const user = computed(() => store.getters['auth/me']);
const chat = computed(() => store.getters['chats/chatById'](chatId));


const sendMessage = () => {
  if (!newMessage.value.trim()) return;
  const msg = {
    type: EventType.MESSAGE,
    chat_id: chatId,
    message: newMessage.value.trim(),
  };
  if (!ws.value || ws.value.readyState !== WebSocket.OPEN) {
    console.warn("WebSocket не готов к отправке сообщения");
    return;
  }
  ws.value?.send(JSON.stringify(msg));
  newMessage.value = '';
};

const handleMessage = (event: any) => {
  if (event.type === EventType.MESSAGE && event.chat_id === chatId) {
      messages.value.push({
        username: event.user.username,
        content: event.message,
      });
    }
};

onMounted(() => {
  eventBus.on(EventType.MESSAGE, handleMessage);
});

onBeforeUnmount(() => {
  eventBus.off(EventType.MESSAGE, handleMessage);
});

</script>

<style scoped>
.chat-window {
  height: 400px;
  overflow-y: auto;
  background-color: #f9f9f9;
  padding: 16px;
}

.message {
  margin-bottom: 10px;
}
</style>
