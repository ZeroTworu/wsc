<template>
  <v-container>
    <v-card>
      <v-toolbar flat>
        <v-toolbar-title>Чат: {{ chat.chat_name }}</v-toolbar-title>
        <v-spacer/>
        <v-btn @click="leaveChat()" color="error">Покинуть чат</v-btn>
      </v-toolbar>

      <v-card-text ref="chatWindow" class="chat-window">
          <DisconnectAlert/>
          <SystemMessage/>
          <div v-for="(msg, index) in messages" :key="index" class="message">
            <MessageItem
              :msg="msg"
              :is-own-message="msg.user_id === user.user_id"
            />
          </div>
      </v-card-text>

      <v-divider/>

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
import {onMounted, onBeforeUnmount, ref, computed, watch, nextTick} from 'vue';
import {useRoute, useRouter} from 'vue-router';
import {useStore} from 'vuex';
import {EventType} from "@/store/stats";
import MessageItem from "@/components/MessageItem.vue";
import DisconnectAlert from "@/components/DisconnectAlert.vue";
import SystemMessage from "@/components/SystemMessage.vue";

const store = useStore();
const route = useRoute();
const router = useRouter();

const chatId = route.params.chat_id as string;

const newMessage = ref('');
const ws = computed(() => store.state.messages.ws);
const user = computed(() => store.getters['auth/me']);
const chat = computed(() => store.getters['chats/chatById'](chatId));
const messages = computed(() => store.getters['messages/messagesByChat'](chatId));
const unreadMessageIds = computed(() => store.getters['messages/unreadMessageIdsByChatId'](chatId));
const isWsConnected = computed(() => store.getters['messages/isWsConnected']);
const chatWindow = ref<HTMLElement | null>(null);

watch(
  () => messages.value.length,
  (newLength, oldLength) => {
    if (newLength > oldLength) {
      scrollToBottom();
    }
  }
);

const leaveChat = async () => {
  await store.dispatch('chats/leaveChat', chatId);
  await router.push({name: 'home'});
}

const scrollToBottom = async () => {
  if (chatWindow.value) {
    await nextTick();
    const el = chatWindow.value.$el;
    el.scrollTop = el.scrollHeight;
  }
};

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

const sendReadUpdates = () => {
  if (!isWsConnected.value || unreadMessageIds.value.size === 0) return;
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

onMounted(() => {
  store.dispatch("messages/loadHistory", chatId);
  scrollToBottom();
  document.addEventListener('visibilitychange', onVisibilityChange);
  window.addEventListener('focus', onVisibilityChange);
});

onBeforeUnmount(() => {
  store.dispatch("messages/exitChat", chatId);
  document.removeEventListener('visibilitychange', onVisibilityChange);
  window.removeEventListener('focus', onVisibilityChange);
});
</script>

<style scoped>
.chat-window {
  height: 400px;
  overflow-y: auto;
  padding: 16px;
  scroll-behavior: smooth;
  background-color: rgba(var(--v-theme-surface), 0.7);
  color: rgba(var(--v-theme-on-surface), 0.87);
  border-radius: 4px;
  transition: background-color 0.3s ease;
  overflow-x: hidden;
}

.theme--light .chat-window {
  background-color: #f9f9f9;
}

.theme--dark .chat-window {
  background-color: rgba(var(--v-theme-surface-darken-1), 0.9);
}

.message {
  margin-bottom: 10px;
}
</style>
