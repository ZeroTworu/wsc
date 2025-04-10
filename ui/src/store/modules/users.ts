import { Module } from "vuex";
import { Api } from "@/api/api"
import type {RootState} from "@/store";


export type User = {
  user_id: string;
  email: string;
  username: string;
}

export interface UsersState {
  listUsers: User[];
}

export const users: Module<UsersState, RootState> = {
  namespaced: true,

  state: (): UsersState => ({
    listUsers: [],
  }),

  mutations: {
    setUsers(state: UsersState, users: User[]) {
      state.listUsers = users;
    },
  },
 getters: {
  users: (state: UsersState) => state.listUsers
  },
  actions: {
    async fetchUsers({ commit }) {
      const response = await Api.getUsers();
      commit("setUsers", response.data);
    },
  },
};
