<!--
프론트 최소 이해 세트
1) 내비게이션 클릭/로그아웃 클릭 이벤트가 발생한다.
2) /auth/me/ GET으로 토큰 유효성을 확인하며 로그아웃 시에는 API 호출 없이 토큰만 제거한다.
3) 토큰 검증 응답은 사용자의 로그인 상태(auth store)에 반영되고, 화면에는 RouterView와 내비게이션 가시성으로 렌더링된다.
4) 흐름: 앱 마운트 → 토큰 존재 시 /auth/me/ 검사 → 실패 시 인터셉터가 로그아웃 → 헤더 메뉴 렌더 → RouterView로 각 페이지 표시.
-->
<template>
  <div class="app">
    <header class="app-header">
      <RouterLink to="/" class="brand">
        <span class="brand-title">JEJU ROUTER</span>
        <span class="brand-sub">제주 AI ROUTER</span>
      </RouterLink>

      <nav class="nav">
        <RouterLink class="nav-link" to="/">홈</RouterLink>
        <RouterLink
          v-if="auth.isAuthenticated"
          class="nav-link"
          to="/routes/recommend"
        >
          루트 추천
        </RouterLink>
        <RouterLink
          v-if="auth.isAuthenticated"
          class="nav-link"
          to="/routes"
        >
          내 루트
        </RouterLink>
        <RouterLink
          v-if="auth.isAuthenticated"
          class="nav-link"
          to="/community"
        >
          커뮤니티
        </RouterLink>
      </nav>

      <div class="header-actions">
        <RouterLink
          v-if="auth.isAuthenticated"
          to="/mypage"
          class="pill ghost"
        >
          마이페이지
        </RouterLink>
        <button
          v-if="auth.isAuthenticated"
          type="button"
          class="pill primary"
          @click="onLogout"
        >
          로그아웃
        </button>
        <template v-else>
          <RouterLink to="/login" class="pill primary">로그인</RouterLink>
          <RouterLink to="/signup" class="pill ghost">회원가입</RouterLink>
        </template>
      </div>
    </header>

    <main class="app-main">
      <RouterView />
    </main>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/api/client'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()

const onLogout = () => {
  if (!confirm('정말 로그아웃 하시겠어요?')) return
  auth.logout()
  alert('로그아웃 되었습니다.')
  router.push('/login')
}

onMounted(async () => {
  if (!auth.isAuthenticated) return
  try {
    await api.get('/auth/me/')
  } catch (error) {
    // 401은 인터셉터에서 처리되므로 여기서는 추가 처리 없음
  }
})
</script>

<style scoped>
.app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-header {
  position: sticky;
  top: 0;
  z-index: 10;
  background: rgba(255, 255, 255, 0.82);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 28px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.04);
  border-bottom: 1px solid rgba(15, 23, 42, 0.05);
}

.brand {
  display: flex;
  flex-direction: column;
  text-decoration: none;
  color: var(--color-text);
  gap: 2px;
}

.brand-title {
  font-weight: 800;
  letter-spacing: 0.4px;
}

.brand-sub {
  font-size: 12px;
  color: var(--color-muted);
}

.nav {
  display: flex;
  align-items: center;
  gap: 16px;
  flex: 1;
  justify-content: center;
}

.nav-link {
  text-decoration: none;
  color: var(--color-muted);
  font-weight: 600;
  padding: 8px 12px;
  border-radius: 12px;
  transition: all 0.2s ease;
}

.nav-link.router-link-active {
  color: var(--color-text);
  background: rgba(47, 178, 228, 0.12);
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.pill {
  border: 1px solid transparent;
  border-radius: 999px;
  padding: 8px 14px;
  font-weight: 700;
  cursor: pointer;
  text-decoration: none;
  transition: all 0.2s ease;
}

.pill.primary {
  background: linear-gradient(120deg, var(--color-primary), var(--color-secondary));
  color: #fff;
  border-color: transparent;
  box-shadow: var(--shadow-soft);
}

.pill.ghost {
  background: rgba(255, 255, 255, 0.8);
  color: var(--color-text);
  border-color: rgba(15, 23, 42, 0.08);
}

.pill:hover {
  transform: translateY(-1px);
  box-shadow: 0 12px 24px rgba(15, 23, 42, 0.08);
}

.app-main {
  flex: 1;
  padding: 32px 20px 48px;
}

@media (max-width: 900px) {
  .app-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .nav {
    width: 100%;
    justify-content: flex-start;
    flex-wrap: wrap;
  }

  .header-actions {
    width: 100%;
    justify-content: flex-start;
    flex-wrap: wrap;
  }
}
</style>
