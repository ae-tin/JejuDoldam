<template>
  <div class="routes-tab-content">
    
    <div class="header">
      <h3>📂 내가 저장한 여행</h3>
      <span class="count" v-if="routes.length">총 {{ routes.length }}개</span>
    </div>

    <div v-if="loading" class="state-msg">
      <div class="spinner"></div> 로딩 중...
    </div>

    <div v-else-if="routes.length" class="route-grid">
      <article 
        v-for="route in routes" 
        :key="route.id" 
        class="route-card"
        @click="goDetail(route.id)"
      >
        <div 
          class="card-thumb"
          :class="{ 'recommend-gradient': !route.photo_url }"
          :style="route.photo_url ? bgStyle(route.photo_url) : {}"
        >
          <span class="badge">Route #{{ route.id }}</span>
        </div>
        
        <div class="card-body">
          <h4 class="title">{{ route.title }}</h4>
          <p class="desc">{{ route.description || '설명이 없습니다.' }}</p>
          <div class="footer">
            <span class="date">{{ formatDate(route.created_at) }}</span>
            <span class="link">상세보기 →</span>
          </div>
        </div>
      </article>
    </div>

    <div v-else class="empty-state">
      <div class="icon">📭</div>
      <p>아직 저장된 여행 루트가 없습니다.</p>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/api/client'

const router = useRouter()

// --- [상태 변수] ---
const routes = ref([])     // API로 받아온 루트 목록을 저장할 배열
const loading = ref(false) // 로딩 중인지 여부 (true/false)

// --- [함수: 라우팅] ---
// 상세 페이지로 이동
const goDetail = (id) => {
  // router.push: 브라우저 히스토리에 기록을 남기며 페이지 이동
  router.push({ name: 'route-detail', params: { routeId: id } })
}

// --- [함수: 유틸리티] ---
// 날짜 포맷팅 (YYYY.MM.DD)
const formatDate = (iso) => {
  if (!iso) return '-'
  const d = new Date(iso)
  return `${d.getFullYear()}.${d.getMonth()+1}.${d.getDate()}`
}

// --- [함수: API 호출] ---
const fetchRoutes = async () => {
  // 1. 요청 시작 전 로딩 상태 켜기
  loading.value = true
  try {
    // 2. 백엔드에 GET 요청
    const { data } = await api.get('/routes/')
    // 3. 받아온 데이터를 ID 역순(최신순)으로 정렬해서 저장
    const routesData = data.sort((a, b) => b.id - a.id)

    for (const route of routesData) {
      const photoRes = await api.get('/routes/photo/', {
        params: { route_id: route.id }
      })

      route.photo_url = photoRes.data?.photo_url || null
    }

    routes.value = routesData

  } catch (e) {
    console.error('루트 목록 로드 실패:', e)
  } finally {
    // 4. 성공하든 실패하든 로딩 상태 끄기 (반드시 실행됨)
    loading.value = false
  }
}


const bgStyle = (url) => ({
  backgroundImage: `url(${url})`,
  backgroundSize: "cover",
  backgroundPosition: "center",
  backgroundRepeat: "no-repeat",
})
// --- [라이프사이클] ---
// 컴포넌트가 마운트되자마자 데이터를 불러옵니다.
onMounted(() => {
  fetchRoutes()
})
</script>

<style scoped>
/* 헤더 스타일 */
.header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
.header h3 { font-size: 1.3rem; font-weight: 700; color: #333; }
.count { color: #888; font-weight: 600; }

/* 그리드 레이아웃 설정 
  - minmax(300px, 1fr): 카드의 최소 너비는 300px, 공간이 남으면 1fr(비율)로 늘어남
  - auto-fill: 화면 너비에 맞춰서 가능한 많은 열(column)을 자동으로 생성
*/
.route-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 24px;
}

/* 카드 디자인 */
.route-card {
  background: white;
  border-radius: 16px;
  overflow: hidden; /* 자식 요소가 둥근 모서리를 넘치지 않게 */
  box-shadow: 0 4px 15px rgba(0,0,0,0.05);
  cursor: pointer;
  transition: transform 0.2s; /* 호버 시 부드러운 움직임 */
  border: 1px solid #eee;
}
.route-card:hover { 
  transform: translateY(-5px); /* 살짝 위로 떠오름 */
  border-color: #2cb398; /* 테두리 민트색 */
}

.card-thumb {
  height: 160px;
  background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
  position: relative;
}
.badge {
  position: absolute; bottom: 12px; left: 12px;
  background: rgba(255,255,255,0.9);
  padding: 5px 10px; border-radius: 8px;
  font-size: 0.8rem; font-weight: bold; color: #555;
}

.card-body { padding: 20px; }
.title { font-size: 1.15rem; font-weight: 700; margin-bottom: 8px; color: #222; }
.desc { 
  color: #666; font-size: 0.95rem; margin-bottom: 20px; line-height: 1.5; 
  height: 3em; overflow: hidden; /* 2줄 넘어가면 숨김 처리 */
}
.footer { display: flex; justify-content: space-between; align-items: center; font-size: 0.9rem; color: #999; border-top: 1px solid #eee; padding-top: 15px; }
.link { color: #2cb398; font-weight: 700; }

/* 로딩 및 빈 상태 */
.state-msg { text-align: center; padding: 40px; color: #888; }
.spinner { display: inline-block; width: 20px; height: 20px; border: 3px solid #ddd; border-top-color: #2cb398; border-radius: 50%; animation: spin 1s infinite linear; margin-right: 8px; vertical-align: middle; }
@keyframes spin { to { transform: rotate(360deg); } }

.empty-state { text-align: center; padding: 80px 0; color: #999; }
.icon { font-size: 3rem; margin-bottom: 16px; }
</style>