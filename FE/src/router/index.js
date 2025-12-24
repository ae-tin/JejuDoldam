import LoginView from '@/views/LoginView.vue'
import MyPageView from '@/views/MyPageView.vue'
import HomeView from '@/views/HomeView.vue'
import { createRouter, createWebHistory } from 'vue-router'
import RouteRecommendView from '@/views/RouteRecommendView.vue'
import { useAuthStore } from '@/stores/auth'
import SignupView from '@/views/SignupView.vue'
import RouteDetailView from '@/views/RouteDetailView.vue'
import RouteRecommendInputView from '@/views/RouteRecommendInputView.vue'
import RouteListView from '@/views/RouteListView.vue'
import CommunityPostListView from '@/views/CommunityPostListView.vue'
import CommunityPostCreateView from '@/views/CommunityPostCreateView.vue'
import CommunityPostDetailView from '@/views/CommunityPostDetailView.vue'
import CommunityPostUpdateView from '@/views/CommunityPostUpdateView.vue'
import KakaoCallback from '@/components/KakaoCallback.vue'


const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/",
      name: "home",
      component: HomeView,
    },
    {
      path: "/login",
      name: "login",
      component: LoginView,
    },
    {
      path: "/mypage",
      name: "mypage",
      component: MyPageView,
      meta: { requiresAuth: true },
    },
    {
      path: "/routes/recommend",
      name: "routes-recommend-input",
      component: RouteRecommendInputView,
      meta: { requiresAuth: true },
    },
    {
      path: "/routes/recommend/results",
      name: "route-recommend-results",
      component: RouteRecommendView,
      meta: { requiresAuth: true },
    },
    {
      path:'/signup',
      name: 'signup',
      component: SignupView,
    },
    {
      path: "/routes/:routeId",
      name: "route-detail",
      component: RouteDetailView,
      meta: { requiresAuth: true },
    },
    {
      path: '/routes',
      name: "routes-list",
      component: RouteListView,
      meta: { requiresAuth: true},
    },
      { 
      path: '/community', 
      name: 'community-list', 
      component: CommunityPostListView, 
      meta: { requiresAuth: true } 
    },
    { 
      path: '/community/new', 
      name: 'community-create', 
      component: CommunityPostCreateView,
      meta: { requiresAuth: true } 
    },
    { 
      path: '/community/:postId', 
      name: 'community-detail', 
      component: CommunityPostDetailView, 
      meta: { requiresAuth: true } 
    },
    {
      path: '/community/:postId/edit',
      name: 'community-edit',
      component: CommunityPostUpdateView,
      meta: { requiresAuth: true }
    },
    {
      path: '/auth/kakao/callback',
      name: 'KakaoCallback',
      component: KakaoCallback,
    },
  ],
})

// ✅ async 추가 (fetchUser 대기용)
router.beforeEach(async (to, from, next) => {
  const auth = useAuthStore()

  // [1] 유저 정보 복구 로직
  // 새로고침 등으로 Pinia state가 비었을 때, 토큰이 있다면 유저 정보를 다시 가져옴
  const token = localStorage.getItem('access')
  if (token && !auth.user) {
    try {
      await auth.fetchUser() // is_setting 포함된 정보 로드
    } catch (error) {
      console.error('사용자 정보 로드 실패', error)
    }
  }

  const isLoggedIn = auth.isAuthenticated

  // [2] 로그인 필요 페이지 접근 제어
  if (to.meta.requiresAuth && !isLoggedIn) {
    return next({ name: 'login', query: { next: to.fullPath } })
  }

  // [3] 로그인 상태에서 로그인/회원가입 페이지 접근 제어
  if ((to.name === 'login' || to.name === 'signup') && isLoggedIn) {
    return next({ name: 'home' })
  }

  // [4] ✅ 추가된 가드: 추천 페이지 접근 시 프로필 설정(is_setting) 확인
  if (to.name === 'routes-recommend-input') {
    // 유저 정보가 있고, is_setting이 false인 경우
    if (auth.user && !auth.user.is_setting) {
      alert('여행 취향 분석을 위해 프로필 설정이 필요합니다.\n설정 페이지로 이동합니다.')
      // 마이페이지의 설정 탭으로 리다이렉트 (query는 MyPageView 구현에 맞춤)
      return next({ name: 'mypage', query: { tab: 'settings' } })
    }
  }

  return next()
})

export default router