import { createStore } from "vuex";
import { auth} from "./modules/auth.ts";
import type { AuthState } from "./modules/auth.ts";

export interface RootState {
    auth: AuthState;
}

const store = createStore<RootState>({
    modules: {
        auth,
    },
});

export default store;
