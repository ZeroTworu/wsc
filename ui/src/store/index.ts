import { createStore } from "vuex";
import { auth } from "./modules/auth";
import type { AuthState } from "./modules/auth";
import type { UsersState } from "./modules/users";
import { users } from "./modules/users";
import { chats } from "./modules/chats";
import { messages } from "./modules/messages";

export interface RootState {
    auth: AuthState;
    users: UsersState,
}

const store = createStore<RootState>({
    modules: {
        auth,
        users,
        chats,
        messages,
    },
});

export default store;
