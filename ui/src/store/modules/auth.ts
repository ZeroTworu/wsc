import type {Module} from "vuex";
import type {RootState} from "@/store";
import {Api} from "@/api/api";

export type SystemUser = {
  user_id: string;
  username: string;
  email: string;
};

export type Token = {
  access_token: string,
  token_type: string,
};

export interface AuthState {
  me: SystemUser | null;
  ws: WebSocket | null;
}

const state: AuthState = {
  me: null,
  ws: null as WebSocket | null,
};

const mutations = {
  SET_USER(state: AuthState, user: SystemUser) {
    localStorage.setItem("authUser", JSON.stringify(user));
  },
  SET_TOKEN(state: AuthState, user: SystemUser) {
    localStorage.setItem("authToken", JSON.stringify(user));
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
  SET_WS(state: AuthState, ws: WebSocket) {
    state.ws = ws;
  },
  CLEAR_USER(state: AuthState) {
    state.me = null;
    state.ws?.close();
    state.ws = null;
    localStorage.removeItem("authUser");
    localStorage.removeItem("authToken");
  },
};

const actions = {
  async login({commit, dispatch}: any, credentials: any) {
    const {data} = await Api.login(credentials);
    commit("SET_TOKEN", data);
    dispatch("connectWebSocket");
  },

  async register({commit, dispatch}: any, userInfo: any) {
    const {data} = await Api.register(userInfo);
    commit("SET_TOKEN", data);
    const user = await Api.getMe();
    commit("SET_USER", user.data);
    dispatch("connectWebSocket");
  },

  getMe({commit}) {
    return Api.getMe()
      .then((res) => {
        commit("SET_USER", res.data);
      })
      .catch((err) => {
        commit("CLEAR_USER");
        throw err;
      });
  },

  isCurrentUser({state}): boolean {
    return state.me !== null;
  },

  exit({commit}) {
    commit("CLEAR_USER");
  },

  connectWebSocket({commit, dispatch, state}: any) {
    if (state.ws) return;

    const token = localStorage.getItem("authToken");
    if (!token) return;
    const access_token = JSON.parse(token).access_token;
    const ws = new WebSocket(`${import.meta.env.VITE_WS_URL}?token=${access_token}`);

    ws.onopen = () => {
      setInterval(() => {
        ws.send(JSON.stringify({type: "ping"}));
      }, 2000)
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        console.log(data);
      } catch (error) {
        console.error("ws.onmessage.ERROR:", error);
      }
    };

    ws.onerror = (error) => {
      console.error("ws.onerror:", error);
    };

    ws.onclose = () => {
      commit("SET_WS", null);
      setTimeout(() => dispatch("connectWebSocket"), 5000);
    };

    commit("SET_WS", ws);
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
