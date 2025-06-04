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
        <SystemMessage :show-sys="showSys" :as-sys="true"/>
        <div v-for="(msg, index) in messages" :key="index" class="message">
          <MessageItem
            :msg="msg"
            :is-own-message="msg.user_id === user.user_id"
          />
        </div>
        <SystemMessage :show-sys="showSys" :as-sys="false"/>
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
import {EventType} from "../store/stats";
import MessageItem from "../components/MessageItem.vue";
import DisconnectAlert from "../components/DisconnectAlert.vue";
import SystemMessage from "../components/SystemMessage.vue";

const store = useStore();
const route = useRoute();
const router = useRouter();

const chatId = route.params.chat_id as string;

const newMessage = ref('');
const showSys = ref(false);
const ws = computed(() => store.state.messages.ws);
const user = computed(() => store.getters['auth/me']);
const chat = computed(() => store.getters['chats/chatById'](chatId));
const messages = computed(() => store.getters['messages/messagesByChat'](chatId));
const isWsConnected = computed(() => store.getters['messages/isWsConnected']);
const systemMessage = computed(() => store.getters['messages/systemMessage']());
const chatWindow = ref<HTMLElement | null>(null);

watch(
  () => systemMessage.value,
  (newMessage) => {
    if (newMessage) {
      showSys.value = true;
      scrollToBottom();
      setTimeout(() => {
        showSys.value = false
      }, 5000);
    }
  }
);

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

const onVisibilityChange = () => {
  if (document.visibilityState === 'visible') {
    store.dispatch("messages/sendAllUpdateRead", chatId);
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

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.theme--dark .system-message {
  background: rgba(var(--v-theme-primary-darken-1), 0.15);
  color: rgba(var(--v-theme-on-primary-darken-1), 0.9);
}

</style>
