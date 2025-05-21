import type {Module, ActionContext} from 'vuex';
import dayjs from 'dayjs'
import store, {type RootState} from '@/store';
import {Api} from '@/api/api';
import {EventType} from "@/store/stats";
import {type User} from "@/store/modules/auth";

export type Message = {
  user: User;
  content: string;
  readers: User[];
  showReadersList: boolean;
  created_at: string;
  updated_at: string;
  id: string;
}

export interface MessageState {
  messages: { [id: string]: Message[] };
  unreadMessageIds: { [id: string]: Set<string> };
  ws: WebSocket | null;
}

const state: MessageState = {
  messages: {},
  unreadMessageIds: {},
  ws: null,
}

const mutations = {
  SET_WS(state: MessageState, ws: WebSocket) {
    state.ws = ws;
  },
};

const getters = {
  messagesByChat: (state: MessageState) => (chatId: string) => {
    if (state.messages[chatId]) {
      return state.messages[chatId];
    }
    state.messages[chatId] = [];
    return state.messages[chatId];
  },
  unreadMessageIdsByChatId: (state: MessageState) => (chatId: string) => {
    if (state.unreadMessageIds[chatId]) {
      return state.unreadMessageIds[chatId];
    }
    state.unreadMessageIds[chatId] = new Set();
    return state.unreadMessageIds[chatId];
  },
};

const actions = {
  connectWebSocket({commit, dispatch, state}: ActionContext<MessageState, RootState>) {
    if (state.ws !== null && state.ws.readyState === WebSocket.OPEN) return;
    const token = localStorage.getItem("authToken") || "{}";
    if (!token) return;
    let reconnectInterval1: number, reconnectInterval2: number;
    const access_token = JSON.parse(token).access_token;
    const ws = new WebSocket(`${import.meta.env.VITE_WS_URL}?token=${access_token}`);
    const user = store.getters['auth/me'];
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
            console.log(data);

            const newMsg = {
              id: data.message_id,
              username: data.user.username,
              content: data.message,
              readers: data.readers || [],
              showReadersList: false,
              created_at: dayjs.unix(data.created_at).format("DD.MM.YYYY HH:mm:ss"),
              updated_at: dayjs.unix(data.updated_at).format("DD.MM.YYYY HH:mm:ss"),
            };

            if (state.messages[data.chat_id] == null) {
              state.messages[data.chat_id] = [];
            }

            if (state.unreadMessageIds[data.chat_id] == null) {
              state.unreadMessageIds[data.chat_id] = new Set();
            }

            if (!newMsg.readers.find((r: any) => r.id === user.value.id)) {
              state.unreadMessageIds[data.chat_id].add(data.message_id);
            }

            state.messages[data.chat_id].push(newMsg);
            break;
          case EventType.UPDATE_READERS:
            const msg = state.messages[data.chat_id].find(m => m.id === data.message_id);
            if (msg) {
              msg.readers = data.readers;
              if (state.unreadMessageIds[data.chat_id] == null) {
                state.unreadMessageIds[data.chat_id] = new Set();
              }
              if (data.readers.some((r: any) => r.user_id === user.user_id)) {
                state.unreadMessageIds[data.chat_id].delete(data.message_id);
              }
            }
            break;
          default:
            console.log("UB", event)
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
  },
  async loadHistory({state}: ActionContext<MessageState, RootState>, chatId: string) {
    const {data} = await Api.getHistory(chatId);
    data.forEach((val: any) => {
      const newMsg = {
        id: val.message_id,
        username: val.user.username,
        user_id: val.user.user_id,
        content: val.text,
        readers: val.readers || [],
        showReadersList: false,
        created_at: dayjs.unix(val.created_at).format("DD.MM.YYYY HH:mm:ss"),
        updated_at: dayjs.unix(val.updated_at).format("DD.MM.YYYY HH:mm:ss"),
      };
      state.messages[chatId].push(newMsg);
    })
  },

}

export const messages: Module<MessageState, RootState> = {
  namespaced: true,
  state,
  mutations,
  actions,
  getters,
};
