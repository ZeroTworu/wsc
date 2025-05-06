import type { Module, ActionContext } from "vuex";
import store, {type RootState} from "@/store";
import {Api} from "@/api/api";
import { EventType } from "@/store/stats"
import { eventBus } from "@/store/EventBus.ts";

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
  token: Token | null;
  ws: WebSocket | null;
}

const state: AuthState = {
  me: null,
  token: null,
  ws: null as WebSocket | null,
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
  async login({commit, dispatch}: ActionContext<AuthState, RootState>, credentials: any) {
    const {data} = await Api.login(credentials);
    commit("SET_TOKEN", data);
    dispatch("connectWebSocket");
  },

  async register({commit, dispatch}: ActionContext<AuthState, RootState>, userInfo: any) {
    const {data} = await Api.register(userInfo);
    commit("SET_TOKEN", data);
    const user = await Api.getMe();
    commit("SET_USER", user.data);
    dispatch("connectWebSocket");
  },

  getMe({commit, dispatch}: ActionContext<AuthState, RootState>) {
    return Api.getMe()
      .then((res) => {
        commit("SET_USER", res.data);
        dispatch("connectWebSocket");
      })
      .catch((err) => {
        console.log("getMe.err: ", err)
        commit("CLEAR_USER");
        throw err;
      });
  },

  connectWebSocket({commit, dispatch, state}: ActionContext<AuthState, RootState>) {
    if (state.ws !== null && state.ws.readyState === WebSocket.OPEN) return;
    const token = localStorage.getItem("authToken") || "{}";
    if (!token) return;
    let reconnectInterval1: number, reconnectInterval2: number;
    const access_token = JSON.parse(token).access_token;
    const ws = new WebSocket(`${import.meta.env.VITE_WS_URL}?token=${access_token}`);
    ws.onopen = () => {
      ws.send(JSON.stringify({type: EventType.PING}));
      commit("SET_WS", ws);
      if (reconnectInterval1 !== null) clearInterval(reconnectInterval1);
      if (reconnectInterval2 !== null) clearInterval(reconnectInterval2);
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        switch (data.type) {
          case EventType.MESSAGE:
            eventBus.emit(EventType.MESSAGE, data);
            break;
          case EventType.UPDATE_READERS:
            eventBus.emit(EventType.UPDATE_READERS, data);
            break;
          default:
            console.log("UD", event)
            break;
        }
      } catch (error) {
        console.error("ws.onmessage.ERROR:", error);
      }
    };

    ws.onerror = (error) => {
      console.error("ws.onerror:", error);
      commit("SET_WS", null);
      reconnectInterval1 = setInterval(() => dispatch("connectWebSocket"), 100);
    };

    ws.onclose = () => {
      commit("SET_WS", null);
      reconnectInterval2 = setInterval(() => dispatch("connectWebSocket"), 100);
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
