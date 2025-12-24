<script setup>
import { onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import axios from 'axios'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

onMounted(async () => {
  const code = route.query.code // 1. URL에서 인가 코드 추출

  if (code) {
    try {
      // 2. 백엔드로 인가 코드 전송 (백엔드가 다 알아서 함)
      const response = await axios.post('http://127.0.0.1:8000/api/v1/auth/kakao/', {
        code: code
      })

      // 3. 백엔드 응답(JWT + is_setting) 처리
      const { access, refresh, is_setting } = response.data
      
      // Pinia 스토어 액션 호출 (이전에 정의하신 login 함수 활용)
      authStore.login(access, refresh)
      
      router.push({ name: 'home' })

    } catch (error) {
      console.error(error)
      alert("로그인 실패")
      router.push('/login')
    }
  }
})
</script>