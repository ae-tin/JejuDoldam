// src/api/client.js
import { useAuthStore } from '@/stores/auth';
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://127.0.0.1:80/api/v1',
});

// 매 요청마다 access 토큰을 Authorization 헤더에 실어줌
api.interceptors.request.use((config) => {
  const access = localStorage.getItem('access');
  if (access) {
    config.headers.Authorization = `Bearer ${access}`;
  }
  return config;
});


// 매 응답을 인터셉터가 가로채서 검사: 401 반환시 refresh 시도 및 로그아웃 처리
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const auth = useAuthStore();
    const originalRequest = error.config;

    // access 토큰 만료 등으로 401 반환 및 아직 재시도하지 않았다면(무한 재시도 방지)
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      const refresh = localStorage.getItem('refresh');

      // 만약 refresh가 없다면 로그아웃처리
      if (!refresh) {
        auth.logout();
        return Promise.reject(error);
      }

      try {
        // refresh 토큰으로 access 재발급 요쳥
        const { data } = await axios.post(
          'http://127.0.0.1:80/api/v1/auth/jwt/refresh/',
          { refresh }
        )
        // 다시 발급받은 access 토큰으로 로그인
        const newAceess = data.access;
        auth.login(newAceess, refresh);
        console.log('jwt 리프레시')
        // 실패했던 요청을 다시 새로운 access 토큰과 함께 보냄
        originalRequest.headers.Authorization = `Bearer ${newAceess}`;
        return api(originalRequest);
      } catch (error) {
        // 위에서 재로그인 실패시 refresh도 만료된 것 -> 로그아웃 처리
        auth.logout();
        return Promise.reject(error);
      }
    }
    // 이외의 에러는 그대로 발생시킴
    return Promise.reject(error);
  }
)

export default api;