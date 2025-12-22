// src/api/client.js
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

/**
 * ✅ baseURL을 "환경변수 → 없으면 기본값(/api/v1)" 순서로 사용
 * - 개발(dev): VITE_API_BASE_URL을 http://127.0.0.1:8000/api/v1 로 둘 수도 있고
 * - 운영(prod): VITE_API_BASE_URL 없이 /api/v1 로도 동작하게 만들 수 있음
 */
const BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1'

/**
 * ✅ 실제 API 호출용 axios 인스턴스
 * - 모든 요청이 BASE_URL 기준으로 나감
 */
const api = axios.create({
  baseURL: BASE_URL,
})

/**
 * ✅ refresh 전용 axios 인스턴스 (중요)
 * - api 인스턴스를 refresh에 쓰면 "인터셉터 → 401 → refresh → 또 인터셉터…" 같은 꼬임이 날 수 있어서
 *   refresh는 별도 인스턴스로 분리하는 게 안전함
 */
const refreshClient = axios.create({
  baseURL: BASE_URL,
})

/**
 * ✅ [요청 인터셉터]
 * 요청이 서버로 나가기 직전에 Authorization 헤더에 access 토큰을 붙임
 *
 * 요청 → (여기서 토큰 붙임) → 서버 처리 → 응답
 */
api.interceptors.request.use((config) => {
  const access = localStorage.getItem('access')

  // headers가 비어있을 수 있으니 안전하게 초기화
  config.headers = config.headers || {}

  if (access) {
    config.headers.Authorization = `Bearer ${access}`
  }

  return config
})

/**
 * ✅ [응답 인터셉터]
 * 응답이 돌아오는 순간 검사해서, 401이면 refresh로 access 재발급 후 원래 요청을 재시도
 *
 * 응답(401) → refresh 요청 → 새 access 저장 → 실패했던 요청 재시도 → 최종 응답
 */
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const auth = useAuthStore()
    const originalRequest = error.config

    // 401 + 아직 재시도 안한 요청만 처리 (무한루프 방지)
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      const refresh = localStorage.getItem('refresh')

      // refresh 토큰이 없으면 더 이상 갱신 불가 → 로그아웃
      if (!refresh) {
        auth.logout()
        return Promise.reject(error)
      }

      try {
        /**
         * ✅ refresh로 access 재발급 요청
         * BASE_URL이 /api/v1 이면 → /api/v1/auth/jwt/refresh/
         * BASE_URL이 http://127.0.0.1:8000/api/v1 이면 → 해당 주소로 요청
         */
        const { data } = await refreshClient.post('/auth/jwt/refresh/', { refresh })

        const newAccess = data.access

        // ✅ 새 access 저장 (auth.login이 저장해주더라도, 여기서 한 번 더 보장해두면 안전)
        localStorage.setItem('access', newAccess)

        // ✅ 너의 기존 로직 유지: store에 로그인 상태 업데이트
        auth.login(newAccess, refresh)

        // ✅ 실패했던 요청을 새 access로 다시 시도
        originalRequest.headers = originalRequest.headers || {}
        originalRequest.headers.Authorization = `Bearer ${newAccess}`

        return api(originalRequest)
      } catch (refreshError) {
        // refresh도 실패 = refresh 만료 가능성 큼 → 로그아웃
        auth.logout()
        return Promise.reject(refreshError)
      }
    }

    return Promise.reject(error)
  }
)

export default api
