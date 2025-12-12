<template>
  <div class="home">
    <h2>홈</h2>

    <!-- 비로그인 -->
    <div v-if="!auth.isAuthenticated" class="card">
      <p>로그인하면 저장한 루트와 추천 기능을 사용할 수 있어요.</p>
      <div class="actions">
        <RouterLink to="/login" class="btn">로그인</RouterLink>
        <RouterLink to="/signup" class="btn">회원가입</RouterLink>
      </div>
    </div>

    <!-- 로그인 -->
    <div v-else class="card">
      <p v-if="me">안녕하세요, <b>{{ me.username }}</b>님</p>
      <p v-else>유저 정보를 불러오는 중...</p>

      <div class="actions">
        <RouterLink to="/routes/recommend" class="btn">루트 추천 받기</RouterLink>
        <RouterLink to="/mypage" class="btn">마이페이지</RouterLink>
      </div>

      <hr />

      <h3>최근 저장한 루트</h3>

      <p v-if="loading">불러오는 중...</p>
      <p v-else-if="error" class="error">{{ error }}</p>

      <ul v-else-if="routes.length" class="list">
        <li v-for="r in recentRoutes" :key="r.id" @click="detailRoutes(r.id)" class="item">
          <div class="title">{{ r.title }}</div>
          <div class="desc">{{ r.description || '설명 없음' }}</div>
          <div class="meta">#{{ r.id }} · {{ r.created_at.slice(0, 10) }}</div>
        </li>
        <RouterLink to="/mypage?tab=routes" class="btn">저장한 경로 더보기</RouterLink>
      </ul>

      <p v-else>아직 저장된 루트가 없습니다. 추천을 받아보세요!</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import api from '@/api/client'
import { useRouter } from 'vue-router'

const auth = useAuthStore()
const router = useRouter()

const me = ref(null)
const routes = ref([])
// 최근 3개만 자르기
const recentRoutes = computed(() => routes.value.slice(0, 3))
const loading = ref(false)
const error = ref('')


onMounted(async () => {
  if (!auth.isAuthenticated) return

  loading.value = true
  error.value = ''

  try {
    const [meRes, routesRes] = await Promise.all([
      api.get('/auth/me/'),
      api.get('/routes/'),
    ])

    me.value = meRes.data
    routes.value = routesRes.data
  } catch (e) {
    // 여기서 401이면 인터셉터가 refresh 시도 후 실패 시 logout까지 처리함
    // (그래서 HomeView에서는 메시지만 보여줘도 됨)
    error.value = '홈 데이터를 불러오지 못했습니다.'
    console.error(e)
  } finally {
    loading.value = false
  }
})

// 사용자가 루트를 클릭하면 해당 루트 상세조회 페이지로 이동
const detailRoutes = function (routeId) {
  router.push({name: "route-detail", params: { routeId: routeId }})
}

</script>

<style scoped>
.home { max-width: 860px; margin: 0 auto; }
.card { border: 1px solid #eee; border-radius: 12px; padding: 16px; }
.actions { display: flex; gap: 8px; margin-top: 10px; flex-wrap: wrap; }
.btn { border: 1px solid #ddd; padding: 8px 10px; border-radius: 10px; text-decoration: none; color: inherit; }
.list { list-style: none; padding: 0; margin: 12px 0 0; display: flex; flex-direction: column; gap: 10px; }
.item { border: 1px solid #f0f0f0; border-radius: 10px; padding: 12px; cursor: pointer; }
.title { font-weight: 700; }
.desc { color: #555; margin-top: 4px; }
.meta { color: #888; font-size: 12px; margin-top: 6px; }
.error { color: #dc2626; }
</style>
