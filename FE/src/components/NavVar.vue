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

// 스크롤 감지 로직 (네브바 배경 투명 -> 흰색 변경용)
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
.navbar {
  position: fixed;
  top: 0; left: 0; right: 0;
  height: 60px;
  background-color: transparent; /* 초기엔 투명 */
  border-bottom: 1px solid transparent;
  z-index: 1000;
  display: flex;
  justify-content: center;
  transition: all 0.3s ease-in-out;
}

/* 스크롤 되었을 때 스타일 */
.navbar.scrolled {
  background-color: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(5px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
  border-bottom: 1px solid rgba(0,0,0,0.05);
}

.nav-content {
  width: 100%; max-width: 1024px;
  display: flex; justify-content: space-between; align-items: center;
  padding: 0 20px;
}

.logo { 
  font-weight: 800; font-size: 1.4rem; color: #2cb398; 
  text-decoration: none; cursor: pointer; 
}

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
  .nav-actions { display: none; /* 모바일 메뉴는 생략 or 햄버거 메뉴로 대체 */ }
}
</style>