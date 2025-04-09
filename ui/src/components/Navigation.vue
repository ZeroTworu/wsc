<template>
  <v-container v-show="route.path !== '/login'" app>
    <v-navigation-drawer>
      <v-list-item link>
        <v-list-item-content @click="goto('/')">
          <v-list-item-title class="text-h6">
            WS Chats
          </v-list-item-title>
        </v-list-item-content>
      </v-list-item>
      <v-divider></v-divider>

      <v-list dense nav>
        <!-- v-list-item-group управляет активным элементом -->
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
  </v-container>
</template>

<script lang="ts" setup>
import {ref, watchEffect} from "vue";
import {useRoute, useRouter} from "vue-router";

const router = useRouter();
const route = useRoute();


const navigation = [
  {text: "Чаты", path: "/chats", icon: "mdi-file-document-outline"},
  {text: "Пользователи", path: "/users", icon: "mdi-file-document-outline"},
];


const activeItem = ref(route.path);


const goto = (path: string) => {
  router.push(path);
};


watchEffect(() => {
  activeItem.value = route.path;
});
</script>

<style scoped></style>
