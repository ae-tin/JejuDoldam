<!--
프론트 최소 이해 세트
1) 페이지 로드시 인증 상태에 따라 /auth/me/, /routes/, /posts/ GET 요청을 트리거하고 카드 클릭 시 라우터 네비게이션 이벤트가 발생한다.
2) /auth/me/, /routes/, /posts/ (GET) API를 호출해 사용자 정보와 최근 루트/게시글을 가져온다.
3) 응답 데이터는 me, routes, posts 상태에 저장되고, 히어로/리스트 카드에 렌더링된다.
4) 흐름: 로그인 여부 확인 → 필요 시 병렬 API 호출 → 상태 저장 → 히어로 섹션과 카드 리스트에 데이터 표시 → 카드 클릭 시 상세 라우팅.
-->
<template>
  <div class="home">
    <section class="hero" :class="auth.isAuthenticated ? 'hero-auth' : 'hero-guest'">
      <div class="hero-content">
        <p class="eyebrow">JEJU ROUTER</p>
        <p v-if="auth.isAuthenticated && me" class="welcome">{{ me.username }}님, 제주 여정을 다시 준비해볼까요?</p>
        <h1 v-if="auth.isAuthenticated">
          다시 떠나볼까요? AI에게 새로운 제주 일정을 맡겨보세요.
        </h1>
        <h1 v-else>AI가 만들어주는 나만의 제주 여행 루트</h1>
        <p class="subtitle" v-if="auth.isAuthenticated">
          자연, 맛집, 액티비티까지. 이전 취향을 기억해 맞춤 루트를 준비했어요.
        </p>
        <p class="subtitle" v-else>
          몇 가지 취향만 알려주면 AI가 일정·동선·장소까지 정리해드릴게요.
        </p>
        <div class="hero-actions">
          <RouterLink class="pill primary" :to="auth.isAuthenticated ? '/routes/recommend' : '/signup'">
            {{ auth.isAuthenticated ? 'AI 루트 추천 받기' : 'AI 추천 무료 체험' }}
          </RouterLink>
          <RouterLink
            v-if="auth.isAuthenticated"
            class="pill ghost"
            to="/routes"
          >
            저장한 루트 보기
          </RouterLink>
          <RouterLink
            v-else
            class="pill ghost"
            to="/login"
          >
            로그인하고 둘러보기
          </RouterLink>
        </div>
        <div v-if="auth.isAuthenticated" class="hero-meta">
          <div class="meta-card">
            <span class="meta-label">최근 루트</span>
            <strong>{{ recentRoutes[0]?.title || '새 루트를 만들어보세요' }}</strong>
            <small v-if="recentRoutes[0]">{{ recentRoutes[0].description || '설명 없음' }}</small>
          </div>
          <div class="meta-card">
            <span class="meta-label">최근 게시글</span>
            <strong>{{ recentPosts[0]?.title || '게시글을 작성해보세요' }}</strong>
            <small v-if="recentPosts[0]">{{ recentPosts[0].content?.slice(0, 30) }}...</small>
          </div>
        </div>
        <p v-if="error" class="error-text">{{ error }}</p>
      </div>
      <div class="hero-visual">
        <div class="floating-card">
          <p class="floating-title">주문진 풍경 감성</p>
          <p class="floating-desc">카페 · 뷰포인트 위주</p>
        </div>
        <div class="floating-card alt">
          <p class="floating-title">3일 완성 힐링 루트</p>
          <p class="floating-desc">바다 산책 · 한라수목원 · 감귤 체험</p>
        </div>
      </div>
    </section>

    <section v-if="auth.isAuthenticated" class="section">
      <div class="section-header">
        <h2>최근 저장한 루트</h2>
        <RouterLink to="/routes" class="link">더 보기</RouterLink>
      </div>
      <div class="card-grid">
        <article
          v-for="route in recentRoutes"
          :key="route.id"
          class="info-card clickable"
          @click="detailRoutes(route.id)"
        >
          <p class="card-label">{{ route.created_at?.slice(0, 10) || '최근' }}</p>
          <h3>{{ route.title }}</h3>
          <p class="card-desc">{{ route.description || '설명 없음' }}</p>
          <p class="card-meta">{{ route.days?.length || 0 }}일 일정 · 장소 {{ route.places_count || route.days?.reduce((acc, d) => acc + (d.places?.length || 0), 0) || 0 }}곳</p>
        </article>
        <p v-if="!loading && !recentRoutes.length" class="empty-text">아직 저장된 루트가 없어요. AI 추천으로 시작해보세요.</p>
      </div>
    </section>

    <section v-if="auth.isAuthenticated" class="section">
      <div class="section-header">
        <h2>최근 작성한 게시글</h2>
        <RouterLink to="/community" class="link">커뮤니티 가기</RouterLink>
      </div>
      <div class="card-grid">
        <article v-for="post in recentPosts" :key="post.id" class="info-card">
          <p class="card-label">{{ post.like_count || 0 }}명이 좋아해요</p>
          <h3>{{ post.title }}</h3>
          <p class="card-desc">{{ post.content?.slice(0, 80) || '내용 없음' }}</p>
          <RouterLink :to="`/community/${post.id}`" class="text-button">게시글 보기 →</RouterLink>
        </article>
        <p v-if="!loading && !recentPosts.length" class="empty-text">커뮤니티에 첫 글을 남겨보세요.</p>
      </div>
    </section>

    <section v-else class="section">
      <div class="section-header">
        <h2>이런 기능을 추천해요</h2>
      </div>
      <div class="feature-grid">
        <div class="feature-card">
          <p class="feature-title">맞춤 일정 생성</p>
          <p class="feature-desc">여행 기간과 취향만 선택하면 AI가 루트를 완성해요.</p>
        </div>
        <div class="feature-card">
          <p class="feature-title">루트 커스터마이징</p>
          <p class="feature-desc">카카오맵 검색으로 장소를 추가하고 순서를 조정하세요.</p>
        </div>
        <div class="feature-card">
          <p class="feature-title">저장 & 공유</p>
          <p class="feature-desc">완성한 루트를 저장하고 커뮤니티에 공유할 수 있어요.</p>
        </div>
        <div class="feature-card">
          <p class="feature-title">인기 루트 둘러보기</p>
          <p class="feature-desc">많이 저장된 제주 인기 루트를 미리 체험해보세요.</p>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/api/client'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()

const me = ref(null)
const routes = ref([])
const posts = ref([])
const loading = ref(false)
const error = ref('')

const recentRoutes = computed(() => routes.value.slice(0, 3))
const recentPosts = computed(() => posts.value.slice(0, 3))

// 최근 루트/게시글을 불러와 홈에 요약 카드로 보여준다.
const fetchHomeData = async () => {
  if (!auth.isAuthenticated) return
  loading.value = true
  error.value = ''
  try {
    const [meRes, routesRes, postsRes] = await Promise.all([
      api.get('/auth/me/'),
      api.get('/routes/'),
      api.get('/posts/'),
    ])
    me.value = meRes.data
    routes.value = routesRes.data
    posts.value = postsRes.data?.results || postsRes.data || []
  } catch (e) {
    error.value = '홈 데이터를 불러오지 못했습니다.'
    console.error(e)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchHomeData()
})

// 사용자가 루트를 클릭하면 해당 루트 상세조회 페이지로 이동
const detailRoutes = function (routeId) {
  router.push({ name: 'route-detail', params: { routeId } })
}
</script>

<style scoped>
.home {
  max-width: 1180px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.hero {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 28px;
  padding: 32px;
  border-radius: 28px;
  background: linear-gradient(140deg, rgba(47, 178, 228, 0.18), rgba(109, 209, 182, 0.2));
  box-shadow: var(--shadow-soft);
}

.hero-auth {
  background: linear-gradient(140deg, rgba(47, 178, 228, 0.16), rgba(255, 255, 255, 0.8));
}

.hero-guest {
  background: linear-gradient(140deg, rgba(47, 178, 228, 0.15), rgba(109, 209, 182, 0.24));
}

.hero-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.eyebrow {
  margin: 0;
  color: var(--color-primary-strong);
  font-weight: 800;
  letter-spacing: 1px;
}

.welcome {
  margin: 0;
  color: var(--color-muted);
  font-weight: 600;
}

h1 {
  margin: 0;
  font-size: 28px;
  line-height: 1.35;
}

.subtitle {
  margin: 0;
  color: var(--color-muted);
}

.hero-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  margin-top: 6px;
}

.pill {
  border: 1px solid transparent;
  border-radius: 999px;
  padding: 10px 16px;
  font-weight: 700;
  cursor: pointer;
  text-decoration: none;
  transition: all 0.2s ease;
}

.pill.primary {
  background: linear-gradient(120deg, var(--color-primary), var(--color-secondary));
  color: #fff;
  box-shadow: var(--shadow-soft);
}

.pill.ghost {
  background: rgba(255, 255, 255, 0.9);
  color: var(--color-text);
  border-color: rgba(15, 23, 42, 0.08);
}

.pill:hover {
  transform: translateY(-1px);
}

.hero-meta {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 12px;
  margin-top: 12px;
}

.meta-card {
  background: rgba(255, 255, 255, 0.7);
  border-radius: 14px;
  padding: 12px 14px;
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.05);
}

.meta-label {
  color: var(--color-muted);
  font-size: 12px;
}

.meta-card strong {
  display: block;
  margin-top: 4px;
}

.meta-card small {
  display: block;
  margin-top: 2px;
  color: var(--color-muted);
}

.error-text {
  margin: 6px 0 0;
  color: #dc2626;
  font-weight: 600;
}

.hero-visual {
  display: grid;
  gap: 12px;
  align-content: start;
}

.floating-card {
  background: #fff;
  border-radius: 16px;
  padding: 16px;
  box-shadow: var(--shadow-soft);
}

.floating-card.alt {
  background: linear-gradient(160deg, rgba(47, 178, 228, 0.1), rgba(109, 209, 182, 0.25));
}

.floating-title {
  margin: 0;
  font-weight: 700;
}

.floating-desc {
  margin: 6px 0 0;
  color: var(--color-muted);
}

.section {
  background: rgba(255, 255, 255, 0.82);
  border-radius: 24px;
  padding: 20px 22px;
  box-shadow: var(--shadow-soft);
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.section h2 {
  margin: 0;
}

.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 14px;
}

.info-card {
  background: var(--color-surface);
  border: 1px solid rgba(15, 23, 42, 0.05);
  border-radius: 16px;
  padding: 16px;
  box-shadow: 0 10px 28px rgba(15, 23, 42, 0.06);
}

.clickable {
  cursor: pointer;
  transition: transform 0.2s ease;
}

.clickable:hover {
  transform: translateY(-2px);
}

.card-label {
  margin: 0;
  color: var(--color-muted);
  font-size: 12px;
}

.card-desc {
  margin: 4px 0 8px;
  color: var(--color-muted);
}

.card-meta {
  margin: 0;
  font-size: 13px;
  color: #111827;
}

.empty-text {
  color: var(--color-muted);
}

.link {
  color: var(--color-primary-strong);
  text-decoration: none;
  font-weight: 700;
}

.text-button {
  text-decoration: none;
  color: var(--color-primary-strong);
  font-weight: 700;
}

.feature-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 12px;
}

.feature-card {
  background: #fff;
  border-radius: 18px;
  padding: 14px 16px;
  border: 1px solid rgba(15, 23, 42, 0.05);
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06);
}

.feature-title {
  margin: 0;
  font-weight: 700;
}

.feature-desc {
  margin: 6px 0 0;
  color: var(--color-muted);
}
</style>
