<template>
  <div class="home" :class="{ auth: auth.isAuthenticated }">
    <!-- Hero 영역 -->
    <section class="hero" :class="auth.isAuthenticated ? 'hero-auth' : 'hero-guest'">
      <div class="hero-copy">
        <p class="eyebrow">JEJU ROUTER</p>
        <div v-if="auth.isAuthenticated && me" class="welcome">안녕하세요, {{ me.username }}님</div>
        <h1 v-if="auth.isAuthenticated">
          다시 떠나볼까요? AI에게 새로운 제주 일정을 맡겨보세요.
        </h1>
        <h1 v-else>AI가 만들어주는 나만의 제주 여행 루트</h1>
        <p class="sub">자연, 먹거리, 휴식까지. 제주에 어울리는 테마로 일정과 장소를 빠르게 완성합니다.</p>
        <div class="hero-actions" v-if="auth.isAuthenticated">
          <RouterLink to="/routes/recommend" class="btn-primary">새 여행 일정 만들기</RouterLink>
          <RouterLink to="/routes" class="btn-outline">마이루트 보러가기</RouterLink>
        </div>
        <div class="hero-actions" v-else>
          <RouterLink to="/routes/recommend" class="btn-primary">서비스 사용 및 루트 만들기</RouterLink>
          <RouterLink to="/login" class="btn-outline">로그인 하기</RouterLink>
        </div>
      </div>

      <div class="hero-panel surface-card" v-if="auth.isAuthenticated">
        <div class="panel-head">최근 저장한 루트</div>
        <div class="panel-body" v-if="loading">불러오는 중...</div>
        <div class="panel-body" v-else-if="error">{{ error }}</div>
        <div class="panel-body" v-else-if="recentRoutes.length">
          <div
            v-for="route in recentRoutes"
            :key="route.id"
            class="panel-route"
            @click="goRouteDetail(route.id)"
          >
            <div class="panel-title">{{ route.title }}</div>
            <p class="panel-desc">{{ route.description || '루트 설명이 준비되어 있어요.' }}</p>
            <div class="panel-meta">{{ formatDate(route.created_at) }}</div>
          </div>
        </div>
        <div class="panel-body" v-else>아직 저장된 루트가 없어요. 첫 루트를 만들어보세요.</div>
      </div>

      <div class="hero-panel surface-card" v-else>
        <div class="panel-head">#맞춤형 제주 루트</div>
        <div class="panel-title">3분 안에 완성되는 일정</div>
        <p class="panel-desc">여행 기간, 동행 타입, 여행 스타일만 선택하면 AI가 알아서 루트를 완성합니다.</p>
        <div class="badge-soft">Day별 볼거리 · 맛집 추천</div>
      </div>
    </section>

    <!-- 로그인 사용자 레이아웃 -->
    <template v-if="auth.isAuthenticated">
      <section class="section">
        <div class="section-title">
          최근 저장한 루트
          <small>AI 추천 루트부터 직접 저장한 동선까지 확인하세요</small>
        </div>
        <div class="card-grid">
          <article
            v-for="route in recentRoutes"
            :key="route.id"
            class="card route-card"
            @click="goRouteDetail(route.id)"
          >
            <div class="card-top">
              <span class="pill">{{ route.days?.length || 1 }}일차</span>
              <span class="pill mute">{{ formatDate(route.created_at) }}</span>
            </div>
            <h3>{{ route.title }}</h3>
            <p>{{ route.description || '루트 설명이 곧 채워질 예정입니다.' }}</p>
            <div class="card-meta">{{ route.places?.length || 0 }}곳의 장소가 포함되어 있어요.</div>
          </article>
          <article class="card empty-card" v-if="!recentRoutes.length">
            <p>아직 저장한 루트가 없습니다.</p>
            <RouterLink to="/routes/recommend" class="btn-primary">루트 추천 받기</RouterLink>
          </article>
        </div>
      </section>

      <section class="section">
        <div class="section-title">
          최근 작성한 게시글
          <small>커뮤니티에서 공유 중인 제주 여행 이야기</small>
        </div>
        <div class="card-grid">
          <article
            v-for="post in recentPosts"
            :key="post.id"
            class="card post-card"
            @click="goPostDetail(post.id)"
          >
            <div class="card-top">
              <span class="pill">{{ post.like_count || 0 }} 좋아요</span>
              <span class="pill mute">{{ post.comment_count || 0 }} 댓글</span>
            </div>
            <h3>{{ post.title }}</h3>
            <p>{{ post.content || '내용을 불러오는 중입니다.' }}</p>
            <div class="card-meta" v-if="post.route">루트 연결됨 · 자세히 보기</div>
          </article>
          <article class="card empty-card" v-if="!recentPosts.length">
            <p>아직 작성한 글이 없습니다.</p>
            <RouterLink to="/community" class="btn-outline">커뮤니티 가기</RouterLink>
          </article>
        </div>
      </section>

      <section class="section two-col">
        <article class="card highlight">
          <div class="section-title">어서 저장해볼까요?</div>
          <p>AI가 추천한 Day/장소를 바로 내 루트에 저장하고 수정할 수 있어요.</p>
          <RouterLink to="/routes/recommend" class="btn-primary">루트 추천 받기</RouterLink>
        </article>

        <article class="card info">
          <div class="section-title">실시간 인기 여행 루트</div>
          <ul>
            <li v-for="route in routes.slice(0, 4)" :key="route.id" @click="goRouteDetail(route.id)">
              <strong>{{ route.title }}</strong>
              <span>{{ route.description || '제주 인기 스팟을 따라가보세요.' }}</span>
            </li>
          </ul>
          <RouterLink to="/routes" class="btn-outline">전체 루트 보기</RouterLink>
        </article>
      </section>
    </template>

    <!-- 비로그인 사용자 레이아웃 -->
    <template v-else>
      <section class="section">
        <div class="section-title">AI 기능으로 추천해요</div>
        <div class="card-grid feature-grid">
          <article v-for="feature in features" :key="feature.title" class="card feature-card">
            <h3>{{ feature.title }}</h3>
            <p>{{ feature.desc }}</p>
          </article>
        </div>
      </section>

      <section class="section">
        <div class="section-title">인기 제주 여행 루트 미리보기</div>
        <div class="card-grid">
          <article v-for="route in popularPreview" :key="route.title" class="card preview-card">
            <h3>{{ route.title }}</h3>
            <p>{{ route.desc }}</p>
            <div class="pill mute">{{ route.tag }}</div>
          </article>
        </div>
        <div class="cta-box">
          <div>
            <div class="eyebrow">루트 추천을 위한 정보만 입력해주세요</div>
            <p class="cta-desc">여행 기간, 동행 타입, 여행 스타일만 있으면 AI가 알아서 장소를 채워요.</p>
          </div>
          <RouterLink to="/routes/recommend" class="btn-primary">루트 무료 추천 받기</RouterLink>
        </div>
      </section>
    </template>
  </div>
</template>

<script setup>
/**
 * ✅ 프론트 최소 이해 세트(HomeView)
 * 1) 앱 진입 시 로그인 상태라면 /auth/me/, /routes/, /posts/를 병렬 호출해 홈 데이터로 채운다.
 * 2) CTA 버튼 클릭 시 router.push 로 추천/루트/로그인 페이지로 이동한다.
 * 3) 응답 데이터는 me, routes, posts ref에 저장하고 컴포넌트 카드에 렌더링한다.
 * 4) 요청 실패 시 error 메시지를 화면에 표시하고 기본 안내 카드를 유지한다.
 * 5) 클릭 이벤트로 루트·게시글 상세로 이동하는 흐름을 단순화해 메인 홈 UX를 제공한다.
 */
import { ref, onMounted, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import api from '@/api/client'

const auth = useAuthStore()
const router = useRouter()

const me = ref(null)
const routes = ref([])
const posts = ref([])
const loading = ref(false)
const error = ref('')

const recentRoutes = computed(() => routes.value.slice(0, 3))
const recentPosts = computed(() => posts.value.slice(0, 3))

const features = [
  { title: '맞춤 여행 스타일 추천', desc: '취향만 알려주시면 가장 어울리는 테마로 코스를 제안해요.' },
  { title: '루트 커스터마이즈', desc: '추천 결과를 바로 편집해서 나만의 루트를 완성하세요.' },
  { title: '저장·공유까지 한 번에', desc: '마음에 드는 루트를 저장하고 커뮤니티에서 바로 공유할 수 있어요.' },
  { title: '지도 기반 장소 탐색', desc: '카카오맵으로 주변 맛집과 명소를 빠르게 찾아볼 수 있어요.' },
]

const popularPreview = [
  { title: '프리미엄 가을 제주 2박 3일', desc: '쇠소깍과 혼인지 등 자연을 담은 프리미엄 여행', tag: '2박 3일 | 자연·감성' },
  { title: '자연 & 문화 스팟 한 번에', desc: '일몰 명소부터 올레길까지 여유롭게 돌아보는 루트', tag: '힐링 | 올레길' },
  { title: '제주 인기 해변 맛집 투어', desc: '해안도로 따라 맛집과 카페를 잇는 미식 여행', tag: '맛집 | 바다 전망' },
  { title: '가족과 함께하는 서귀포 여행', desc: '아이와 함께하기 좋은 체험 중심 일정', tag: '가족 | 체험' },
]

const fetchHome = async () => {
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
    routes.value = routesRes.data || []

    const postData = postsRes.data
    posts.value = Array.isArray(postData?.results) ? postData.results : postData || []
  } catch (err) {
    error.value = '홈 정보를 불러오지 못했어요. 잠시 후 다시 시도해주세요.'
    console.error(err)
  } finally {
    loading.value = false
  }
}

onMounted(fetchHome)

const goRouteDetail = (routeId) => {
  router.push({ name: 'route-detail', params: { routeId } })
}

const goPostDetail = (postId) => {
  router.push({ name: 'community-detail', params: { postId } })
}

// YYYY-MM-DD 형태로 자르기 위한 헬퍼
const formatDate = (value) => (value ? String(value).slice(0, 10) : '기록 없음')

</script>

<style scoped>
.home {
  display: flex;
  flex-direction: column;
  gap: 22px;
}

.hero {
  display: grid;
  grid-template-columns: 1.6fr 1fr;
  gap: 18px;
  align-items: stretch;
}

.hero-auth {
  background: linear-gradient(135deg, rgba(58, 161, 255, 0.18), rgba(101, 214, 255, 0.24));
  border-radius: var(--radius-lg);
  padding: 28px;
  box-shadow: var(--shadow-soft);
}

.hero-guest {
  background: linear-gradient(135deg, rgba(58, 161, 255, 0.16), rgba(190, 238, 255, 0.32));
  border-radius: var(--radius-lg);
  padding: 28px;
  box-shadow: var(--shadow-soft);
}

.hero-copy h1 {
  margin: 10px 0 12px;
  font-size: 28px;
  letter-spacing: -0.02em;
}

.sub {
  color: #1f2a44;
  line-height: 1.6;
  margin-bottom: 16px;
}

.eyebrow {
  text-transform: uppercase;
  font-weight: 800;
  letter-spacing: 0.06em;
  color: #0f5fa8;
}

.welcome {
  margin: 6px 0 4px;
  font-weight: 700;
  color: #0a2540;
}

.hero-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.hero-panel {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.panel-head {
  color: var(--color-muted);
  font-weight: 700;
}

.panel-body {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.panel-title {
  font-weight: 800;
  font-size: 20px;
  margin-bottom: 6px;
}

.panel-desc {
  margin: 4px 0 6px;
  color: #42536b;
  line-height: 1.5;
}

.panel-meta {
  color: var(--color-muted);
  font-size: 13px;
}

.panel-route {
  padding: 12px;
  border-radius: 12px;
  background: #f7fbff;
  border: 1px solid #e6f2ff;
  cursor: pointer;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.panel-route:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 32px rgba(58, 161, 255, 0.12);
}

.section {
  background: rgba(255, 255, 255, 0.74);
  border-radius: var(--radius-lg);
  padding: 18px;
  box-shadow: 0 10px 36px rgba(0, 92, 156, 0.08);
}

.card {
  background: white;
  border-radius: 16px;
  padding: 14px;
  border: 1px solid #e5f0ff;
  box-shadow: 0 8px 30px rgba(0, 73, 125, 0.08);
  cursor: pointer;
  transition: transform 0.15s ease, box-shadow 0.2s ease;
}

.card:hover {
  transform: translateY(-2px);
  box-shadow: 0 14px 40px rgba(58, 161, 255, 0.18);
}

.card h3 {
  margin: 8px 0;
}

.card p {
  margin: 0;
  color: #1f2a44;
  line-height: 1.5;
}

.card-top {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.pill {
  display: inline-block;
  padding: 6px 10px;
  border-radius: 999px;
  background: #eef7ff;
  color: #0b518d;
  font-weight: 700;
  font-size: 12px;
}

.pill.mute {
  background: #f7fafc;
  color: #4b5563;
}

.card-meta {
  margin-top: 10px;
  color: var(--color-muted);
  font-size: 13px;
}

.empty-card {
  text-align: center;
  display: grid;
  place-items: center;
  gap: 10px;
  cursor: default;
}

.post-card {
  cursor: pointer;
}

.two-col {
  display: grid;
  grid-template-columns: 1.2fr 1fr;
  gap: 14px;
}

.highlight {
  background: linear-gradient(135deg, rgba(58, 161, 255, 0.14), rgba(101, 214, 255, 0.28));
}

.info ul {
  list-style: none;
  padding: 0;
  margin: 0 0 12px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.info li {
  padding: 10px 12px;
  border-radius: 12px;
  background: #f8fbff;
  border: 1px solid #e3f1ff;
  cursor: pointer;
}

.info li strong {
  display: block;
  margin-bottom: 4px;
}

.feature-card {
  background: #f7fbff;
}

.feature-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 14px 38px rgba(58, 161, 255, 0.2);
}

.feature-grid .card {
  cursor: default;
}

.preview-card {
  cursor: default;
}

.cta-box {
  margin-top: 16px;
  padding: 18px;
  border-radius: 16px;
  background: linear-gradient(135deg, rgba(58, 161, 255, 0.12), rgba(187, 235, 255, 0.32));
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.cta-desc {
  margin: 6px 0 0;
  color: #1f2a44;
}

@media (max-width: 960px) {
  .hero {
    grid-template-columns: 1fr;
  }

  .two-col {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .hero-actions {
    flex-direction: column;
    align-items: stretch;
  }

  .card-grid {
    grid-template-columns: 1fr;
  }
}
</style>
