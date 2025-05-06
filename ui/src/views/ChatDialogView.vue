<template>
  <v-container>
    <v-card>
      <v-toolbar flat color="white">
        <v-toolbar-title>Чат: {{ chat.chat_name }}</v-toolbar-title>
        <v-spacer />
        <v-btn @click="router.push({name: 'home'})" color="error">Покинуть чат</v-btn>
      </v-toolbar>

      <v-card-text class="chat-window">
        <v-alert
          v-if="!isWsConnected"
          type="info"
          border="start"
          colored-border
          class="mb-4 d-flex align-center"
        >
          <v-progress-circular indeterminate size="20" class="mr-2" />
          Соединение потеряно, переподключаемся...
          <v-spacer />
        </v-alert>

        <div v-for="(msg, index) in messages" :key="index" class="message">
          <strong>{{ msg.username }}:</strong> {{ msg.content }}
          <div class="read-status" @mouseenter="showReadersList(index)" @mouseleave="hideReadersList(index)">
            <span v-if="msg.readers.length > 0" class="read-checks">
              <v-icon>mdi-check</v-icon>
              <v-icon v-if="msg.readers.length > 1">mdi-check</v-icon>
            </span>
            <span v-else class="read-checks">
              <v-icon>mdi-check</v-icon>
            </span>
            <v-menu v-model="msg.showReadersList" activator="parent" offset-y>
              <v-list>
                <v-list-item
                  v-for="reader in msg.readers.filter(r => r.user_id !== user.user_id)"
                  :key="reader.user_id"
                >
                  <v-list-item-title>{{ reader.username }}</v-list-item-title>
                </v-list-item>
                <v-list-item v-if="msg.readers.length === 0 || msg.readers.every(r => r.user_id === user.user_id)">
                  <v-list-item-title>Нет прочитавших</v-list-item-title>
                </v-list-item>
              </v-list>
            </v-menu>
          </div>
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
          :disabled="!isWsConnected"
        />
        <v-btn @click="sendMessage" color="primary" :disabled="!isWsConnected">
          Отправить
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-container>
</template>

<script setup lang="ts">
import { onMounted, onBeforeUnmount, ref, computed, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useStore } from 'vuex';
import { EventType } from "@/store/stats";
import { eventBus } from "@/store/EventBus.ts";

const store = useStore();
const route = useRoute();
const router = useRouter();

const chatId = route.params.chat_id as string;
const messages = ref<
  {
    username: string;
    content: string;
    readers: any[];
    showReadersList: boolean;
    id?: number;
  }[]
>([]);

const newMessage = ref('');
const ws = computed(() => store.state.auth.ws);
const user = computed(() => store.getters['auth/me']);
const chat = computed(() => store.getters['chats/chatById'](chatId));
const unreadMessageIds = ref<Set<string>>(new Set());

const isWsConnected = computed(() => {
  return ws.value !== null && ws.value.readyState === WebSocket.OPEN;
});


const sendMessage = () => {
  if (!isWsConnected.value || !newMessage.value.trim()) return;
  const msg = {
    type: EventType.MESSAGE,
    chat_id: chatId,
    message: newMessage.value.trim(),
  };
  ws.value?.send(JSON.stringify(msg));
  newMessage.value = '';
};

const handleMessage = (event: any) => {
  if (event.chat_id !== chatId) {
    return;
  }

  const newMsg = {
    id: event.message_id,
    username: event.user.username,
    content: event.message,
    readers: event.readers || [],
    showReadersList: false,
  };
  messages.value.push(newMsg);
  if (!newMsg.readers.find((r: any) => r.id === user.value.id)) {
    unreadMessageIds.value.add(event.message_id);
  }

};

const handleUpdateReaders = (event: any) => {
    console.log(event);
    const msg = messages.value.find(m => m.id === event.message_id);
    if (msg) {
      msg.readers = event.readers;

      if (event.readers.some((r: any) => r.user_id === user.value.id)) {
        unreadMessageIds.value.delete(event.message_id);
      }
    }

};

const sendReadUpdates = () => {
  if (!isWsConnected.value || unreadMessageIds.value.size === 0) return;
  console.log(unreadMessageIds.value);
  for (const id of unreadMessageIds.value) {
    const readMsg = {
      type: EventType.UPDATE_READERS,
      chat_id: chatId,
      message_id: id,
      user_id: user.value.user_id,
    };
    ws.value?.send(JSON.stringify(readMsg));
  }

  unreadMessageIds.value.clear();
};

const onVisibilityChange = () => {
  if (document.visibilityState === 'visible') {
    sendReadUpdates();
  }
};

const showReadersList = (index: number) => {
  messages.value[index].showReadersList = true;
};
const hideReadersList = (index: number) => {
  messages.value[index].showReadersList = false;
};

onMounted(() => {
  eventBus.on(EventType.MESSAGE, handleMessage);
  eventBus.on(EventType.UPDATE_READERS, handleUpdateReaders);
  document.addEventListener('visibilitychange', onVisibilityChange);
  window.addEventListener('focus', onVisibilityChange)
});

onBeforeUnmount(() => {
  eventBus.off(EventType.MESSAGE, handleMessage);
  eventBus.off(EventType.UPDATE_READERS, handleUpdateReaders);
  document.removeEventListener('visibilitychange', onVisibilityChange);
  window.removeEventListener('focus', onVisibilityChange)
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

.read-status {
  position: relative;
  display: inline-block;
  margin-left: 8px;
}

.read-checks {
  color: #4caf50;
}
</style>
