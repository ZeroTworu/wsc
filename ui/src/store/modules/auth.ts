import type { Module, ActionContext } from "vuex";
import store, {type RootState} from "@/store";
import {Api} from "@/api/api";

export type SystemUser = {
  user_id: string;
  username: string;
  email: string;
};

export type User = {
  user_id: string;
  username: string;
};

export type Token = {
  access_token: string,
  token_type: string,
};

export interface AuthState {
  me: SystemUser | null;
  token: Token | null;
}

const state: AuthState = {
  me: null,
  token: null,
};

const mutations = {
  SET_USER(state: AuthState, user: SystemUser) {
    localStorage.setItem("authUser", JSON.stringify(user));
    state.me = user;
  },
  SET_TOKEN(state: AuthState, token: Token) {
    localStorage.setItem("authToken", JSON.stringify(token));
  },
  GET_USER(state: AuthState): SystemUser | null {
    const user = localStorage.getItem("currentUser");
    if (user) {
      const sys_user: SystemUser = JSON.parse(user);
      state.me = sys_user;
      return sys_user;
    }
    return null;
  },
  CLEAR_USER(state: AuthState) {
    state.me = null;
    localStorage.removeItem("authUser");
    localStorage.removeItem("authToken");
  },
};

const actions = {
  async login({commit}: ActionContext<AuthState, RootState>, credentials: any) {
    const {data} = await Api.login(credentials);
    commit("SET_TOKEN", data);
    store.dispatch("messages/connectWebSocket");
  },

  async register({commit}: ActionContext<AuthState, RootState>, userInfo: any) {
    const {data} = await Api.register(userInfo);
    commit("SET_TOKEN", data);
    const user = await Api.getMe();
    commit("SET_USER", user.data);
    store.dispatch("messages/connectWebSocket");
  },

  getMe({commit}: ActionContext<AuthState, RootState>) {
    return Api.getMe()
      .then((res) => {
        commit("SET_USER", res.data);
        store.dispatch("messages/connectWebSocket");
      })
      .catch((err) => {
        console.log("getMe.err: ", err)
        commit("CLEAR_USER");
        throw err;
      });
  },
};

const getters = {
  me: (state: AuthState) => state.me,
};

export const auth: Module<AuthState, RootState> = {
  namespaced: true,
  state,
  mutations,
  actions,
  getters,
};
