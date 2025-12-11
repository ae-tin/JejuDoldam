<template>
  <div class="mypage">
    <h1>마이페이지 (뼈대)</h1>

    <div v-if="loading">불러오는 중...</div>

    <div v-else-if="error" class="error">
      {{ error }}
    </div>

    <div v-else-if="user">
      <p>로그인한 유저 ID: {{ user.id }}</p>
      <p>username: {{ user.username }}</p>
    </div>

    <div v-else>
      <p>로그인 정보가 없습니다.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api/client'  // 이미 만든 axios 인스턴스

const user = ref(null)
const loading = ref(false)
const error = ref('')

onMounted(async () => {
  loading.value = true
  error.value = ''

  try {
    const { data } = await api.get('/auth/me/')
    user.value = data
  } catch (err) {
    console.error(err)
    // 401 같은 경우엔 나중에 로그인 페이지로 리다이렉트 걸어도 됨
    error.value = '유저 정보를 불러오지 못했습니다.'
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.mypage {
  max-width: 600px;
  margin: 0 auto;
}
.error {
  color: red;
}
</style>
