<template>
  <div class="pc-layout-container" @mouseup="stopResize" @mouseleave="stopResize">
    
    <div v-if="loading" class="state-overlay">
      <div class="spinner"></div>
      <p>여행 코스를 생성하고 있어요...</p>
    </div>

    <div v-else-if="error" class="state-overlay error">
      <p>⚠️ {{ error }}</p>
      <RouterLink class="btn-retry" to="/routes/recommend">다시 시도</RouterLink>
    </div>

    <div 
      v-else-if="selectedRoute" 
      class="split-view"
      @mousemove="onResize"
    >
      
      <aside class="left-panel" :style="{ width: panelWidth + 'px' }">
        <div v-if="results.length" class="panel-top-tabs">
          <button
            v-for="(r, idx) in results"
            :key="r.id ?? idx"
            class="panel-tab-btn"
            :class="{ active: idx === selectedRouteIndex }"
            @click="selectRoute(idx)"
          >
            추천 {{ idx + 1 }}
          </button>
        </div>

        <div class="panel-header">
          <div class="title-row">
            <h3 class="route-title">{{ selectedRoute.title }}</h3>
            <button
              class="save-btn"
              :disabled="saving || !canSave"
              @click="handleConfirm(selectedRoute)"
            >
              {{ saving ? '저장 중...' : '일정 저장' }}
            </button>
          </div>
          <p class="route-desc">{{ selectedRoute.description }}</p>
        </div>

        <div class="day-tabs-sticky">
          <div class="day-scroll-area">
            <button
              v-for="d in dayList"
              :key="d"
              class="day-chip"
              :class="{ active: d === selectedDay }"
              @click="selectedDay = d"
            >
              DAY {{ d }}
            </button>
          </div>
        </div>

        <div class="place-list-container">
          
          <div class="search-section">
            <KakaoPlaceSearch @select="addPlaceToSelectedDay" />
          </div>

          <p v-if="dayPlaces.length" class="helper-text">
            * 장소를 클릭하면 사진이 나와요.
          </p>

          <ul class="place-items">
            <li
              v-for="(p, idx) in dayPlaces"
              :key="p._uid"
              class="place-row"
              :class="{ 'selected': selectedPlaceUid === p._uid }"
              @click="togglePlacePhoto(p)"
            >
              <div class="place-info">
                <span class="marker-num">{{ idx + 1 }}</span>
                <div class="text-wrap">
                  <strong class="name">
                    {{ p.name }}
                    <a v-if="p.place_url" :href="p.place_url" target="_blank" @click.stop class="map-link">
                      <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path><polyline points="15 3 21 3 21 9"></polyline><line x1="10" y1="14" x2="21" y2="3"></line></svg>
                    </a>
                  </strong>
                  <span class="addr">{{ p.address }}</span>
                </div>
              </div>

              <div class="place-actions" @click.stop>
                <div class="btn-group">
                  <button type="button" @click="movePlace(idx, -1)" :disabled="idx === 0">▲</button>
                  <button type="button" @click="movePlace(idx, 1)" :disabled="idx === dayPlaces.length - 1">▼</button>
                </div>
                <button type="button" class="del-btn" @click="removePlaceAt(idx)">×</button>
              </div>

              <div v-if="selectedPlaceUid === p._uid && p.photo_url" class="photo-expand">
                <img :src="p.photo_url" class="expanded-img" />
              </div>
            </li>
          </ul>

          <div v-if="!dayPlaces.length" class="empty-placeholder">
            <span class="icon">📍</span>
            <p>방문할 장소를 검색해서 추가해보세요.</p>
          </div>
        </div>
      </aside>

      <div class="resizer" @mousedown="startResize"></div>

      <main class="right-map">
        <KakaoMap :places="dayPlaces" class="full-map" />
      </main>

    </div>

    <div v-else-if="!loading" class="state-overlay empty">
      <p>생성된 코스가 없습니다.</p>
      <RouterLink class="btn-retry" to="/routes/recommend">입력 화면으로</RouterLink>
    </div>

  </div>
</template>

<script setup>
// =================================================================
// [로직 변경 없음] 기존 기능을 100% 유지합니다.
// =================================================================
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute, RouterLink } from 'vue-router'
import api from '@/api/client'
import KakaoMap from '@/components/KakaoMap.vue'
import KakaoPlaceSearch from '@/components/KakaoPlaceSearch.vue'

// --- [Resizing Logic] ---
const panelWidth = ref(500)
const isResizing = ref(false)

const startResize = () => {
  isResizing.value = true
  document.body.style.cursor = 'col-resize'
  document.body.style.userSelect = 'none'
}

const onResize = (event) => {
  if (!isResizing.value) return
  let newWidth = event.clientX
  if (newWidth < 300) newWidth = 300
  if (newWidth > 800) newWidth = 800
  panelWidth.value = newWidth
}

const stopResize = () => {
  if (isResizing.value) {
    isResizing.value = false
    document.body.style.cursor = ''
    document.body.style.userSelect = ''
    window.dispatchEvent(new Event('resize'))
  }
}

// --- [Core Logic] ---
const router = useRouter()
const route = useRoute()

const loading = ref(false)
const saving = ref(false)
const error = ref('')
const results = ref([])
const selectedRouteIndex = ref(0)
const selectedDay = ref(1)

const selectedRoute = computed(() => results.value[selectedRouteIndex.value] || null)

const recommendPayload = computed(() => {
  const q = route.query
  return {
    HOW_LONG: Number(q.HOW_LONG),
    TRAVEL_STYL_1: Number(q.TRAVEL_STYL_1),
    TRAVEL_STATUS_ACCOMPANY: q.TRAVEL_STATUS_ACCOMPANY ? String(q.TRAVEL_STATUS_ACCOMPANY) : '',
    TRAVEL_MOTIVE_1: q.TRAVEL_MOTIVE_1 ? String(q.TRAVEL_MOTIVE_1) : '',
  }
})

const canRecommend = computed(() => {
  const p = recommendPayload.value
  return (
    Number.isFinite(p.HOW_LONG) &&
    Number.isFinite(p.TRAVEL_STYL_1) &&
    !!p.TRAVEL_STATUS_ACCOMPANY &&
    !!p.TRAVEL_MOTIVE_1
  )
})

const dayList = computed(() => {
  if (!selectedRoute.value) return []
  const n = Number(selectedRoute.value.days || selectedRoute.value.HOW_LONG || 1)
  return Array.from({ length: n }, (_, i) => i + 1)
})

const selectedDayObj = computed(() => {
  if (!selectedRoute.value) return null
  return selectedRoute.value.daysData?.find((d) => d.day === selectedDay.value) || null
})

const dayPlaces = computed(() => {
  const arr = selectedDayObj.value?.places || []
  return arr.slice().sort((a, b) => (a.order ?? 0) - (b.order ?? 0))
})

const canSave = computed(() => {
  if (!selectedRoute.value) return false
  const all = selectedRoute.value.daysData || []
  return all.some((d) => (d.places || []).length > 0)
})

function selectRoute(idx) {
  selectedRouteIndex.value = idx
  selectedDay.value = dayList.value[0] ?? 1
}

function toEditableRoute(r) {
  const days = Number(r.days ?? r.HOW_LONG ?? recommendPayload.value.HOW_LONG ?? 1)
  const daysData = Array.from({ length: days }, (_, i) => ({
    day: i + 1,
    places: [],
  }))

  for (const p of r.places || []) {
    const day = Number(p.day ?? 1)
    const target = daysData[day - 1]
    if (!target) continue
    target.places.push({
      _uid: genUid(),
      order: p.order ?? target.places.length + 1,
      name: p.name,
      address: p.address ?? '',
      latitude: p.latitude ?? null,
      longitude: p.longitude ?? null,
      photo_url: p.photo_url ?? '',
      place_url: p.place_url ?? '',
      place_cat: p.place_cat ?? '',
      memo: p.memo ?? '',
    })
  }
  for (const d of daysData) normalizeOrders(d)
  return { ...r, days, daysData }
}

function normalizeOrders(dayData) {
  dayData.places.forEach((p, idx) => { p.order = idx + 1 })
}

function genUid() {
  return globalThis.crypto?.randomUUID?.() || `${Date.now()}-${Math.random().toString(16).slice(2)}`
}

function addPlaceToSelectedDay(place) {
  const dayObj = selectedDayObj.value
  if (!dayObj) return
  dayObj.places.push({
    _uid: genUid(),
    order: dayObj.places.length + 1,
    name: place.name,
    address: place.address ?? '',
    latitude: place.latitude ?? null,
    longitude: place.longitude ?? null,
    place_url: place.place_url ?? '',
    memo: '',
  })
  normalizeOrders(dayObj)
}

function removePlaceAt(idx) {
  const dayObj = selectedDayObj.value
  if (!dayObj) return
  dayObj.places.splice(idx, 1)
  normalizeOrders(dayObj)
}

function movePlace(idx, dir) {
  const dayObj = selectedDayObj.value
  if (!dayObj) return
  const next = idx + dir
  if (next < 0 || next >= dayObj.places.length) return
  const tmp = dayObj.places[idx]
  dayObj.places[idx] = dayObj.places[next]
  dayObj.places[next] = tmp
  normalizeOrders(dayObj)
}

async function fetchRecommendations() {
  error.value = ''
  results.value = []
  selectedRouteIndex.value = 0
  selectedDay.value = 1

  if (!canRecommend.value) {
    error.value = '추천 입력 정보가 없거나 올바르지 않습니다.'
    return
  }

  loading.value = true
  try {
    const { data } = await api.post('/routes/recommend/', recommendPayload.value)
    results.value = (data || []).map((r) => toEditableRoute(r))
    selectedRouteIndex.value = 0
    selectedDay.value = 1
  } catch (e) {
    console.error(e)
    const serverMsg = e?.response?.data?.detail || e?.response?.data?.message || (typeof e?.response?.data === 'string' ? e.response.data : null)
    error.value = serverMsg || '오류가 발생했습니다.'
  } finally {
    loading.value = false
  }
}

async function handleConfirm(routeObj) {
  if (!confirm('이 루트를 확정해서 저장할까요?')) return
  saving.value = true
  try {
    const confirmPayload = mapRouteToConfirmPayload(routeObj)
    const { data } = await api.post('/routes/confirm/', confirmPayload)
    router.push({ name: 'route-detail', params: { routeId: data.id } })
  } catch (e) {
    console.error(e)
    alert('저장 중 오류가 발생했습니다.')
  } finally {
    saving.value = false
  }
}

function mapRouteToConfirmPayload(routeObj) {
  return {
    title: routeObj.title,
    description: routeObj.description ?? '',
    days: (routeObj.daysData || []).map((d) => ({
      day: d.day,
      places: (d.places || []).map((p, idx) => ({
        order: idx + 1,
        name: p.name,
        address: p.address ?? '',
        latitude: p.latitude ?? null,
        longitude: p.longitude ?? null,
        photo_url: p.photo_url ?? '',
        place_url: p.place_url ?? '',
        memo: p.memo ?? '',
      })),
    })),
  }
}

const selectedPlaceUid = ref(null)
function togglePlacePhoto(place) {
  selectedPlaceUid.value = selectedPlaceUid.value === place._uid ? null : place._uid
}

onMounted(fetchRecommendations)
watch(() => route.query, () => fetchRecommendations(), { deep: true })
</script>

<style scoped>
/* [페이지 레이아웃]
  - padding-top: 60px; (전역 Navbar 높이만큼 여백 확보)
  - height: 100vh; (화면 꽉 채움)
*/
.pc-layout-container {
  display: flex;
  flex-direction: column;
  height: 100vh; 
  padding-top: 60px; /* App.vue의 Navbar 높이 고려 */
  background-color: #fff;
  overflow: hidden;
  box-sizing: border-box; /* 패딩 포함 높이 계산 */
}

/* [스플릿 뷰]
  - 부모(pc-layout-container)의 남은 높이를 모두 채웁니다.
*/
.split-view {
  display: flex;
  flex: 1; 
  height: 100%; /* 부모의 남은 공간 100% 사용 */
  overflow: hidden;
}

/* --- [LEFT PANEL] 왼쪽 패널 --- */
.left-panel {
  border-right: 1px solid #e0e0e0;
  background: #fff;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  overflow-y: auto;
  position: relative;
  z-index: 5;
  min-width: 320px;
  max-width: 800px;
}

/* ✅ [수정됨] 감각적인 추천 루트 탭 스타일 (Segmented Control) */
.panel-top-tabs {
  display: flex;
  background-color: #f2f4f6; /* 은은한 회색 배경 트랙 */
  padding: 6px;
  margin: 24px 24px 0; /* 패널 내부 여백과 라인 맞춤 */
  border-radius: 14px; /* 둥근 모서리 */
  gap: 6px; /* 버튼 사이 간격 */
}

.panel-tab-btn {
  flex: 1;
  padding: 10px 0;
  border: none;
  background: transparent;
  font-size: 0.9rem;
  font-weight: 600;
  color: #888;
  cursor: pointer;
  border-radius: 10px; /* 버튼 자체도 둥글게 */
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1); /* 쫀득한 애니메이션 */
  position: relative;
  overflow: hidden;
}

/* 호버 효과 */
.panel-tab-btn:hover {
  color: #555;
  background-color: rgba(255, 255, 255, 0.5);
}

/* 활성화 상태 (카드처럼 떠오르는 효과) */
.panel-tab-btn.active {
  background-color: #fff;
  color: #2cb398; /* 브랜드 컬러 */
  font-weight: 800;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08); /* 부드러운 그림자 */
  transform: scale(1.02); /* 아주 살짝 커지면서 강조 */
}

/* 클릭 시 눌리는 느낌 (인터랙션 디테일) */
.panel-tab-btn:active {
  transform: scale(0.98);
}

/* 패널 헤더 (여백 조정) */
.panel-header {
  padding: 24px 24px 16px; /* 탭과의 간격을 위해 상단 패딩 유지 */
  background: #fff;
}

.title-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.route-title {
  font-size: 1.3rem;
  font-weight: 800;
  color: #222;
  margin: 0;
}

.save-btn {
  background: #2cb398;
  color: white;
  border: none;
  padding: 8px 14px;
  border-radius: 6px;
  font-weight: 700;
  font-size: 0.85rem;
  cursor: pointer;
  white-space: nowrap;
}
.save-btn:hover:not(:disabled) { background: #24917d; }
.save-btn:disabled { background: #ccc; cursor: not-allowed; }

.route-desc {
  color: #666;
  font-size: 0.9rem;
  line-height: 1.4;
  margin: 0;
}

/* DAY 탭 (Sticky) */
.day-tabs-sticky {
  position: sticky;
  top: 0;
  background: #fff;
  padding: 10px 24px;
  border-bottom: 1px solid #f0f0f0;
  z-index: 10;
}

.day-scroll-area {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  padding-bottom: 4px;
}
.day-scroll-area::-webkit-scrollbar { height: 0; }

.day-chip {
  padding: 6px 14px;
  border: 1px solid #e0e0e0;
  border-radius: 20px;
  background: #fff;
  color: #555;
  font-size: 0.9rem;
  font-weight: 600;
  white-space: nowrap;
  cursor: pointer;
}
.day-chip.active {
  background: #333;
  color: #fff;
  border-color: #333;
}

/* 장소 리스트 */
.place-list-container {
  padding: 0 24px 60px; /* 하단에 여유 공간 */
  flex: 1;
}

.search-section { margin: 16px 0; }

.helper-text {
  font-size: 0.8rem;
  color: #999;
  margin-bottom: 12px;
  text-align: right;
}

.place-items {
  list-style: none;
  padding: 0;
  margin: 0;
}

/* 장소 행 스타일 */
.place-row {
  display: flex;
  flex-direction: column;
  border-bottom: 1px solid #f0f0f0;
  padding: 16px 0;
  cursor: pointer;
  transition: background 0.2s;
}
.place-row:hover { background: #fafafa; }
.place-row.selected { background: #f0fdfa; }

.place-info {
  display: flex;
  align-items: flex-start;
  position: relative;
}

.marker-num {
  width: 24px; height: 24px;
  background: #2cb398;
  color: white;
  border-radius: 50%;
  text-align: center;
  line-height: 24px;
  font-size: 0.8rem;
  font-weight: 700;
  margin-right: 12px;
  flex-shrink: 0;
}

.text-wrap { flex: 1; }

.name {
  display: block;
  font-size: 1rem;
  font-weight: 700;
  color: #333;
  margin-bottom: 4px;
}

.map-link {
  color: #aaa;
  margin-left: 6px;
  vertical-align: middle;
}
.map-link:hover { color: #2cb398; }

.addr {
  display: block;
  font-size: 0.85rem;
  color: #888;
}

.place-actions {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  margin-top: 8px;
  gap: 8px;
}

.btn-group {
  display: flex;
  border: 1px solid #eee;
  border-radius: 6px;
  overflow: hidden;
}
.btn-group button {
  width: 28px; height: 28px;
  border: none; background: #fff; cursor: pointer;
  font-size: 0.7rem; border-right: 1px solid #eee;
}
.btn-group button:last-child { border-right: none; }
.btn-group button:hover:not(:disabled) { background: #f5f5f5; }
.btn-group button:disabled { color: #ddd; }

.del-btn {
  background: none; border: none; color: #bbb;
  font-size: 1.2rem; cursor: pointer; padding: 0 4px;
}
.del-btn:hover { color: #e74c3c; }

.photo-expand {
  margin-top: 12px;
  padding-left: 36px;
  animation: slideDown 0.3s ease;
}
.expanded-img {
  width: 100%;
  border-radius: 8px;
  border: 1px solid #eee;
}

@keyframes slideDown {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}

.empty-placeholder {
  text-align: center;
  padding: 40px 0;
  color: #aaa;
}
.empty-placeholder .icon { font-size: 2rem; display: block; margin-bottom: 8px; }

/* [RESIZER] */
.resizer {
  width: 8px;
  background: transparent;
  cursor: col-resize;
  flex-shrink: 0;
  z-index: 10;
  margin-left: -4px;
  transition: background 0.2s;
}
.resizer:hover, .resizer:active {
  background: rgba(44, 179, 152, 0.2); 
  border-left: 1px solid #2cb398;
}

/* [RIGHT PANEL] 지도 */
.right-map {
  flex: 1;
  background: #f0f0f0;
  position: relative;
}
.full-map { width: 100%; height: 100%; }

/* 로딩/에러 */
.state-overlay {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100%; /* 부모 높이만큼 */
  background: #fff;
}
.btn-retry {
  margin-top: 16px;
  padding: 10px 20px;
  border: 1px solid #ddd;
  border-radius: 8px;
  text-decoration: none;
  color: #333;
}
.spinner {
  width: 40px; height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #2cb398;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* 모바일 대응 */
@media (max-width: 900px) {
  .split-view { flex-direction: column-reverse; }
  .left-panel { width: 100% !important; height: 50vh; }
  .right-map { height: 50vh; }
  .resizer { display: none; }
}
</style>