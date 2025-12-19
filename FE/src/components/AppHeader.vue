<!-- src/components/AppHeader.vue -->
<template>
  <header class="header">
    <nav class="nav">
      <RouterLink class="link" to="/">Home</RouterLink>

      <!-- 로그인 상태에서만 보여줄 메뉴 -->
      <template v-if="isLoggedIn">
        <RouterLink class="link" to="/routes">내 루트</RouterLink>
        <RouterLink class="link" to="/routes/recommend">루트 추천</RouterLink>
        <RouterLink class="link" to="/community">커뮤니티</RouterLink>
        <RouterLink class="link" to="/mypage">마이페이지</RouterLink>

        <button class="btn" @click="handleLogout">로그아웃</button>
      </template>

      <!-- 비로그인 -->
      <template v-else>
        <RouterLink class="link" to="/login">로그인</RouterLink>
        <RouterLink class="link" to="/signup">회원가입</RouterLink>
      </template>
    </nav>
  </header>
</template>

<script setup>
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()

// Pinia 상태를 기반으로 로그인 여부 판단
const isLoggedIn = computed(() => auth.isAuthenticated)

const handleLogout = () => {
  auth.logout()
}
</script>

<style scoped>
.header {
  padding: 14px 18px;
  border-bottom: 1px solid #eee;
}
.nav {
  display: flex;
  gap: 12px;
  align-items: center;
}
.link {
  text-decoration: none;
  color: #222;
}
.btn {
  margin-left: auto;
  border: none;
  padding: 8px 12px;
  cursor: pointer;
  border-radius: 8px;
}
</style>
