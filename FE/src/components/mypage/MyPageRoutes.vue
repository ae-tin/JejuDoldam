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
          
          <button 
            class="btn-delete" 
            @click.stop="deleteRoute(route.id)" 
            title="루트 삭제"
          >
            🗑️
          </button>
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

const routes = ref([])
const loading = ref(false)

const goDetail = (id) => {
  router.push({ name: 'route-detail', params: { routeId: id } })
}

// ✅ [추가됨] 루트 삭제 함수
const deleteRoute = async (routeId) => {
  if (!confirm('정말 이 여행 루트를 삭제하시겠습니까?')) return

  try {
    // DELETE /routes/<route_pk>
    await api.delete(`/routes/${routeId}/`)
    
    // 삭제 성공 시 목록에서 제거
    routes.value = routes.value.filter(r => r.id !== routeId)
    alert('여행 루트가 삭제되었습니다.')
  } catch (e) {
    console.error('삭제 실패:', e)
    alert('루트 삭제 중 오류가 발생했습니다.')
  }
}

const formatDate = (iso) => {
  if (!iso) return '-'
  const d = new Date(iso)
  return `${d.getFullYear()}.${d.getMonth()+1}.${d.getDate()}`
}

const fetchRoutes = async () => {
  loading.value = true
  try {
    const { data } = await api.get('/routes/')
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
    loading.value = false
  }
}

const bgStyle = (url) => ({
  backgroundImage: `url(${url})`,
  backgroundSize: "cover",
  backgroundPosition: "center",
  backgroundRepeat: "no-repeat",
})

onMounted(() => {
  fetchRoutes()
})
</script>

<style scoped>
/* 기존 스타일 유지 */
.header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
.header h3 { font-size: 1.3rem; font-weight: 700; color: #333; }
.count { color: #888; font-weight: 600; }

.route-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 24px;
}

.route-card {
  background: white; border-radius: 16px; overflow: hidden;
  box-shadow: 0 4px 15px rgba(0,0,0,0.05); cursor: pointer;
  transition: transform 0.2s; border: 1px solid #eee;
}
.route-card:hover { transform: translateY(-5px); border-color: #2cb398; }

.card-thumb {
  height: 160px;
  background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
  position: relative;
}
.badge {
  position: absolute; bottom: 12px; left: 12px;
  background: rgba(255,255,255,0.9); padding: 5px 10px; border-radius: 8px;
  font-size: 0.8rem; font-weight: bold; color: #555;
}

/* ✅ [추가됨] 삭제 버튼 스타일 */
.btn-delete {
  position: absolute;
  top: 10px;
  right: 10px;
  background: rgba(0, 0, 0, 0.3); /* 반투명 배경 */
  border: none;
  border-radius: 50%;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 1rem;
  transition: background 0.2s;
  backdrop-filter: blur(4px); /* 블러 효과 */
}
.btn-delete:hover {
  background: rgba(255, 0, 0, 0.6); /* 호버 시 붉은색 */
}

.card-body { padding: 20px; }
.title { font-size: 1.15rem; font-weight: 700; margin-bottom: 8px; color: #222; }
.desc { color: #666; font-size: 0.95rem; margin-bottom: 20px; line-height: 1.5; height: 3em; overflow: hidden; }
.footer { display: flex; justify-content: space-between; align-items: center; font-size: 0.9rem; color: #999; border-top: 1px solid #eee; padding-top: 15px; }
.link { color: #2cb398; font-weight: 700; }

.state-msg { text-align: center; padding: 40px; color: #888; }
.spinner { display: inline-block; width: 20px; height: 20px; border: 3px solid #ddd; border-top-color: #2cb398; border-radius: 50%; animation: spin 1s infinite linear; margin-right: 8px; vertical-align: middle; }
@keyframes spin { to { transform: rotate(360deg); } }
.empty-state { text-align: center; padding: 80px 0; color: #999; }
.icon { font-size: 3rem; margin-bottom: 16px; }
</style>