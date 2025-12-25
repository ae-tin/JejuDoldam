<template>
  <div class="triple-container">
    <NavVar />

    <div v-if="!auth.isAuthenticated" class="landing-view">
      <header class="hero-section">
        <div class="hero-bg"></div>
        <div class="hero-text fade-element">
          <h1>여행의 모든 것,<br>AI가 설계해 드립니다</h1>
          <p>로그인하고 나만의 맞춤형 루트를 저장하세요.</p>
          <div class="cta-group">
            <button class="cta-button" @click="router.push('/login')">
              로그인하고 시작하기
            </button>
          </div>
        </div>
      </header>

      <section class="features-section fade-element delay-200">
        <div class="feature-item">
          <div class="icon">🤖</div><h3>AI 맞춤 추천</h3><p>클릭 몇 번으로 최적의 동선 완성</p>
        </div>
        <div class="feature-item">
          <div class="icon">📍</div><h3>검증된 장소</h3><p>카카오맵 기반의 정확한 정보</p>
        </div>
        <div class="feature-item">
          <div class="icon">📂</div><h3>루트 저장</h3><p>언제든 다시 꺼내보는 여행 계획</p>
        </div>
      </section>
    </div>

    <div v-else class="dashboard-view">
      <div class="content-wrapper">
        <section class="dashboard-header fade-element">
          <h2 v-if="me">반가워요, <b>{{ me.username }}</b>님! 👋<br>어디로 떠나볼까요?</h2>
          <h2 v-else>여행 준비를 시작해볼까요?</h2>
          
          <div class="action-cards">
            <div class="action-card primary" @click="router.push('/routes/recommend')">
              <div class="card-icon">✈️</div>
              <div class="card-text">
                <h3>새로운 루트 만들기</h3>
                <p>AI가 취향에 딱 맞는 코스를 짜드려요</p>
              </div>
            </div>
            <div class="action-card" @click="router.push('/community')">
              <div class="card-icon">💬</div>
              <div class="card-text">
                <h3>커뮤니티</h3>
                <p>다른 여행자들의 꿀팁 구경하기</p>
              </div>
            </div>
          </div>
        </section>

        <hr class="divider fade-element delay-100" />

        <section class="recent-routes-section fade-element delay-200">
          <div class="section-header">
            <h3>최근 저장한 루트</h3>
            <RouterLink to="/mypage?tab=routes" class="more-link">전체보기 ></RouterLink>
          </div>

          <div v-if="loading" class="status-msg">
            <div class="spinner"></div> 루트 정보를 불러오고 있어요...
          </div>
          <div v-else-if="error" class="status-msg error">{{ error }}</div>

          <div v-else-if="routes.length" class="route-grid">
            <div v-for="r in recentRoutes" :key="r.id" class="route-card" @click="detailRoutes(r.id)">
              
              <div
                class="route-card-img"
                :class="{ 'recommend-gradient': !r.photo_url }"
                :style="r.photo_url ? bgStyle(r.photo_url) : {}"
              >
                <span class="route-tag">Saved</span>
              </div>
              
              <div class="route-card-body">
                <h4 class="route-title">{{ r.title }}</h4>
                <p class="route-desc">{{ r.description || '설명 없는 여행'}}</p>
                <div class="route-meta">
                  <span>#{{ r.id }}</span>
                  <span>{{ r.created_at.slice(0, 10) }}</span>
                </div>
              </div>
            </div>
          </div>

          <div v-else class="empty-state">
            <p>아직 저장된 여행이 없네요 텅 비었어요! 🏝️</p>
            <button class="btn-outline" @click="router.push('/routes/recommend')">
              첫 번째 여행 계획하기
            </button>
          </div>
        </section>

        <hr class="divider fade-element delay-200" />

        <section class="recommend-section fade-element delay-200">
          <div class="section-header">
            <h3>✈️ 지금 떠나기 좋은 여행</h3>
          </div>

          <div class="route-grid">
            <div 
              v-for="(r, idx) in recommendedRoutes" 
              :key="r.id" 
              class="route-card"
              @click="selectRecommendedRoute(idx)"
            >
            
              <div
                class="route-card-img"
                :class="{ 'recommend-gradient': !r.places?.[0]?.photo_url }"
                :style="r.places?.[0]?.photo_url ? bgStyle(r.places[0].photo_url) : {}"
              >
                <span v-if="r.is_hot" class="route-tag hot">HOT 🔥</span>
                <span v-else class="route-tag recommend">AI Pick</span>
              </div>
              
              <div class="route-card-body">
                <h4 class="route-title">{{ r.title }}</h4>
                <p class="route-desc">{{ r.description }}</p>
              </div>
            </div>
          </div>
        </section>

        <hr class="divider fade-element delay-200" />

        <section class="recommend-section fade-element delay-200">
          <div class="section-header">
            <h3>🎈 이런 여행지는 어때요!?</h3>
          </div>

          <ul class="place-list">
            <li
              v-for="p in recommendedPlaces"
              :key="p.id"
              class="place-list-item"
              @click="openPlace(p.PLACE_URL)"
            >
              <span class="route-title">{{ p.VISIT_AREA_NM }}</span>
              <span class="place-arrow">›</span>
            </li>
          </ul>
        </section>


        <!-- <section class="recommend-section fade-element delay-200">
          <div class="section-header">
            <h3>이런 여행지는 어때요?</h3>
          </div>

          <div class="route-grid">
            <div 
              v-for="(p, idx) in recommendedPlaces" 
              :key="p.id" 
              class="route-card"
              @click="selectRecommendedRoute(idx)"
            >
            
              <div
                class="route-card-img"
                :class="{ 'recommend-gradient': !p.photo_url }"
                :style="p.photo_url ? bgStyle(p.photo_url) : {}"
              >
                <span v-if="p.is_hot" class="route-tag hot">HOT 🔥</span>
                <span v-else class="route-tag recommend">AI Pick</span>
              </div>
              
              <div class="route-card-body">
                <h4 class="route-title">{{ p.VISIT_AREA_NM }}</h4>
                
              </div>
            </div>
          </div>
        </section> -->
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, nextTick } from 'vue'
import { useAuthStore } from '@/stores/auth'
import api from '@/api/client'
import { useRouter } from 'vue-router'
import NavVar from '@/components/NavVar.vue'

const auth = useAuthStore()
const router = useRouter()

const me = ref(null)
const routes = ref([])
const recentRoutes = computed(() => routes.value.slice(0, 3))
const loading = ref(false)
const error = ref('')
const recommendedRoutes = ref([])
const recommendedPlaces = ref([])

let observer = null

// 상세 페이지 이동 (저장된 루트용)
const detailRoutes = (routeId) => {
  router.push({ name: "route-detail", params: { routeId: routeId } })
}

const openPlace = (url) => {
  if (!url) return
  window.open(url, "_blank")
}


// ✅ [수정됨] 추천 루트 클릭 시 전체 리스트와 선택된 인덱스를 넘깁니다.
const selectRecommendedRoute = (index) => {
  router.push({
    path: '/routes/recommend/results',
    state: { 
      // 3개 루트 정보 전체를 넘겨야 탭이 정상적으로 나옵니다.
      passedRoutes: JSON.parse(JSON.stringify(recommendedRoutes.value)), 
      // 사용자가 클릭한 루트가 몇 번째인지 함께 전달
      initialIndex: index 
    }
  })
}

async function fetchRecommendedRoutes() {
  try {
    const { data } = await api.get('/routes/recommend/')
    recommendedRoutes.value = data || []
  } catch (e) {
    console.error('추천 루트 로딩 실패', e)
    recommendedRoutes.value = []
  }
}

async function fetchRecommendedPlaces() {
  try {
    const { data } = await api.get('/routes/recommend/places/')
    recommendedPlaces.value = data || []
  } catch (e) {
    console.error('추천 장소 로딩 실패', e)
    recommendedPlaces.value = []
  }
}

const bgStyle = (url) => ({
  backgroundImage: `url(${url})`,
  backgroundSize: "cover",
  backgroundPosition: "center",
  backgroundRepeat: "no-repeat",
})

onMounted(async () => {

  await nextTick()
  // 기존 observer 로직 유지
  observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible')
      }
    })
  }, { threshold: 0.1 })

  document.querySelectorAll('.fade-element').forEach(el => observer.observe(el))

  if (auth.isAuthenticated) {
    loading.value = true
    try {
      const [meRes, routesRes] = await Promise.all([
        api.get('/auth/me/'),
        api.get('/routes/'),
      ])

      me.value = meRes.data
      const routesData = routesRes.data

      for (const route of routesData) {
        const photoRes = await api.get('/routes/photo/', {
          params: { route_id: route.id }
        })
        route.photo_url = photoRes.data?.photo_url || null
      }
      routes.value = routesData

    } catch (e) {
      console.error(e)
      error.value = '데이터를 불러오지 못했습니다.'
    } finally {
      loading.value = false
    }
  }

  fetchRecommendedRoutes()
  fetchRecommendedPlaces()
})

onUnmounted(() => {
  if (observer) observer.disconnect()
})
</script>

<style scoped>
/* 기존 스타일 유지 */
.triple-container {
  font-family: -apple-system, BlinkMacSystemFont, "Pretendard", Roboto, sans-serif;
  color: #333;
  padding-top: 60px;
  min-height: 100vh;
}
.fade-element { opacity: 0; transform: translateY(20px); transition: 0.8s ease; }
.fade-element.visible { opacity: 1; transform: translateY(0); }
.delay-100 { transition-delay: 0.1s; }
.delay-200 { transition-delay: 0.2s; }

.hero-section {
  position: relative; height: 70vh;
  display: flex; align-items: center; justify-content: center; text-align: center;
  background-image: url('https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1000&q=80');
  background-size: cover; background-position: center;
}
.hero-bg { position: absolute; inset: 0; background: rgba(0,0,0,0.35); }
.hero-text { position: relative; z-index: 1; color: white; }
.hero-text h1 { font-size: 3rem; margin-bottom: 20px; font-weight: 800; line-height: 1.2; }
.hero-text p { font-size: 1.2rem; margin-bottom: 30px; opacity: 0.9; }
.cta-button {
  background: #2cb398; color: white; padding: 15px 40px; border-radius: 30px; border: none;
  font-size: 1.1rem; font-weight: bold; cursor: pointer; transition: transform 0.2s;
}
.cta-button:hover { transform: scale(1.05); }

.features-section {
  display: flex; justify-content: center; gap: 40px; padding: 60px 20px; background: #fff;
  flex-wrap: wrap; text-align: center;
}
.feature-item { max-width: 250px; }
.feature-item .icon { font-size: 2.5rem; margin-bottom: 10px; }
.feature-item h3 { font-size: 1.2rem; margin-bottom: 8px; color: #333; }
.feature-item p { color: #888; line-height: 1.5; font-size: 0.95rem; }

.dashboard-view { background-color: #f9f9f9; min-height: calc(100vh - 60px); padding: 40px 20px; }
.content-wrapper { max-width: 860px; margin: 0 auto; }

.dashboard-header { margin-bottom: 40px; }
.dashboard-header h2 { font-size: 2rem; margin-bottom: 30px; line-height: 1.3; color: #111; }
.dashboard-header b { color: #2cb398; }

.action-cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; }
.action-card {
  background: white; border-radius: 16px; padding: 24px; cursor: pointer;
  display: flex; align-items: center; gap: 16px;
  box-shadow: 0 4px 10px rgba(0,0,0,0.03); transition: all 0.2s; border: 1px solid transparent;
}
.action-card:hover { transform: translateY(-3px); box-shadow: 0 10px 20px rgba(0,0,0,0.08); }
.action-card.primary { border: 1px solid #2cb398; background: #f0fffc; }
.card-icon { font-size: 2rem; }
.card-text h3 { font-size: 1.1rem; margin-bottom: 4px; color: #333; }
.card-text p { font-size: 0.9rem; color: #888; }

.divider { border: 0; height: 1px; background: #eee; margin: 40px 0; }

.section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.section-header h3 { font-size: 1.4rem; font-weight: 700; color: #333; }
.more-link { font-size: 0.9rem; color: #888; text-decoration: none; }
.more-link:hover { color: #2cb398; }

.route-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 20px; }
.route-card {
  background: white; border-radius: 12px; overflow: hidden; cursor: pointer;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06); transition: transform 0.2s;
}
.route-card:hover { transform: translateY(-5px); }
.route-card-img {
  height: 140px; background: linear-gradient(120deg, #a1c4fd 0%, #c2e9fb 100%);
  position: relative;
}
.route-tag {
  position: absolute; top: 12px; left: 12px; background: rgba(0,0,0,0.6); color: white;
  font-size: 0.7rem; padding: 4px 8px; border-radius: 4px; font-weight: bold;
}
.route-card-body { padding: 16px; }
.route-title { font-size: 1.1rem; font-weight: bold; margin-bottom: 6px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
/* ✅ [수정됨] 설명 텍스트가 잘리지 않고 2줄 말줄임표(...)로 나오도록 개선 */
.route-desc { 
  font-size: 0.9rem; 
  color: #666; 
  margin-bottom: 12px; 
  
  /* 멀티 라인 말줄임 처리 */
  display: -webkit-box;
  -webkit-line-clamp: 2;      /* 최대 2줄까지만 표시 */
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: normal;        /* 기존 nowrap 제거 */
  line-height: 1.4;           /* 줄 간격 확보 */
  height: 2.8em;              /* 2줄 높이만큼 고정 (레이아웃 깨짐 방지) */
}
.route-meta { font-size: 0.8rem; color: #999; display: flex; gap: 8px; }

.empty-state { text-align: center; padding: 40px; background: white; border-radius: 12px; color: #888; border: 1px dashed #ddd; }
.btn-outline { margin-top: 15px; padding: 10px 20px; background: white; border: 1px solid #2cb398; color: #2cb398; border-radius: 20px; cursor: pointer; }
.btn-outline:hover { background: #2cb398; color: white; }

.status-msg { text-align: center; padding: 40px; color: #666; }
.spinner { display: inline-block; width: 12px; height: 12px; border: 2px solid #ccc; border-top-color: #2cb398; border-radius: 50%; animation: spin 1s infinite linear; margin-right: 8px; }
@keyframes spin { to { transform: rotate(360deg); } }

@media (max-width: 768px) {
  .hero-text h1 { font-size: 2rem; }
  .dashboard-header h2 { font-size: 1.5rem; }
}
.recommend-gradient { background: linear-gradient(120deg, #fccb90 0%, #d57eeb 100%); }
.route-tag.hot { background-color: #ff5252; }
.route-tag.recommend { background-color: #764ba2; }
.route-card:hover { transform: translateY(-8px); box-shadow: 0 8px 20px rgba(0,0,0,0.1); }



.place-list {
  list-style: none;
  padding: 0;
  margin: 0;
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

.place-list-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 18px;
  cursor: pointer;
  border-bottom: 1px solid #eee;
  /* transition: background 0.15s; */
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.place-list-item:last-child {
  border-bottom: none;
}

.place-list-item:hover {
  background: #f5fdfa;
  transform: translateY(-4px);
  box-shadow: 0 6px 14px rgba(0,0,0,0.08);
}

.route-title { font-size: 0.95rem; font-weight: bold; margin-bottom: 6px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

.place-arrow {
  font-size: 1.2rem;
  color: #2cb398;
}

</style>