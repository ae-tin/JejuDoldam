<!-- src/views/RouteRecommendView.vue -->
<template>
  <div class="page">
    <h2>제주 여행 루트 추천 결과</h2>

    <!-- ✅ 로딩/에러/가드 -->
    <div v-if="loading" class="card">추천 결과 불러오는 중...</div>

    <div v-else-if="error" class="card error">
      {{ error }}
      <div class="actions">
        <!-- 입력 페이지로만 다시 가면 됨(조건 재입력 UI는 굳이 여기서 제공 안 함) -->
        <RouterLink class="btn" to="/routes/recommend">추천 입력으로 돌아가기</RouterLink>
      </div>
    </div>

    <!-- ✅ 추천 루트 탭 -->
    <div v-else-if="results.length" class="tabs">
      <button
        v-for="(r, idx) in results"
        :key="r.id ?? idx"
        class="tab"
        :class="{ active: idx === selectedRouteIndex }"
        @click="selectRoute(idx)"
        type="button"
      >
        추천루트 {{ idx + 1 }}
      </button>
    </div>

    <!-- ✅ 추천 내용 + DAY 탭 + 편집 + 지도 -->
    <div v-if="selectedRoute" class="layout">
      <!-- 왼쪽: 리스트/탭/편집 -->
      <section class="card left">
        <div class="titleRow">
          <div>
            <h3 class="routeTitle">{{ selectedRoute.title }}</h3>
            <p class="routeDesc">{{ selectedRoute.description }}</p>
          </div>

          <!-- ✅ 현재 편집 상태 그대로 저장 -->
          <button
            class="btn"
            type="button"
            :disabled="saving || !canSave"
            @click="handleConfirm(selectedRoute)"
            title="현재 편집 상태 그대로 저장됩니다."
          >
            {{ saving ? '저장 중...' : '이 루트 확정 저장' }}
          </button>
        </div>

        <!-- DAY 탭 -->
        <div class="dayTabs">
          <button
            v-for="d in dayList"
            :key="d"
            class="dayTab"
            :class="{ active: d === selectedDay }"
            @click="selectedDay = d"
            type="button"
          >
            DAY {{ d }}
          </button>
        </div>

        <!-- ✅ 장소 검색 → 선택한 장소를 현재 DAY에 추가 -->
        <KakaoPlaceSearch @select="addPlaceToSelectedDay" />

        <ul class="placeList">
          <li v-for="(p, idx) in dayPlaces" :key="p._uid" class="placeItem">
            <div class="placeTop">
              <b>{{ p.order }}. {{ p.name }}</b>

              <div class="miniBtns">
                <button type="button" class="mini" @click="movePlace(idx, -1)" :disabled="idx === 0">
                  ▲
                </button>
                <button
                  type="button"
                  class="mini"
                  @click="movePlace(idx, 1)"
                  :disabled="idx === dayPlaces.length - 1"
                >
                  ▼
                </button>
                <button type="button" class="mini danger" @click="removePlaceAt(idx)">
                  삭제
                </button>
              </div>
            </div>

            <div class="placeAddr">{{ p.address || '주소 없음' }}</div>
          </li>
        </ul>

        <p v-if="!dayPlaces.length" class="mutedSmall">
          아직 DAY {{ selectedDay }}에 장소가 없습니다. 위에서 검색해서 추가해보세요.
        </p>
      </section>

      <!-- 오른쪽: 지도 -->
      <section class="card right">
        <!-- 지도는 “현재 DAY의 장소들(dayPlaces)”만 받음 -->
        <KakaoMap :places="dayPlaces" />
      </section>
    </div>

    <p v-else-if="!loading" class="muted">
      추천 결과가 없습니다. 입력 페이지에서 추천을 먼저 받아주세요.
    </p>
  </div>
</template>

<script setup>
/**
 * ✅ 프론트 최소 이해 세트(이 파일에서 꼭 알아야 할 것)
 *
 * 1) 어떤 이벤트가 발생?
 *  - 추천루트 탭 클릭(selectRoute)
 *  - DAY 탭 클릭(selectedDay 변경)
 *  - 장소 검색에서 “추가”(addPlaceToSelectedDay)
 *  - ▲▼로 순서 변경(movePlace)
 *  - 삭제(removePlaceAt)
 *  - “이 루트 확정 저장”(handleConfirm)
 *
 * 2) 어떤 API 호출?
 *  - 페이지 진입 시: POST /routes/recommend/ (추천 결과 3개 받아오기)
 *  - 저장 버튼: POST /routes/confirm/ (현재 편집 상태를 DB에 저장)
 *
 * 3) 응답은 어디에 저장?
 *  - results(ref 배열)에 저장 → 탭/리스트/지도 렌더링에 사용
 */

import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute, RouterLink } from 'vue-router'
import api from '@/api/client'
import KakaoMap from '@/components/KakaoMap.vue'
import KakaoPlaceSearch from '@/components/KakaoPlaceSearch.vue'

const router = useRouter()
const route = useRoute()

/** 화면 상태 */
const loading = ref(false)
const saving = ref(false)
const error = ref('')

/** 추천 결과(편집 가능한 형태로 가공해서 저장) */
const results = ref([])

/** 탭/선택 상태 */
const selectedRouteIndex = ref(0)
const selectedDay = ref(1)

/** 현재 선택된 루트 */
const selectedRoute = computed(() => results.value[selectedRouteIndex.value] || null)

/**
 * ✅ 입력 페이지(/routes/recommend)에서 넘어온 query를 payload로 변환
 * - days, companion_type, companion_cnt, style, themes(쉼표 join된 문자열)
 */
const recommendPayload = computed(() => {
  const q = route.query

  const days = Number(q.days)
  const companion_cnt = Number(q.companion_cnt)

  // themes: "힐링,일상탈출" 같은 문자열 → ["힐링", "일상탈출"]
  const themes = (q.themes ? String(q.themes).split(',').filter(Boolean) : [])

  return {
    days,
    companion_type: q.companion_type ? String(q.companion_type) : '',
    companion_cnt,
    style: q.style ? String(q.style) : '',
    themes,
  }
})

/** query가 정상인지(필수값 최소 체크) */
const canRecommend = computed(() => {
  const p = recommendPayload.value
  return (
    Number.isFinite(p.days) && p.days >= 1 && p.days <= 8 &&
    Number.isFinite(p.companion_cnt) && p.companion_cnt >= 0 && p.companion_cnt <= 16 &&
    !!p.companion_type &&
    !!p.style
  )
})

/**
 * ✅ dayList: 선택된 route의 days(1~N)
 * - 응답에 days가 없으면 payload.days를 사용
 */
const dayList = computed(() => {
  if (!selectedRoute.value) return []
  const n = Number(selectedRoute.value.days || recommendPayload.value.days || 1)
  return Array.from({ length: n }, (_, i) => i + 1)
})

/** 선택된 day 객체 */
const selectedDayObj = computed(() => {
  if (!selectedRoute.value) return null
  return selectedRoute.value.daysData?.find((d) => d.day === selectedDay.value) || null
})

/** 현재 DAY 장소들 */
const dayPlaces = computed(() => {
  const arr = selectedDayObj.value?.places || []
  // 안전하게 order 기준 정렬해서 지도/리스트 순서 보장
  return arr.slice().sort((a, b) => (a.order ?? 0) - (b.order ?? 0))
})

/** 저장 가능 조건: 전체 day 중 하나라도 장소가 있으면 저장 가능 */
const canSave = computed(() => {
  if (!selectedRoute.value) return false
  const all = selectedRoute.value.daysData || []
  return all.some((d) => (d.places || []).length > 0)
})

/**
 * 추천 결과 탭 클릭 이벤트
 * - 선택 route 바꾸고, day는 1일차로 초기화
 */
function selectRoute(idx) {
  selectedRouteIndex.value = idx
  selectedDay.value = dayList.value[0] ?? 1
}

/** 추천 응답 -> 편집 가능한 구조로 변환 */
function toEditableRoute(r) {
  // 응답에 days가 없다면 payload 기준으로 fallback
  const days = Number(r.days ?? recommendPayload.value.days ?? 1)

  const daysData = Array.from({ length: days }, (_, i) => ({
    day: i + 1,
    places: [],
  }))

  // r.places: [{day, order, name, address, latitude, longitude, memo...}]
  for (const p of r.places || []) {
    const day = Number(p.day ?? 1)
    const target = daysData[day - 1]
    if (!target) continue

    target.places.push({
      _uid: genUid(), // 프론트에서 렌더링 key로 쓰는 고유값
      order: p.order ?? target.places.length + 1,
      name: p.name,
      address: p.address ?? '',
      latitude: p.latitude ?? null,
      longitude: p.longitude ?? null,
      memo: p.memo ?? '',
    })
  }

  // order 정규화(1,2,3,...)
  for (const d of daysData) normalizeOrders(d)

  return { ...r, days, daysData }
}

function normalizeOrders(dayData) {
  dayData.places.forEach((p, idx) => {
    p.order = idx + 1
  })
}

/** uid 생성(브라우저 호환) */
function genUid() {
  return (
    globalThis.crypto?.randomUUID?.() ||
    `${Date.now()}-${Math.random().toString(16).slice(2)}`
  )
}

/** ✅ 검색 결과로 넘어온 place를 현재 DAY에 추가 */
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

/**
 * ✅ 페이지 진입 시 자동 추천 호출
 * - 입력 페이지에서 query를 싣고 넘어오면 여기서 API 호출함
 */
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

    // 탭/일차 초기화
    selectedRouteIndex.value = 0
    selectedDay.value = 1
  } catch (e) {
    console.error(e)

    // 서버가 validation errors 내려주면 최대한 보여주기
    const serverMsg =
      e?.response?.data?.detail ||
      e?.response?.data?.message ||
      (typeof e?.response?.data === 'string' ? e.response.data : null)

    error.value = serverMsg || '추천 결과를 불러오는 중 오류가 발생했습니다.'
  } finally {
    loading.value = false
  }
}

/**
 * ✅ 확정 저장 버튼
 * - 현재 편집 상태(route.daysData)를 payload로 만들어서 백엔드에 저장
 * - 저장 성공하면 상세 페이지로 이동
 */
async function handleConfirm(routeObj) {
  if (!confirm('이 루트를 확정해서 저장할까요?')) return
  saving.value = true

  try {
    const confirmPayload = mapRouteToConfirmPayload(routeObj)
    const { data } = await api.post('/routes/confirm/', confirmPayload)

    router.push({ name: 'route-detail', params: { routeId: data.id } })
  } catch (e) {
    console.error(e)
    alert('루트 저장 중 오류가 발생했습니다.')
  } finally {
    saving.value = false
  }
}

/** daysData 기반 payload 생성 */
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

/**
 * ✅ 실행 흐름(요청→처리→응답)
 * - 요청: 페이지 진입(onMounted) / query 변경(watch)
 * - 처리: fetchRecommendations()가 API 호출
 * - 응답: results에 저장 → 화면/지도 렌더링
 */
onMounted(fetchRecommendations)

/** query가 바뀌면(입력 페이지에서 다시 넘어온 경우) 자동으로 재호출 */
watch(
  () => route.query,
  () => fetchRecommendations(),
  { deep: true }
)
</script>

<style scoped>
.page { max-width: 1100px; margin: 0 auto; padding-bottom: 50px; }
.card { border: 1px solid #eee; border-radius: 12px; padding: 16px; background: #fff; }
.error { color: #dc2626; }
.actions { margin-top: 10px; }
.btn { padding: 10px 12px; border: 1px solid #ddd; border-radius: 10px; background: #fff; cursor: pointer; text-decoration:none; color: inherit; display:inline-block; }
.btn:disabled { opacity: 0.6; cursor: not-allowed; }

.tabs { display: flex; gap: 8px; margin: 14px 0; }
.tab { padding: 10px 12px; border: 1px solid #ddd; border-radius: 10px; background:#fff; cursor:pointer; }
.tab.active { border-color: #111827; font-weight: 700; }

.layout { display: grid; grid-template-columns: 380px 1fr; gap: 16px; margin-top: 14px; }
.titleRow { display:flex; justify-content: space-between; align-items:flex-start; gap: 10px; }
.routeTitle { margin: 0 0 6px; }
.routeDesc { margin: 0; color:#555; font-size: 13px; }

.dayTabs { display:flex; gap: 8px; margin: 14px 0; flex-wrap: wrap; }
.dayTab { padding: 8px 10px; border:1px solid #ddd; border-radius: 999px; background:#fff; cursor:pointer; font-size: 13px; }
.dayTab.active { border-color:#111827; font-weight:700; }

.placeList { list-style:none; padding:0; margin: 12px 0 0; display:flex; flex-direction:column; gap: 10px; }
.placeItem { border:1px solid #f0f0f0; border-radius: 10px; padding: 10px; }
.placeTop { display:flex; align-items:center; gap: 10px; }
.placeAddr { color:#666; font-size: 12px; margin-top: 6px; }

.miniBtns { margin-left:auto; display:flex; gap: 6px; }
.mini { padding: 6px 10px; border:1px solid #ddd; border-radius: 999px; background:#fff; cursor:pointer; font-size: 12px; }
.mini:disabled { opacity: 0.5; cursor:not-allowed; }
.mini.danger { border-color:#fca5a5; }

.muted { margin-top: 16px; color:#666; }
.mutedSmall { margin-top: 10px; color:#777; font-size: 12px; }

@media (max-width: 900px) {
  .layout { grid-template-columns: 1fr; }
}

.slider-wrapper {
  width: 100%;
  max-width: 360px;
}

.slider {
  width: 100%;
  margin: 12px 0;
}

.labels {
  display: flex;
  justify-content: space-between;
  font-size: 14px;
}

.current {
  font-weight: 600;
}

</style>
