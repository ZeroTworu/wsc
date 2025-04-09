import axios from "axios";

export class Api {
    static getMe() {
        return axios.get("/auth/me");
    }
    static getUsers() {
        return axios.put("/api/users/list");
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
