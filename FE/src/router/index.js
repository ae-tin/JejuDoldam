import LoginView from '@/views/LoginView.vue'
import MyPageView from '@/views/MyPageView.vue'
import HomeView from '@/views/HomeView.vue'
import { createRouter, createWebHistory } from 'vue-router'
import RouteRecommendView from '@/views/RouteRecommendView.vue'

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
  ],
})

router.beforeEach((to, from, next) => {
  const isLoggedIn = !!localStorage.getItem('access')

  // 1) 보호된 페이지인데 로그인 안 됨 → 로그인 페이지로
  if (to.meta.requiresAuth && !isLoggedIn) {
    return next({
      name: 'login',
      query: { next: to.fullPath }, // 나중에 로그인 후 복귀할 때 쓸 수 있음
    })
  }

  // 2) 로그인 페이지로 가려는데 이미 로그인한 상태 → 마이페이지로
  if (to.name === 'login' && isLoggedIn) {
    return next({ name: 'mypage' })
  }

  // 3) 그 외엔 그냥 진행
  return next()
})

export default router
