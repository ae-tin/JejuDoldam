<template>
  <div class="page-container">
    
    <header class="header-section">
      <h2 class="page-title">🍊 AI가 추천하는 제주 여행 코스</h2>
      <p class="page-subtitle">마음에 드는 루트를 선택하고 자유롭게 수정해보세요.</p>
    </header>

    <div v-if="loading" class="state-card loading">
      <div class="spinner"></div>
      <p>여행 코스를 생성하고 있어요...</p>
    </div>

    <div v-else-if="error" class="state-card error">
      <p>⚠️ {{ error }}</p>
      <div class="actions">
        <RouterLink class="btn-outline" to="/routes/recommend">다시 입력하기</RouterLink>
      </div>
    </div>

    <div v-else-if="results.length" class="content-wrapper">
      
      <div class="route-tabs">
        <button
          v-for="(r, idx) in results"
          :key="r.id ?? idx"
          class="route-tab-btn"
          :class="{ active: idx === selectedRouteIndex }"
          @click="selectRoute(idx)"
          type="button"
        >
          <span class="tab-label">추천 루트 {{ idx + 1 }}</span>
          <span v-if="idx === selectedRouteIndex" class="tab-desc-preview">
            {{ r.title }}
          </span>
        </button>
      </div>

      <div v-if="selectedRoute" class="route-detail-container">
        
        <div class="route-info-header">
          <div class="text-group">
            <h3 class="route-name">{{ selectedRoute.title }}</h3>
            <p class="route-description">{{ selectedRoute.description }}</p>
          </div>
          
          <button
            class="save-btn"
            type="button"
            :disabled="saving || !canSave"
            @click="handleConfirm(selectedRoute)"
            title="현재 편집 상태 그대로 저장됩니다."
          >
            {{ saving ? '저장 중...' : '이 루트 확정 저장 ✨' }}
          </button>
        </div>

        <div class="day-tabs-wrapper">
          <button
            v-for="d in dayList"
            :key="d"
            class="day-pill"
            :class="{ active: d === selectedDay }"
            @click="selectedDay = d"
            type="button"
          >
            DAY {{ d }}
          </button>
        </div>

        <section class="map-section">
          <KakaoMap :places="dayPlaces" class="big-map" />
        </section>

        <section class="places-section">
          
          <div class="search-box-wrapper">
            <KakaoPlaceSearch @select="addPlaceToSelectedDay" />
          </div>

          <p v-if="dayPlaces.length" class="guide-text">
            💡 장소를 클릭하면 <b>사진</b>을 볼 수 있어요!
          </p>

          <ul class="place-list">
            <li
              v-for="(p, idx) in dayPlaces"
              :key="p._uid"
              class="place-card"
              @click="togglePlacePhoto(p)"
            >
              <div class="card-header">
                <div class="place-title-group">
                  <span class="order-badge">{{ p.order }}</span>
                  <strong class="place-name">{{ p.name }}</strong>
                  
                  <a 
                    v-if="p.place_url" 
                    class="kakaomap-link" 
                    :href="p.place_url" 
                    target="_blank" 
                    rel="noreferrer"
                    @click.stop
                  >
                    지도보기 ↗
                  </a>
                </div>

                <div class="action-buttons" @click.stop>
                  <button 
                    type="button" 
                    class="icon-btn" 
                    @click="movePlace(idx, -1)" 
                    :disabled="idx === 0"
                    title="위로 이동"
                  >
                    ▲
                  </button>
                  <button 
                    type="button" 
                    class="icon-btn" 
                    @click="movePlace(idx, 1)" 
                    :disabled="idx === dayPlaces.length - 1"
                    title="아래로 이동"
                  >
                    ▼
                  </button>
                  <button 
                    type="button" 
                    class="icon-btn delete-btn" 
                    @click="removePlaceAt(idx)"
                    title="삭제"
                  >
                    🗑️
                  </button>
                </div>
              </div>

              <div class="place-address">{{ p.address || '주소 정보 없음' }}</div>

              <transition name="slide-fade">
                <div
                  v-if="selectedPlaceUid === p._uid && p.photo_url"
                  class="place-photo-wrapper"
                >
                  <img :src="p.photo_url" :alt="p.name" class="place-img" />
                </div>
              </transition>
            </li>
          </ul>

          <div v-if="!dayPlaces.length" class="empty-state">
            <p>아직 DAY {{ selectedDay }}에 장소가 없습니다.<br>위 검색창에서 장소를 추가해보세요!</p>
          </div>

        </section>

      </div>
    </div>

    <div v-else-if="!loading" class="state-card empty">
      <p>추천 결과가 없습니다. 입력 페이지에서 추천을 먼저 받아주세요.</p>
      <RouterLink class="btn-outline" to="/routes/recommend">입력하러 가기</RouterLink>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute, RouterLink } from 'vue-router'
import api from '@/api/client'
import KakaoMap from '@/components/KakaoMap.vue'
import KakaoPlaceSearch from '@/components/KakaoPlaceSearch.vue'

const router = useRouter()
const route = useRoute()

// --- [상태 변수] ---
const loading = ref(false)
const saving = ref(false)
const error = ref('')
const results = ref([])          // API로 받아온 추천 루트 목록 (3개)
const selectedRouteIndex = ref(0) // 현재 보고 있는 추천 루트 인덱스
const selectedDay = ref(1)        // 현재 보고 있는 일차 (DAY)

// --- [Computed: 현재 선택된 데이터 계산] ---
const selectedRoute = computed(() => results.value[selectedRouteIndex.value] || null)

// 입력 페이지에서 넘어온 Query String을 API Payload 포맷으로 변환
const recommendPayload = computed(() => {
  const q = route.query
  const HOW_LONG = Number(q.HOW_LONG)
  const TRAVEL_STYL_1 = Number(q.TRAVEL_STYL_1)
  return {
    HOW_LONG,
    TRAVEL_STYL_1,
    TRAVEL_STATUS_ACCOMPANY: q.TRAVEL_STATUS_ACCOMPANY ? String(q.TRAVEL_STATUS_ACCOMPANY) : '',
    TRAVEL_MOTIVE_1: q.TRAVEL_MOTIVE_1 ? String(q.TRAVEL_MOTIVE_1) : '',
  }
})

// 필수 값이 모두 있는지 확인 (없으면 API 호출 안 함)
const canRecommend = computed(() => {
  const p = recommendPayload.value
  return (
    Number.isFinite(p.HOW_LONG) && p.HOW_LONG >= 1 && p.HOW_LONG <= 7 &&
    Number.isFinite(p.TRAVEL_STYL_1) && p.TRAVEL_STYL_1 >= 1 && p.TRAVEL_STYL_1 <= 7 &&
    !!p.TRAVEL_STATUS_ACCOMPANY &&
    !!p.TRAVEL_MOTIVE_1
  )
})

// 선택된 루트의 전체 DAY 리스트 (예: [1, 2, 3])
const dayList = computed(() => {
  if (!selectedRoute.value) return []
  const n = Number(selectedRoute.value.days || selectedRoute.value.HOW_LONG || recommendPayload.value.HOW_LONG || 1)
  return Array.from({ length: n }, (_, i) => i + 1)
})

// 현재 선택된 DAY의 데이터 객체
const selectedDayObj = computed(() => {
  if (!selectedRoute.value) return null
  return selectedRoute.value.daysData?.find((d) => d.day === selectedDay.value) || null
})

// 현재 선택된 DAY의 장소 목록 (Order 순으로 정렬)
const dayPlaces = computed(() => {
  const arr = selectedDayObj.value?.places || []
  return arr.slice().sort((a, b) => (a.order ?? 0) - (b.order ?? 0))
})

// 저장 가능 여부 (장소가 하나라도 있어야 저장 가능)
const canSave = computed(() => {
  if (!selectedRoute.value) return false
  const all = selectedRoute.value.daysData || []
  return all.some((d) => (d.places || []).length > 0)
})

// --- [Methods: 로직 처리] ---

// 루트 탭 변경 시 호출
function selectRoute(idx) {
  selectedRouteIndex.value = idx
  selectedDay.value = dayList.value[0] ?? 1 // 1일차로 초기화
}

// API 응답 데이터를 프론트엔드에서 편집하기 편한 구조로 변환
// (각 장소에 고유값 _uid 부여 등)
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
      _uid: genUid(), // 화면 렌더링용 고유 ID 생성
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

// 순서 재정렬 함수 (1, 2, 3...)
function normalizeOrders(dayData) {
  dayData.places.forEach((p, idx) => {
    p.order = idx + 1
  })
}

// 고유 ID 생성기
function genUid() {
  return (
    globalThis.crypto?.randomUUID?.() ||
    `${Date.now()}-${Math.random().toString(16).slice(2)}`
  )
}

// 장소 추가 (검색 결과 선택 시)
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

// 장소 삭제
function removePlaceAt(idx) {
  const dayObj = selectedDayObj.value
  if (!dayObj) return
  dayObj.places.splice(idx, 1)
  normalizeOrders(dayObj)
}

// 장소 순서 이동
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

// 추천 요청 API 호출
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
    // 받아온 데이터를 편집 가능한 구조로 변환하여 저장
    results.value = (data || []).map((r) => toEditableRoute(r))
    selectedRouteIndex.value = 0
    selectedDay.value = 1
  } catch (e) {
    console.error(e)
    const serverMsg =
      e?.response?.data?.detail ||
      e?.response?.data?.message ||
      (typeof e?.response?.data === 'string' ? e.response.data : null)
    error.value = serverMsg || '추천 결과를 불러오는 중 오류가 발생했습니다.'
  } finally {
    loading.value = false
  }
}

// 루트 확정 저장 API 호출
async function handleConfirm(routeObj) {
  if (!confirm('이 루트를 확정해서 저장할까요?')) return
  saving.value = true
  try {
    const confirmPayload = mapRouteToConfirmPayload(routeObj)
    const { data } = await api.post('/routes/confirm/', confirmPayload)
    // 저장 성공 시 상세 페이지로 이동
    router.push({ name: 'route-detail', params: { routeId: data.id } })
  } catch (e) {
    console.error(e)
    alert('루트 저장 중 오류가 발생했습니다.')
  } finally {
    saving.value = false
  }
}

// 백엔드 API 포맷에 맞게 Payload 변환
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
        memo: p.memo ?? '',
      })),
    })),
  }
}

// 사진 토글 상태 관리
const selectedPlaceUid = ref(null)
function togglePlacePhoto(place) {
  // 이미 열린 사진을 다시 누르면 닫기(null), 아니면 해당 uid 설정
  selectedPlaceUid.value =
    selectedPlaceUid.value === place._uid ? null : place._uid
}

// 라이프사이클 훅
onMounted(fetchRecommendations)
watch(
  () => route.query,
  () => fetchRecommendations(),
  { deep: true }
)
</script>

<style scoped>
/* [페이지 레이아웃] */
.page-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 20px 100px;
  background-color: #f5f7fa; /* 연한 회색 배경 */
  min-height: 100vh;
  font-family: -apple-system, BlinkMacSystemFont, "Pretendard", Roboto, sans-serif;
}

/* 헤더 스타일 */
.header-section {
  text-align: center;
  margin-bottom: 40px;
}
.page-title {
  font-size: 2rem;
  font-weight: 800;
  color: #222;
  margin-bottom: 10px;
}
.page-subtitle {
  color: #666;
  font-size: 1.1rem;
}

/* 상태 카드 (로딩, 에러, 빈 상태 공통 스타일) */
.state-card {
  text-align: center;
  padding: 60px;
  background: white;
  border-radius: 20px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.05);
}
.error { color: #e74c3c; }
.actions { margin-top: 20px; }

/* 아웃라인 버튼 스타일 */
.btn-outline {
  padding: 10px 20px;
  border: 1px solid #ddd;
  border-radius: 8px;
  background: white;
  color: #555;
  text-decoration: none;
  font-weight: 600;
  transition: all 0.2s;
}
.btn-outline:hover { background: #f9f9f9; border-color: #ccc; }

/* [상단 탭] 추천 루트 1, 2, 3 선택 버튼 */
.route-tabs {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
}
.route-tab-btn {
  flex: 1; /* 너비 균등 분배 */
  padding: 16px;
  border: 1px solid #eee;
  background: white;
  border-radius: 12px;
  cursor: pointer;
  text-align: left;
  transition: all 0.2s;
}
.route-tab-btn:hover { background: #fcfcfc; }
.route-tab-btn.active {
  border-color: #2cb398;
  background: #e6f7f4; /* 활성화 시 민트색 배경 */
  color: #2cb398;
}
.tab-label {
  display: block;
  font-weight: 700;
  font-size: 1rem;
  margin-bottom: 4px;
}
.tab-desc-preview {
  font-size: 0.85rem;
  color: #666;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* [루트 상세 컨테이너] */
.route-detail-container {
  background: white;
  border-radius: 24px;
  padding: 32px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.03); /* 부드러운 그림자 */
}

/* 루트 정보 헤더 */
.route-info-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
  border-bottom: 1px solid #f0f0f0;
  padding-bottom: 24px;
}
.route-name {
  font-size: 1.6rem;
  font-weight: 800;
  color: #333;
  margin-bottom: 8px;
}
.route-description {
  color: #666;
  font-size: 1rem;
  line-height: 1.5;
}

/* 저장 버튼 스타일 */
.save-btn {
  padding: 12px 24px;
  background-color: #2cb398;
  color: white;
  border: none;
  border-radius: 12px;
  font-weight: 700;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}
.save-btn:hover:not(:disabled) {
  background-color: #249e85;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(44, 179, 152, 0.3);
}
.save-btn:disabled { opacity: 0.6; cursor: not-allowed; }

/* [DAY 탭] 가로 스크롤 가능 */
.day-tabs-wrapper {
  display: flex;
  gap: 10px;
  overflow-x: auto;
  padding-bottom: 10px;
  margin-bottom: 20px;
}
.day-pill {
  padding: 8px 16px;
  border: 1px solid #ddd;
  border-radius: 20px;
  background: white;
  color: #555;
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.2s;
}
.day-pill.active {
  background-color: #333; /* 활성화 시 진한 회색 */
  color: white;
  border-color: #333;
}

/* [지도 섹션] 상단 배치, 높이 고정 */
.map-section {
  width: 100%;
  height: 400px; /* 시원시원한 높이 */
  border-radius: 16px;
  overflow: hidden;
  margin-bottom: 30px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.05);
  border: 1px solid #eee;
}
/* KakaoMap 컴포넌트 스타일 오버라이딩 */
.big-map { width: 100%; height: 100%; }

/* [장소 리스트 섹션] */
.search-box-wrapper { margin-bottom: 20px; }
.guide-text {
  text-align: center;
  color: #888;
  font-size: 0.9rem;
  margin-bottom: 16px;
}

.place-list {
  list-style: none;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* 장소 카드 스타일 */
.place-card {
  background: white;
  border: 1px solid #eee;
  border-radius: 16px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.2s;
}
.place-card:hover {
  border-color: #2cb398;
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
  transform: translateX(4px); /* 호버 시 살짝 오른쪽 이동 */
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.place-title-group {
  display: flex;
  align-items: center;
  gap: 10px;
}
.order-badge {
  background-color: #333;
  color: white;
  width: 24px; height: 24px;
  border-radius: 50%;
  display: flex; justify-content: center; align-items: center;
  font-size: 0.8rem;
  font-weight: 700;
}
.place-name {
  font-size: 1.1rem;
  font-weight: 700;
  color: #333;
}
.kakaomap-link {
  font-size: 0.8rem;
  color: #2cb398;
  text-decoration: none;
  background: #e6f7f4;
  padding: 2px 6px;
  border-radius: 4px;
}
.kakaomap-link:hover { text-decoration: underline; }

.place-address {
  color: #666;
  font-size: 0.9rem;
  padding-left: 34px; /* 뱃지 너비만큼 들여쓰기 */
}

/* 액션 버튼들 (순서변경, 삭제) */
.action-buttons {
  display: flex;
  gap: 6px;
}
.icon-btn {
  width: 32px; height: 32px;
  border: 1px solid #eee;
  background: white;
  border-radius: 8px;
  cursor: pointer;
  display: flex; justify-content: center; align-items: center;
  font-size: 0.8rem;
  color: #555;
  transition: all 0.2s;
}
.icon-btn:hover:not(:disabled) { background: #f5f5f5; border-color: #ccc; }
.icon-btn:disabled { opacity: 0.4; cursor: not-allowed; }
.delete-btn:hover { background: #fff5f5; border-color: #ffcccc; color: #e74c3c; }

/* 사진 표시 영역 (들여쓰기 적용) */
.place-photo-wrapper {
  margin-top: 16px;
  padding-left: 34px;
}
.place-img {
  width: 100%;
  max-width: 400px; /* 너무 커지지 않게 제한 */
  border-radius: 12px;
  border: 1px solid #eee;
  box-shadow: 0 4px 10px rgba(0,0,0,0.05);
}

/* 사진 토글 애니메이션 (Vue Transition) */
.slide-fade-enter-active { transition: all 0.3s ease-out; }
.slide-fade-leave-active { transition: all 0.3s cubic-bezier(1, 0.5, 0.8, 1); }
.slide-fade-enter-from, .slide-fade-leave-to { transform: translateY(-10px); opacity: 0; }

.empty-state {
  text-align: center;
  padding: 40px;
  color: #999;
  border: 2px dashed #eee;
  border-radius: 16px;
  margin-top: 20px;
}

/* 로딩 스피너 애니메이션 */
.spinner {
  width: 40px; height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #2cb398;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }

/* 모바일 대응 (반응형) */
@media (max-width: 768px) {
  .route-info-header { flex-direction: column; gap: 16px; }
  .save-btn { width: 100%; }
  .route-tabs { overflow-x: auto; padding-bottom: 10px; } /* 탭 스크롤 */
  .route-tab-btn { min-width: 200px; }
}
</style>