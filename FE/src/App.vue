<template>
  <div class="app">
    <header class="app-header">
      <nav class="nav">
        <!-- 왼쪽: 로고(메인으로 이동) -->
        <RouterLink to="/" class="logo">
          JejuDoldam
        </RouterLink>

        <!-- 오른쪽: 로그인 상태에 따라 메뉴 변경 -->
        <div class="nav-right">
          <!-- 로그인 안 했을 때 -->
          <template v-if="!isLoggedIn">
            <RouterLink to="/login" class="nav-link">로그인</RouterLink>
            <!-- 회원가입은 나중에 붙이면됨 -->
            <!-- <RouterLink to="/signup" class="nav-link">회원가입</RouterLink> -->
          </template>

          <!-- 로그인 했을 때 -->
          <template v-else>
            <RouterLink to="/mypage" class="nav-link">마이페이지</RouterLink>
            <button type="button" class="nav-link" @click="handleLogout">
              로그아웃
            </button>
          </template>
        </div>
      </nav>
    </header>

    <main class="app-main">
      <RouterView />
    </main>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter, RouterLink, RouterView } from 'vue-router'

const router = useRouter()

// 뼈대용 로그인 여부 판단: access 토큰 존재 여부로만 체크
const isLoggedIn = computed(() => {
  return !!localStorage.getItem('access')
})

// 로그아웃: 토큰 제거 + 로그인 페이지로 이동
const handleLogout = () => {
  localStorage.removeItem('access')
  localStorage.removeItem('refresh')

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

/* 기존 헤더 스타일 + nav 레이아웃 추가 */
.app-header {
  padding: 16px 24px;
  border-bottom: 1px solid #eee;
  font-weight: 600;
}

.nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.logo {
  text-decoration: none;
  font-size: 20px;
  font-weight: 700;
  color: #222;
}

/* 오른쪽 메뉴 영역 */
.nav-right {
  display: flex;
  gap: 12px;
}

/* 링크 / 버튼 공통 스타일 */
.nav-link {
  border: none;
  background: none;
  padding: 4px 8px;
  cursor: pointer;
  font-size: 14px;
  text-decoration: none;
  color: #333;
}

.nav-link:hover {
  text-decoration: underline;
}

.app-main {
  flex: 1;
  padding: 24px;
}
</style>
