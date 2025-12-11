// src/stores/auth.js
import { defineStore } from 'pinia'

export const useAuthStore = defineStore('auth', {
  // 중괄호 내부를 즉시 반환하는 화살표함수 return 생략
  state: () => ({
    // 앱이 처음 켜질 때 localStorage를 보고 초기 로그인 여부 설정
    isAuthenticated: !!localStorage.getItem('access'),
  }),

  actions: {
    // 로그인 성공 시 호출할 함수
    login(access, refresh) {
      localStorage.setItem('access', access)
      localStorage.setItem('refresh', refresh)
      this.isAuthenticated = true
    },

    // 로그아웃 시 호출할 함수
    logout() {
      localStorage.removeItem('access')
      localStorage.removeItem('refresh')
      this.isAuthenticated = false
    },
  },
})
