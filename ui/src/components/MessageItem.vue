<template>
  <div class="message">
    <strong>{{ msg.username }}:</strong> {{ msg.content }}
    <div
      class="read-status"
      @mouseenter="showMenu"
      @mouseleave="hideMenu"
    >
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
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import { useStore } from 'vuex';

const props = defineProps({
  msg: {
    type: Object,
    required: true
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
