<template>
  <v-container>
    <v-card>
      <v-toolbar flat color="white">
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
        v-model:selected="selected"
        class="elevation-1"
        loading-text="Загружаем пользователей..."
      >
        <template #item.actions="{ item }">
          <v-btn color="primary" @click="startChat(item)">
            Начать
          </v-btn>
        </template>
      </v-data-table>
    </v-card>
  </v-container>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { useStore } from 'vuex';
import type { User } from '@/store/modules/users';

const store = useStore();
const loading = ref(false);
const selected = ref<string[]>([]);

const headers = ref([
  { text: 'ID', value: 'user_id' },
  { text: 'Имя пользователя', value: 'username' },
  { text: 'Email', value: 'email' },
  { text: 'Действия', value: 'actions', sortable: false },
]);

const users = computed(() => store.getters['users/users']);

const selectedUsers = computed(() =>
  users.value.filter(u => selected.value.includes(u.user_id))
);


onMounted(async () => {
  loading.value = true;
  await store.dispatch('users/fetchUsers');
  loading.value = false;
});

const  startChat = (user: User) => {
  console.log('Открыть чат с:', user.username, user.user_id);
}

const startGroupChat = () => {
  console.log('Групповой чат с:', selected.value.map(u => u));
}
</script>

<style scoped>
.v-data-table {
  margin-top: 8px;
}
</style>
