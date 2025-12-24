// src/stores/auth.js
import { defineStore } from 'pinia'
import api from '@/api/client' // API 요청을 위해 axios 인스턴스 import

export const useAuthStore = defineStore('auth', {
  state: () => ({
    // 앱이 처음 켜질 때 localStorage를 보고 초기 로그인 여부 설정
    isAuthenticated: !!localStorage.getItem('access'),
    // ✅ [추가] 유저 정보를 담을 변수 (is_setting 등 포함)
    user: null, 
  }),

  actions: {
    // 로그인 성공 시 호출할 함수
    // ✅ [수정] async 키워드 추가 (fetchUser 비동기 호출 위함)
    async login(access, refresh) {
      localStorage.setItem('access', access)
      localStorage.setItem('refresh', refresh)
      this.isAuthenticated = true

      // ✅ [추가] 로그인 직후 유저 정보(is_setting)를 가져와서 저장
      await this.fetchUser()
    },

    // 로그아웃 시 호출할 함수
    logout() {
      localStorage.removeItem('access')
      localStorage.removeItem('refresh')
      this.isAuthenticated = false
      this.user = null // ✅ [추가] 로그아웃 시 유저 정보 초기화
    },

    // ✅ [추가] 내 정보 가져오기 액션
    async fetchUser() {
      try {
        // api/v1/auth/me/ 로 GET 요청 (baseURL 설정에 따라 경로 조절)
        const { data } = await api.get('/auth/me/')
        this.user = data // 받아온 데이터(is_setting 포함)를 state에 저장
      } catch (error) {
        console.error('유저 정보 로드 실패:', error)
      }
    },
  },
})