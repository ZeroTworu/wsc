<template>
  <v-container>
    <v-card>
      <v-toolbar flat>
        <v-toolbar-title>Список чатов</v-toolbar-title>
        <v-spacer />
      </v-toolbar>

      <v-data-table
        :headers="headers"
        :items="chats"
        item-value="id"
        class="elevation-1"
        loading-text="Загружаем чаты..."
        :loading="loading"
      >
        <template #item.chat_name="{ item }">
          <RouterLink
            :to="`/chat/${item.id}`"
            @click.native.prevent="openChat(item.id)"
            class="text-primary"
          >
            {{ item.chat_name }}
          </RouterLink>
        </template>
        <template #item.chat_type="{ item }">
          {{ item.chat_type }}
        </template>
        <template #item.participants="{ item }">
          <div v-for="p in item.participants" :key="p.user_id">{{ p.username }}</div>
        </template>
      </v-data-table>
    </v-card>
  </v-container>
</template>

<script setup lang="ts">
import { onMounted, ref, computed } from 'vue';
import { useStore } from 'vuex';
import { useRouter } from 'vue-router';

const store = useStore();
const router = useRouter();

const chats = computed(() => store.getters['chats/myChats']);
const isWsConnected = computed(() => store.getters['messages/isWsConnected']);
const loading = ref(false);

const headers = [
  { text: 'Название', value: 'chat_name' },
  { text: 'Тип', value: 'chat_type' },
  { text: 'Участники', value: 'participants' },
];



onMounted(() => {
  loading.value = true;
  store.dispatch('chats/fetchMyChats');
  loading.value = false;
});

const openChat = (chatId: string) => {
  if (isWsConnected.value) {
    store.dispatch("messages/enterChat", chatId);
  }
  router.push(`/chat/${chatId}`);
};
</script>

<style scoped>
.v-data-table {
  margin-top: 8px;
}
a.text-primary {
  text-decoration: none;
  color: #1976d2;
  cursor: pointer;
}
</style>
