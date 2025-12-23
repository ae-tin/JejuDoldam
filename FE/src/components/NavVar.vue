<template>
  <nav class="navbar" :class="{ scrolled: isScrolled }">
    <div class="nav-content">
      <RouterLink to="/" class="logo">JejuDoldam</RouterLink>
      
      <div v-if="!auth.isAuthenticated" class="nav-actions">
        <RouterLink to="/login" class="nav-link">로그인</RouterLink>
        <RouterLink to="/signup" class="nav-btn primary">회원가입</RouterLink>
      </div>

      <div v-else class="nav-actions">
        <span class="user-greeting" v-if="auth.user">{{ auth.user.username }}님</span>
        <RouterLink to="/mypage" class="nav-link">마이페이지</RouterLink>
        <button @click="handleLogout" class="nav-link logout-btn">로그아웃</button>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()
const isScrolled = ref(false)

// 스크롤 감지 로직
const handleScroll = () => {
  isScrolled.value = window.scrollY > 30
}

const handleLogout = () => {
  auth.logout()
  router.push('/login')
}

onMounted(() => {
  window.addEventListener('scroll', handleScroll)
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})
</script>

<style scoped>
/* 네브바 전체 컨테이너 */
.navbar {
  position: fixed;
  top: 0; left: 0; right: 0;
  height: 60px;
  background-color: transparent;
  border-bottom: 1px solid transparent;
  z-index: 1000;
  display: flex;
  justify-content: center;
  transition: all 0.3s ease-in-out;
}

/* 스크롤 시 스타일 변경 */
.navbar.scrolled {
  background-color: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(5px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
  border-bottom: 1px solid rgba(0,0,0,0.05);
}

/* [수정됨] 내부 컨텐츠 영역 
  - max-width: 1024px; 제거 -> 화면 전체 너비 사용
  - justify-content: space-between; -> 요소들을 양쪽 끝으로 밀어냄
*/
.nav-content {
  width: 100%;
  /* max-width: 1024px;  <-- 이 부분을 삭제하여 너비 제한을 풀었습니다 */
  display: flex; 
  justify-content: space-between; /* 양쪽 끝 정렬 */
  align-items: center;
  padding: 0 40px; /* 양쪽 여백을 조금 더 넉넉하게 줌 (20px -> 40px) */
}

/* 로고 스타일 */
.logo { 
  font-weight: 800; font-size: 1.4rem; color: #2cb398; 
  text-decoration: none; cursor: pointer; 
}

/* 오른쪽 메뉴 그룹 */
.nav-actions { display: flex; align-items: center; gap: 20px; }

.nav-link { 
  text-decoration: none; color: #666; font-size: 0.95rem; cursor: pointer; 
  border: none; background: none; padding: 0;
}
.nav-link:hover { color: #2cb398; }

.nav-btn.primary {
  background-color: #2cb398; color: white; padding: 8px 16px; 
  border-radius: 6px; text-decoration: none; font-weight: bold; font-size: 0.9rem;
  transition: background-color 0.2s;
}
.nav-btn.primary:hover { background-color: #249e85; }

.user-greeting { font-size: 0.9rem; font-weight: bold; color: #333; }

/* 모바일 반응형 */
@media (max-width: 768px) {
  .nav-content { padding: 0 20px; } /* 모바일에서는 여백 줄임 */
  .nav-actions { display: none; }
}
</style>