<template>
  <div class="app-shell">
    <header class="top-bar">
      <div class="brand" @click="router.push('/')">
        <div class="brand-mark">JEJU</div>
        <div class="brand-name">ROUTER</div>
      </div>

      <nav class="nav-links">
        <RouterLink to="/routes" class="nav-link">루트</RouterLink>
        <RouterLink to="/routes/recommend" class="nav-link">추천 루트</RouterLink>
        <RouterLink to="/community" class="nav-link">커뮤니티</RouterLink>
      </nav>

      <div class="nav-actions">
        <template v-if="!auth.isAuthenticated">
          <RouterLink to="/login" class="ghost-link">로그인</RouterLink>
          <RouterLink to="/signup" class="btn-primary">회원가입</RouterLink>
        </template>
        <template v-else>
          <RouterLink to="/mypage" class="profile-chip">
            <div class="avatar">{{ userInitial }}</div>
            <div>
              <div class="mini-label">JEJU ROUTER</div>
              <strong>내 계정</strong>
            </div>
          </RouterLink>
          <button type="button" class="btn-outline" @click="onLogout">로그아웃</button>
        </template>
      </div>
    </header>

    <main class="page-body">
      <RouterView />
    </main>
  </div>
</template>

<script setup>
/**
 * ✅ 프론트 최소 이해 세트(App.vue)
 * 1) 헤더의 메뉴(루트/추천/커뮤니티) 클릭 → router.push 로 페이지 이동.
 * 2) 로그인 상태에서 로그아웃 버튼 클릭 → 토큰 제거 후 로그인 화면으로 이동.
 * 3) 앱 진입 시 /auth/me/를 호출해 토큰 유효성을 한 번 검증한다.
 * 4) 응답 결과는 auth 스토어의 isAuthenticated 플래그로만 관리하고 뷰 렌더에 사용한다.
 * 5) 요청→검증→상태반영 흐름을 최소화해 헤더 전역 네비게이션에 반영한다.
 */
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import api from '@/api/client'

const router = useRouter()
const auth = useAuthStore()

// 아바타 이니셜 표시용(실제 유저명은 홈에서 불러오므로 기본값 사용)
const userInitial = computed(() => (auth.isAuthenticated ? 'ME' : ''))

const onLogout = () => {
  if (!confirm('정말 로그아웃 하시겠어요?')) return

  auth.logout()
  alert('로그아웃 되었습니다.')
  router.push('/login')
}

// 현재 사용자가 들고 있는 토큰의 유효성을 1회 검사
onMounted(async () => {
  if (!auth.isAuthenticated) return

  try {
    await api.get('/auth/me/')
  } catch (error) {
    // 인터셉터에서 refresh 및 로그아웃 처리됨
  }
})
</script>

<style scoped>
.app-shell {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.top-bar {
  position: sticky;
  top: 0;
  z-index: 10;
  padding: 16px 28px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(14px);
  box-shadow: 0 6px 24px rgba(0, 79, 138, 0.08);
}

.brand {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.brand-mark {
  background: linear-gradient(135deg, var(--color-primary), #65d6ff);
  color: white;
  padding: 10px 12px;
  border-radius: 12px;
  font-weight: 800;
  letter-spacing: 0.02em;
  box-shadow: var(--shadow-soft);
}

.brand-name {
  font-weight: 800;
  letter-spacing: 0.08em;
  color: #0a2540;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 14px;
}

.nav-link {
  text-decoration: none;
  font-weight: 600;
  padding: 10px 12px;
  color: #1f2a44;
  border-radius: 12px;
  transition: background 0.2s ease, color 0.2s ease;
}

.nav-link.router-link-active,
.nav-link:hover {
  background: #eef7ff;
  color: var(--color-primary-strong);
}

.nav-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.ghost-link {
  color: #1f2a44;
  text-decoration: none;
  font-weight: 700;
  padding: 10px 12px;
  border-radius: 12px;
  transition: background 0.2s ease;
}

.ghost-link:hover {
  background: #eef7ff;
}

.profile-chip {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 10px;
  background: #f5f9ff;
  border-radius: 14px;
  border: 1px solid #e2f0ff;
  color: #0a2540;
  text-decoration: none;
}

.avatar {
  width: 38px;
  height: 38px;
  display: grid;
  place-items: center;
  border-radius: 50%;
  background: linear-gradient(135deg, #76d5ff, #5ab2ff);
  color: white;
  font-weight: 800;
  letter-spacing: 0.03em;
}

.mini-label {
  color: var(--color-muted);
  font-size: 12px;
}

.page-body {
  flex: 1;
  padding: 28px 20px 40px;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
}

@media (max-width: 768px) {
  .top-bar {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }

  .nav-links {
    width: 100%;
  }

  .nav-actions {
    width: 100%;
    justify-content: flex-end;
    flex-wrap: wrap;
  }
}
</style>
