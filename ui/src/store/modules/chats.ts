import type { Module, ActionContext } from 'vuex';
import type { RootState } from '@/store';
import { Api } from '@/api/api';
import type { SystemUser } from './auth';

export enum ChatType {
  Private = 'PRIVATE',
  Group = 'GROUP',
}

export interface Chat {
  id: string;
  chat_name: string;
  chat_type: ChatType;
  owner_id: string;
  participants: SystemUser[];
}


export interface CreateChatPayload {
  chat_name: string;
  chat_type: ChatType;
  participants: string[];
}

export interface ChatsState {
  myChats: Chat[];
  allChats: Chat[];
}

const state: ChatsState = {
  myChats: [],
  allChats: [],
};

const mutations = {
  SET_MY_CHATS(state: ChatsState, chats: Chat[]) {
    state.myChats = chats;
  },
  SET_ALL_CHATS(state: ChatsState, chats: Chat[]) {
    state.allChats = chats;
  },
  ADD_CHAT(state: ChatsState, chat: Chat) {
    state.myChats.push(chat);
  },
};

const actions = {
  async fetchMyChats({ commit }: ActionContext<ChatsState, RootState>) {
    const response = await Api.getMyChats();
    commit('SET_MY_CHATS', response.data);
  },
  async fetchAllChats({ commit }: ActionContext<ChatsState, RootState>) {
    const response = await Api.getAllChats();
    commit('SET_ALL_CHATS', response.data);
  },
  async createChat(
    { commit }: ActionContext<ChatsState, RootState>,
    payload: CreateChatPayload
  ) {
    const { data } = await Api.createChat(payload);
    commit('ADD_CHAT', data);
    return data
  },
};

const getters = {
  myChats: (state: ChatsState) => state.myChats,
  allChats: (state: ChatsState) => state.allChats,
  chatById: (state: ChatsState) => (id: string) => {
    return state.myChats.find(chat => chat.id === id) || null;
  },
};

export const chats: Module<ChatsState, RootState> = {
  namespaced: true,
  state,
  mutations,
  actions,
  getters,
};
