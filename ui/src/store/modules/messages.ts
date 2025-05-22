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
  type?: string
  id: string;
}

export interface MessageState {
  messages: { [id: string]: Message[] };
  unreadMessageIds: { [id: string]: Set<string> };
  ws: WebSocket | null;
  systemMessage: string;
}

export interface UpdateMessageReadPayload {
  chatId: string;
  messageId: string;
}

export interface AddMessagePayload {
  chatId: string;
  message: Message;
}

export interface UpdateReadersPayload {
  chatId: string;
  messageId: string;
  readers: User[];
}

const state: MessageState = {
  messages: {},
  unreadMessageIds: {},
  ws: null,
  systemMessage: "",
}

const mutations = {
  SET_WS(state: MessageState, ws: WebSocket) {
    state.ws = ws;
  },
  SET_SYS_MSG(state: MessageState, message: string) {
    state.systemMessage = message;
  },
  ADD_MESSAGE(state: MessageState, payload: AddMessagePayload) {
    const user = store.getters['auth/me'];
    if (state.messages[payload.chatId] == null) {
      state.messages[payload.chatId] = [];
    }

    if (state.unreadMessageIds[payload.chatId] == null) {
      state.unreadMessageIds[payload.chatId] = new Set();
    }

    if (!payload.message.readers.find((r: any) => r.id === user.value.id)) {
      state.unreadMessageIds[payload.chatId].add(payload.message.id);
    }
    console.log(payload);
    state.messages[payload.chatId].push(payload.message);
  },
  UPDATE_READERS(state: MessageState, payload: UpdateReadersPayload){
    const { chatId, messageId, readers } = payload;
    const user = store.getters['auth/me'];
    const msg = state.messages[chatId].find(m => m.id === messageId);
    if (msg) {
      msg.readers = [...readers];
      if (state.unreadMessageIds[chatId] == null) {
        state.unreadMessageIds[chatId] = new Set();
      }
      if (readers.some((r: any) => r.user_id === user.user_id)) {
        state.unreadMessageIds[chatId].delete(messageId);
      }
    }
  },
  CLEAR_UNREAD_MESSAGES(state: MessageState, chatId: string) {
    if (!state.unreadMessageIds[chatId]) return;
    state.unreadMessageIds[chatId].clear();
  },
  REMOVE_SYS_MESSAGE(state: MessageState, text: string, chatId: string) {
    state.messages[chatId] = state.messages[chatId].filter(msg =>
      !(msg.type === 'system' && msg.content === text)
    );
  }
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
  isWsConnected: (state: MessageState) => () => {
    return state.ws !== null && state.ws.readyState === WebSocket.OPEN;
  },
  systemMessage: (state: MessageState) => () => {
    return state.systemMessage;
  }
};

const actions = {
  connectWebSocket({commit, dispatch, state}: ActionContext<MessageState, RootState>) {
    if (state.ws !== null) return;
    console.log("CONNECT WS");
    const token = localStorage.getItem("authToken") || "{}";
    if (!token) return;
    let reconnectInterval1: number, reconnectInterval2: number;
    const access_token = JSON.parse(token).access_token;
    const ws = new WebSocket(`${import.meta.env.VITE_WS_URL}?token=${access_token}`);
    commit("SET_WS", ws);
    ws.onopen = () => {
      ws.send(JSON.stringify({type: EventType.PING}));
      if (reconnectInterval1 !== null) clearInterval(reconnectInterval1);
      if (reconnectInterval2 !== null) clearInterval(reconnectInterval2);
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        switch (data.type) {
          case EventType.MESSAGE:
            const newMsg = {
              id: data.message_id,
              username: data.user.username,
              user_id: data.user.user_id,
              content: data.message,
              readers: data.readers || [],
              showReadersList: false,
              created_at: dayjs.unix(data.created_at).format("DD.MM.YYYY HH:mm:ss"),
              updated_at: dayjs.unix(data.updated_at).format("DD.MM.YYYY HH:mm:ss"),
            };
            commit("ADD_MESSAGE", {
              chatId: data.chat_id,
              message: newMsg,
            });
            if (document.visibilityState === 'visible') {
              dispatch("sendUpdateRead",
                {
                  chat_id: data.chat_id,
                  messageId: newMsg.id,
                }
              )
            }
            break;
          case EventType.UPDATE_READERS:
            commit("UPDATE_READERS", {
              chatId: data.chat_id,
              messageId: data.message_id,
              readers: data.readers,
            });
            break;
          case EventType.USER_ENTER_CHAT:
            commit("SET_SYS_MSG", `Пользователь ${data.user.username} вошёл в чат`);
            break;
          case EventType.USER_EXIT_CHAT:
            commit("SET_SYS_MSG", `Пользователь ${data.user.username} вышел из чата`);
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
      console.error("ws.onclose");
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
  enterChat({state}: ActionContext<MessageState, RootState>, chatId: string) {
    state.ws.send(JSON.stringify({type: EventType.USER_ENTER_CHAT, chat_id: chatId}));
  },
  exitChat({state}: ActionContext<MessageState, RootState>, chatId: string) {
    state.ws.send(JSON.stringify({type: EventType.USER_EXIT_CHAT, chat_id: chatId}));
  },
  sendUpdateRead({state}: ActionContext<MessageState, RootState>, payload: UpdateMessageReadPayload){
    const user = store.getters['auth/me'];
    const readMsg = {
      type: EventType.UPDATE_READERS,
      chat_id: payload.chatId,
      message_id: payload.messageId,
      user_id: user.user_id,
    };
    state.ws.send(JSON.stringify(readMsg));
  },
  sendAllUpdateRead({state, commit, dispatch}: ActionContext<MessageState, RootState>, chatId: string){
    if(!state.ws) return;
    console.log("sendAllUpdateRead");
    const messageIds = [...state.unreadMessageIds[chatId] || []];
    messageIds.forEach((id: string) => {
      dispatch("sendUpdateRead", {chatId: chatId, messageId: id});
    })
    commit('CLEAR_UNREAD_MESSAGES', chatId);
  },
}

export const messages: Module<MessageState, RootState> = {
  namespaced: true,
  state,
  mutations,
  actions,
  getters,
};
