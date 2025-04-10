import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import store from "@/store/index";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
      meta: {
        guest: false,
      },
    },
    {
      path: '/chats',
      name: 'chats',
      component: () => import('../views/ChatsView.vue'),
      meta: {
        guest: false,
      },
    },
    {
      path: '/users',
      name: 'users',
      component: () => import('../views/UsersView.vue'),
      meta: {
        guest: false,
      },
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/LoginView.vue'),
      meta: {
        guest: true,
      },
    },
    {
      path: '/chat/:chat_id',
      name: 'chat-dialog',
      component: () => import('../views/ChatDialogView.vue'),
      meta: {
        guest: false,
      },
      props: true,
    },
  ],
})

router.beforeEach((to, from, next) => {
  if (!to.meta?.guest) {
    store
      .dispatch(`auth/getMe`)
      .then(() => next())
      .catch(() => next({ name: "login" }));
  } else {
    next();
  }
});

export default router
