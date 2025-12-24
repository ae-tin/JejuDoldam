// src/stores/auth.js
import { defineStore } from 'pinia'
import api from '@/api/client'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    isAuthenticated: !!localStorage.getItem('access'),
    user: null, // 초기값 null
  }),

  // ✅ [핵심 추가] computed와 같은 역할 (실시간 반응형)
  // state.user가 바뀌면 자동으로 이 값도 바뀝니다.
  getters: {
    // 유저 정보가 로드되지 않았을 때(null) 에러가 나지 않도록 안전하게 처리
    is_setting: (state) => state.user ? state.user.is_setting : false,
  },

  actions: {
    async login(access, refresh) {
      localStorage.setItem('access', access)
      localStorage.setItem('refresh', refresh)
      this.isAuthenticated = true
      
      // 로그인 직후 내 정보(is_setting 포함) 갱신
      await this.fetchUser()
    },

    logout() {
      localStorage.removeItem('access')
      localStorage.removeItem('refresh')
      this.isAuthenticated = false
      this.user = null
    },

    async fetchUser() {
      try {
        const { data } = await api.get('/auth/me/')
        this.user = data
        console.log(data.is_setting)
        // 💡 중요: 여기서 this.user에 값을 넣는 순간,
        // 위에서 정의한 getters의 is_setting 값도 즉시 '실시간'으로 바뀝니다.
      } catch (error) {
        console.error('유저 정보 로드 실패:', error)
        // 에러 시 토큰 만료 가능성 등을 고려해 로그아웃 처리를 할 수도 있음
      }
    },

    // ✅ [추가] 프로필 수정 직후, 프론트엔드 데이터를 강제로 업데이트하는 함수
    // 백엔드에 다시 요청하지 않고 프론트에서만 값을 살짝 바꿔치기할 때 사용 (속도 향상)
    updateUserState(payload) {
      if (this.user) {
        this.user = { ...this.user, ...payload }
      }
    }
  },
})