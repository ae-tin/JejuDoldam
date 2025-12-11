<template>
  <div class="app">
    <header class="app-header">
      <div class="header-left">
        <RouterLink to="/" class="logo">JejuDoldam</RouterLink>
      </div>

      <nav class="header-nav">
        <!-- 로그인 상태일 때만 보이는 메뉴들 -->
        <RouterLink
          v-if="auth.isAuthenticated"
          to="/routes/recommend"
          class="nav-link"
        >
          루트 추천
        </RouterLink>

        <RouterLink
          v-if="auth.isAuthenticated"
          to="/mypage"
          class="nav-link"
        >
          마이페이지
        </RouterLink>

        <!-- 로그인 안 되어 있을 때만 보이는 메뉴 -->
        <RouterLink
          v-if="!auth.isAuthenticated"
          to="/login"
          class="nav-link"
        >
          로그인
        </RouterLink>

        <!-- 로그아웃 버튼 (로그인 상태에서만) -->
        <button
          v-if="auth.isAuthenticated"
          type="button"
          class="nav-link nav-button"
          @click="onLogout"
        >
          로그아웃
        </button>
      </nav>
    </header>

    <main class="app-main">
      <RouterView />
    </main>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()

const onLogout = () => {
  if (!confirm('정말 로그아웃 하시겠어요?')) return

  auth.logout()  // finia에서 토큰 삭제 + isAuthenticated = false
  alert('로그아웃 되었습니다.')
  router.push('/login')
}
</script>

<style scoped>
.app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-header {
  padding: 16px 24px;
  border-bottom: 1px solid #eee;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.logo {
  font-weight: 700;
  text-decoration: none;
  color: #111827;
}

.header-nav {
  display: flex;
  align-items: center;
  gap: 16px;
  font-size: 14px;
}

.nav-link {
  text-decoration: none;
  color: #4b5563;
}

.nav-link.router-link-active {
  font-weight: 600;
  color: #111827;
}

.nav-button {
  border: none;
  background: transparent;
  cursor: pointer;
  padding: 0;
}

.app-main {
  flex: 1;
  padding: 24px;
}
</style>
