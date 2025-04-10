import { createStore } from "vuex";
import { auth } from "./modules/auth.ts";
import type { AuthState } from "./modules/auth";
import type { UsersState } from "./modules/users";
import { users } from "./modules/users";

export interface RootState {
    auth: AuthState;
    users: UsersState,
}

const store = createStore<RootState>({
    modules: {
        auth,
        users,
    },
});

export default store;
