<template>
  <v-container v-show="route.path !== '/login'" app>
    <v-navigation-drawer>
      <v-list-item link>
        <v-list-item-content @click="goto('/')">
          <v-list-item-title v-if="user" class="text-h6">
            {{ user.username }}
          </v-list-item-title>
        </v-list-item-content>
      </v-list-item>
      <v-divider></v-divider>

      <v-list dense nav>
        <v-list-item-group v-model="activeItem" color="primary">
          <v-list-item
              v-for="(item, index) in navigation"
              :key="index"
              :value="item.path"
              link
              @click="goto(item.path)"
          >
            <v-list-item-icon>
              <v-icon>{{ item.icon }}</v-icon>
            </v-list-item-icon>
            <v-list-item-content>
              <v-list-item-title>{{ item.text }}</v-list-item-title>
            </v-list-item-content>
          </v-list-item>
        </v-list-item-group>
      </v-list>
    </v-navigation-drawer>
    <v-app-bar app>
      <v-btn @click="toggleTheme" icon>
        <v-icon>{{ isDark ? 'mdi-weather-night' : 'mdi-weather-sunny' }}</v-icon>
      </v-btn>
    </v-app-bar>
  </v-container>
</template>

<script lang="ts" setup>
import {computed, ref, watchEffect} from "vue";
import {useRoute, useRouter} from "vue-router";
import {useStore} from "vuex";
import { useTheme } from 'vuetify'

const router = useRouter();
const route = useRoute();
const store = useStore()
const user = computed(() => store.getters['auth/me']);
const theme = useTheme()

const navigation = [
  {text: "Чаты", path: "/chats", icon: "mdi-file-document-outline"},
  {text: "Пользователи", path: "/users", icon: "mdi-file-document-outline"},
];

const activeItem = ref(route.path);
const isDark = computed(() => theme.global.name.value === 'dark')

const goto = (path: string) => {
  router.push(path);
};

const toggleTheme = () => {
  theme.global.name.value = isDark.value ? 'light' : 'dark'
};

watchEffect(() => {
  activeItem.value = route.path;
});
</script>
