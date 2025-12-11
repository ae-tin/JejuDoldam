import LoginView from '@/views/LoginView.vue'
import MyPageView from '@/views/MyPageView.vue'
import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {path:"/", redirect: 'login'},
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
    }
  ],
})

export default router
