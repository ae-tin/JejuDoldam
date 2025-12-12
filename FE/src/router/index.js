import LoginView from '@/views/LoginView.vue'
import MyPageView from '@/views/MyPageView.vue'
import HomeView from '@/views/HomeView.vue'
import { createRouter, createWebHistory } from 'vue-router'
import RouteRecommendView from '@/views/RouteRecommendView.vue'
import { useAuthStore } from '@/stores/auth'
import SignupView from '@/views/SignupView.vue'

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
      name: "routes-recommend",
      component: RouteRecommendView,
      meta: { requiresAuth: true },
    },
    {
      path:'/signup',
      name: 'signup',
      component: SignupView,
    },
  ],
})

router.beforeEach((to, from, next) => {
  const auth = useAuthStore()
  const isLoggedIn = auth.isAuthenticated

  // 1) 로그인이 필요한데 안 되어 있으면 → 로그인 페이지로 (next 파라미터 포함)
  if (to.meta.requiresAuth && !isLoggedIn) {
    return next({ name: 'login', query: { next: to.fullPath } })
  }

  // 2) 이미 로그인 상태인데 /login 으로 가려 하면 → 홈으로
  if (to.name === 'login' && isLoggedIn) {
    return next({ name: 'home' })
  }

  return next()
})

export default router
