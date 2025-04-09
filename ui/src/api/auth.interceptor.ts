import type { InternalAxiosRequestConfig } from 'axios';

export class AuthInterceptor {
  static request(req: InternalAxiosRequestConfig): InternalAxiosRequestConfig {
    const str_token = localStorage.getItem("authToken");
    if (str_token) {
      const token = JSON.parse(str_token).access_token;
      req.headers.Authorization = `Bearer ${token}`;
    }
    return req;
  }
}
