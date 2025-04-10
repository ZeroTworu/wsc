import axios from "axios";

export class Api {
    static getMe() {
        return axios.get("/auth/me");
    }
    static getUsers() {
        return axios.get("/api/users/list/all");
    }

    static getMyChats() {
        return axios.get("/api/chat/list/my");
    }

    static getAllChats() {
        return axios.get("/api/chat/list/all");
    }

    static createChat(val) {
        return axios.post("/api/chat/create", val);
    }

    static login(val) {
        const form = new FormData();

        form.append("username", val.username);
        form.append("password", val.password);
        form.append("grant_type", "password");

        return axios.post("/auth/login", form, {
          headers: { "Content-Type": "multipart/form-data" },
        });
    }

    static register(val) {
        return axios.post("/auth/register", val);
    }
}
