
<template>
  <v-container>
    <v-card>
      <v-toolbar flat>
        <v-toolbar-title>Список пользователей</v-toolbar-title>
        <v-spacer />
        <v-btn
          v-if="selectedUsers.length >= 2"
          color="success"
          class="ml-2"
          @click="startGroupChat"
        >
          Групповой чат
        </v-btn>
      </v-toolbar>

      <v-data-table
        :headers="headers"
        :items="users"
        item-value="user_id"
        show-select
        v-model="selected"
        class="elevation-1"
        loading-text="Загружаем пользователей..."
      >
        <template #item.actions="{ item }">
          <v-btn color="primary" @click="startChat(item)">
            Начать
          </v-btn>
        </template>
      </v-data-table>

      <v-dialog v-model="dialog" max-width="500px">
        <v-card>
          <v-card-title>Создать групповой чат</v-card-title>
          <v-card-text>
            <v-text-field
              label="Название чата"
              v-model="chatName"
              required
              @keyup.enter="createChat"
            />
            <div v-if="errorMessage" class="error mt-2">{{ errorMessage }}</div>
          </v-card-text>
          <v-card-actions>
            <v-spacer />
            <v-btn text @click="dialog = false">Отмена</v-btn>
            <v-btn color="primary" @click="createChat">Создать</v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
    </v-card>
  </v-container>
</template>


<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { useStore } from 'vuex';
import { useRouter } from 'vue-router';
import type { User } from '@/store/modules/users';
import { ChatType } from '@/store/modules/chats';

const store = useStore();
const router = useRouter();
const loading = ref(false);
const selected = ref<string[]>([]);
const dialog = ref(false);
const chatName = ref('');
const errorMessage = ref('');
const users = computed(() => store.getters['users/users']);
const myChats = computed(() => store.getters['chats/myChats']);

const headers = [
  { text: 'ID', value: 'user_id' },
  { text: 'Имя пользователя', value: 'username' },
  { text: 'Email', value: 'email' },
  { text: 'Действия', value: 'actions', sortable: false },
];

const selectedUsers = computed(() =>
  users.value.filter(u => selected.value.includes(u.user_id))
);

const openChat = (chatId: string) => {
  router.push(`/chat/${chatId}`);
};


const findExistingPrivateChat = (userId: string) => {
  return myChats.value.find(chat =>
    chat.chat_type === ChatType.Private &&
    chat.participants.some(p => p.user_id === userId)
  );
};

const createChat = async () => {
  const participants = selectedUsers.value.map(u => u.user_id);
  if (!chatName.value || participants.length === 0) {
    errorMessage.value = 'Введите название и выберите участников';
    return;
  }

  try {
    const response = await store.dispatch('chats/createChat', {
      chat_name: chatName.value,
      chat_type: ChatType.Group,
      participants,
    });

    if (response?.id) {
      await store.dispatch('chats/fetchMyChats');
      openChat(response.id);
    } else {
      errorMessage.value = 'Ошибка создания чата';
    }
  } catch (err) {
    errorMessage.value = 'Ошибка создания чата';
  }
};

const startChat = async (user: User) => {
  const existing = findExistingPrivateChat(user.user_id);
  if (existing) {
    openChat(existing.id);
    return;
  }
  try {
    const response = await store.dispatch('chats/createChat', {
      chat_name: `Чат с ${user.username}`,
      chat_type: ChatType.Private,
      participants: [user.user_id],
    });

    if (response?.id) {
      await store.dispatch('chats/fetchMyChats');
      openChat(response.id);
    } else {
      errorMessage.value = 'Ошибка создания чата';
    }
  } catch (err) {
    errorMessage.value = 'Ошибка создания чата';
  }
};

const startGroupChat = () => {
  dialog.value = true;
};

onMounted(async () => {
  loading.value = true;
  await store.dispatch('users/fetchUsers');
  loading.value = false;
});
</script>
<style scoped>
.v-data-table {
  margin-top: 8px;
}
.error {
  font-size: 14px;
}
</style>
