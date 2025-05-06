<template>
  <v-form @submit.prevent="enter">
    <v-alert v-show="loginError" type="error" class="mb-4" @click="loginError = false">
      Неверный логин или пароль
    </v-alert>

    <v-container>
      <v-row>
        <v-col cols="12">
          <v-text-field
            v-model="login"
            label="Логин"
            required
            autocomplete="username"
          />
        </v-col>
      </v-row>

      <v-row>
        <v-col cols="12">
          <v-text-field
            v-model="password"
            label="Пароль"
            type="password"
            required
            autocomplete="current-password"
          />
        </v-col>
      </v-row>

      <v-row>
        <v-col cols="12">
          <v-btn :loading="loading" color="primary" class="mr-4" @click="enter">
            Войти
          </v-btn>

          <v-btn variant="text" color="secondary" @click="showRegister = true">
            Нет аккаунта?
          </v-btn>
        </v-col>
      </v-row>
    </v-container>


    <v-dialog v-model="showRegister" max-width="500">
      <v-card>
        <v-card-title>Регистрация</v-card-title>
        <v-card-text>
          <v-text-field
            v-model="regUsername"
            label="Логин"
            :rules="[v => !!v || 'Обязательное поле']"
            required
          />
          <v-text-field
            v-model="regEmail"
            label="Email"
            :rules="emailRules"
            required
            type="email"
          />
          <v-text-field
            v-model="regPassword"
            label="Пароль"
            :rules="[v => !!v || 'Обязательное поле']"
            required
            type="password"
          />
        </v-card-text>
        <v-card-actions>
          <v-spacer/>
          <v-btn color="primary" @click="register">Зарегистрироваться</v-btn>
          <v-btn text @click="showRegister = false">Отмена</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-form>
</template>

<script setup lang="ts">
import {ref, computed} from "vue";
import {useStore} from "vuex";
import {useRouter} from "vue-router";

const store = useStore();
const router = useRouter();

const login = ref("");
const password = ref("");
const loginError = ref(false);
const loading = ref(false);

const showRegister = ref(false);
const regUsername = ref("");
const regEmail = ref("");
const regPassword = ref("");

const emailRules = computed(() => [
  value => !!value || 'Обязательное поле',
  value => /.+@.+\..+/.test(value) || 'E-mail должен быть валидным'
])

const enter = async () => {
  loginError.value = false;
  loading.value = true;

  const payload = {
    username: login.value,
    password: password.value,
  };

  try {
    await store.dispatch("auth/login", payload);
    await store.dispatch("auth/getMe"); // для отображения панели навигации
    router.push({name: "home"});
  } catch (err) {
    console.error("Auth error:", err);
    loginError.value = true;
  } finally {
    loading.value = false;
  }
};

const register = async () => {
  const payload = {
    username: regUsername.value,
    password: regPassword.value,
    email: regEmail.value,
  };

  try {
    await store.dispatch("auth/register", payload);
    showRegister.value = false;
    router.push("home");
  } catch (err) {
    console.error("Registration error:", err);
  }
};

</script>

<style scoped>
.v-alert {
  max-width: 400px;
  margin: auto;
}
</style>
