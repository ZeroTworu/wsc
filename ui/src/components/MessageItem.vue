<template>
  <div class="message" :class="{ 'own-message': isOwnMessage }">
    <div class="message-bubble">
      <div v-if="!isOwnMessage" class="message-username">{{ msg.username }}</div>
      <div class="message-content">
        {{ msg.content }}
        <div class="message-meta">
          <span class="message-time">{{ msg.updated_at }}</span>
          <div class="read-status" @mouseenter="showMenu" @mouseleave="hideMenu">
            <span v-if="hasReaders" class="read-checks">
              <v-icon>mdi-check</v-icon>
              <v-icon v-if="multipleReaders">mdi-check</v-icon>
            </span>
            <span v-else class="read-checks">
              <v-icon>mdi-check</v-icon>
            </span>
            <v-menu v-model="showReadersList" activator="parent" offset-y>
              <v-list>
                <v-list-item
                  v-for="reader in filteredReaders"
                  :key="reader.user_id"
                >
                  <v-list-item-title>{{ reader.username }}</v-list-item-title>
                </v-list-item>
                <v-list-item v-if="noOtherReaders">
                  <v-list-item-title>Нет прочитавших</v-list-item-title>
                </v-list-item>
              </v-list>
            </v-menu>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import {computed, ref} from 'vue';
import {useStore} from 'vuex';

const props = defineProps({
  msg: {
    type: Object,
    required: true
  },
  isOwnMessage: {
    type: Boolean,
    default: false
  }
});

const store = useStore();
const user = computed(() => store.getters['auth/me']);
const showReadersList = ref(false);

const hasReaders = computed(() => props.msg.readers.length > 0);
const multipleReaders = computed(() => props.msg.readers.length > 1);
const filteredReaders = computed(() =>
  props.msg.readers.filter((r: any) => r.user_id !== user.value.user_id)
);
const noOtherReaders = computed(() =>
  props.msg.readers.length === 0 ||
  props.msg.readers.every((r: any) => r.user_id === user.value.user_id)
);

const showMenu = () => {
  showReadersList.value = true;
};

const hideMenu = () => {
  showReadersList.value = false;
};
</script>

<style scoped>
.message {
  margin: 8px 0;
  display: flex;
  max-width: 80%;
}

.own-message {
  margin-left: auto;
}

.message-bubble {
  position: relative;
  min-width: 120px;
}

.message-content {
  padding: 8px 12px;
  border-radius: 7.5px;
  position: relative;
  word-break: break-word;
  line-height: 1.4;
  box-shadow: 0 1px 0.5px rgba(0, 0, 0, 0.13);
}

/* Сообщения других пользователей */
.message:not(.own-message) .message-content {
  background: #ffffff;
  border-radius: 0 8px 8px 8px;
}

/* Свои сообщения */
.own-message .message-content {
  background: #e2ffc7;
  border-radius: 8px 0 8px 8px;
}

.message-username {
  font-weight: 500;
  color: #999;
  font-size: 0.8rem;
  margin-bottom: 2px;
}

.message-meta {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  margin-top: 4px;
}

.message-time {
  color: #667781;
  font-size: 0.75rem;
  margin-right: 4px;
}

.read-status {
  display: flex;
  align-items: center;
}

.read-checks {
  color: #0086ff;
}

.read-checks .v-icon {
  font-size: 0.9rem;
}

/* Треугольник-указатель для чужих сообщений */
.message:not(.own-message) .message-bubble::before {
  content: '';
  position: absolute;
  left: -8px;
  top: 0;
  width: 0;
  height: 0;
  border-top: 0 solid transparent;
  border-bottom: 8px solid transparent;
  border-right: 8px solid #ffffff;
}

/* Треугольник-указатель для своих сообщений */
.own-message .message-bubble::after {
  content: '';
  position: absolute;
  right: -8px;
  bottom: 0;
  width: 0;
  height: 0;
  border-top: 8px solid transparent;
  border-left: 8px solid #e2ffc7;
  border-bottom: 0 solid transparent;
}

/* Анимация при наведении */
.message-bubble:hover .message-content {
  filter: brightness(98%);
}

.read-checks {
  display: inline-flex;
  gap: 2px;
  margin-left: 4px;
}

.read-checks .v-icon {
  color: #0086ff;
  font-size: 16px;
}
</style>
