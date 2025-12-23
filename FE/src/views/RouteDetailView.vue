<template>
  <div class="page">
    <div class="topRow">
      <div>
        <h2 class="title">저장한 루트 상세</h2>
        <p class="sub">DAY별 장소를 추가/삭제/순서변경해서 바로 저장할 수 있어요.</p>
      </div>

      <div class="topActions">
        <button class="btn" type="button" @click="reload" :disabled="loading">
          새로고침
        </button>
      </div>
    </div>

    <div v-if="loading" class="card">불러오는 중...</div>
    
    <div v-else-if="error" class="card error">{{ error }}</div>

    <div v-else-if="route" class="layout">
      
      <section class="card left">
        
        <div class="routeMeta">
          <div class="metaRow">
            <label class="label">제목</label>
            <input class="input" v-model="edit.title" type="text" />
          </div>
          <div class="metaRow">
            <label class="label">설명</label>
            <input class="input" v-model="edit.description" type="text" placeholder="(선택)" />
          </div>

          <div class="metaActions">
            <button class="btn primary" type="button" @click="saveRouteMeta" :disabled="metaSaving">
              {{ metaSaving ? '저장 중...' : '수정사항 저장' }}
            </button>
          </div>
        </div>

        <hr class="hr" />

        <div class="dayTabs">
          <button v-for="d in sortedDays" :key="d.id" class="dayTab" :class="{ active: d.id === selectedDayId }"
            type="button" @click="selectedDayId = d.id">
            DAY {{ d.day }}
          </button>

          <button class="dayPlus" type="button" @click="addDay" :disabled="daySaving">
            + DAY
          </button>
        </div>

        <div v-if="selectedDay" class="dayHeader">
          <div class="dayTitle">
            <b>DAY {{ selectedDay.day }}</b>
            <span class="mutedSmall">({{ dayPlaces.length }}곳)</span>
          </div>

          <button class="mini danger" type="button" @click="deleteDay" :disabled="daySaving">
            DAY 삭제
          </button>
        </div>

        <KakaoPlaceSearch v-if="selectedDay" @select="addPlaceToSelectedDay" />

        <p v-if="dayPlaces.length" class="routeDesc" style="margin-top: 10px; text-align: center;">
          클릭시 사진이 나타나요!
        </p>

        <ul v-if="selectedDay" class="placeList">
          <li 
            v-for="(p, idx) in dayPlaces" 
            :key="p.id" 
            class="placeItem" 
            @click="togglePlacePhoto(p)"
          >
            <div class="placeTop">
              <b>{{ idx + 1 }}. {{ p.name }}
                <a 
                  v-if="p.place_url" 
                  class="link" 
                  :href="p.place_url" 
                  target="_blank" 
                  rel="noreferrer"
                  @click.stop
                >
                  링크
                </a>
              </b>

              <div class="miniBtns" @click.stop>
                <button class="mini" type="button" @click="movePlace(idx, -1)" :disabled="idx === 0 || placeBusy">
                  ▲
                </button>
                <button class="mini" type="button" @click="movePlace(idx, 1)"
                  :disabled="idx === dayPlaces.length - 1 || placeBusy">
                  ▼
                </button>
                <button class="mini danger" type="button" @click="removePlace(p.id)" :disabled="placeBusy">
                  삭제
                </button>
              </div>
            </div>

            <div class="placeAddr">{{ p.address || '주소 정보 없음' }}</div>

            <input class="memo" v-model="p.memo" type="text" placeholder="메모(선택)"
              @blur="savePlaceMemo(p)" :disabled="placeBusy" @click.stop />

            <div v-if="selectedPlaceId === p.id && p.photo_url" class="placePhoto">
              <img :src="p.photo_url" :alt="p.name" />
            </div>
          </li>
        </ul>

        <p v-if="selectedDay && !dayPlaces.length" class="mutedSmall" style="margin-top:10px;">
          아직 장소가 없습니다. 위에서 검색해서 추가해보세요.
        </p>
      </section>

      <section class="card right">
        <KakaoMap :places="dayPlaces" />
      </section>
    </div>
  </div>
</template>

<script setup>
// Vue 및 라우터 라이브러리 임포트
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router' // 페이지 이동을 위해 useRouter 추가
import api from '@/api/client'
import KakaoMap from '@/components/KakaoMap.vue'
import KakaoPlaceSearch from '@/components/KakaoPlaceSearch.vue'

// 라우터 객체 초기화
const routeParam = useRoute()  // 현재 URL 파라미터 확인용
const router = useRouter()     // 페이지 이동(push)용

// --- [상태 변수 선언] ---
const loading = ref(false)   // 전체 데이터 로딩 상태
const error = ref('')        // 에러 메시지
const route = ref(null)      // 서버에서 받아온 루트 전체 데이터

const selectedDayId = ref(null) // 현재 선택된 DAY의 DB ID

// 각 작업별 로딩 상태 (버튼 중복 클릭 방지)
const metaSaving = ref(false) // 제목/설명 저장 중?
const daySaving = ref(false)  // DAY 추가/삭제 중?
const placeBusy = ref(false)  // 장소 추가/삭제/이동 중?

// 사진 토글을 위한 선택된 장소 ID
const selectedPlaceId = ref(null)

// 제목/설명 수정을 위한 임시 변수 (v-model 연결)
const edit = ref({
  title: '',
  description: '',
})

// --- [Computed 속성] ---

// DAY 목록을 날짜 순서(day 오름차순)로 정렬하여 반환
const sortedDays = computed(() => {
  const days = route.value?.days || []
  return [...days].sort((a, b) => a.day - b.day)
})

// 현재 선택된 DAY 객체 찾기
const selectedDay = computed(() => {
  if (!route.value) return null
  return (route.value.days || []).find(d => d.id === selectedDayId.value) || null
})

// 현재 선택된 DAY의 장소 목록 (순서(order)대로 정렬)
const dayPlaces = computed(() => {
  const d = selectedDay.value
  if (!d) return []
  const places = d.places || []
  return [...places].sort((a, b) => (a.order ?? 0) - (b.order ?? 0))
})

// --- [Life Cycle] ---
onMounted(() => {
  reload() // 컴포넌트가 켜지면 데이터 로드 시작
})

// --- [메서드 구현] ---

// 사진 토글 함수: 이미 열려있으면 닫고(null), 아니면 해당 ID 설정
function togglePlacePhoto(place) {
  selectedPlaceId.value = selectedPlaceId.value === place.id ? null : place.id
}

// 데이터 불러오기 함수
async function reload() {
  loading.value = true
  error.value = ''
  selectedPlaceId.value = null // 새로고침 시 열린 사진 닫기
  try {
    const routeId = routeParam.params.routeId
    // GET /routes/{id}/ API 호출
    const { data } = await api.get(`/routes/${routeId}/`)

    route.value = data
    // 편집용 변수에 데이터 복사
    edit.value.title = data.title || ''
    edit.value.description = data.description || ''

    // 데이터 로드 후 첫 번째 DAY를 기본으로 선택
    const first = [...(data.days || [])].sort((a, b) => a.day - b.day)[0]
    selectedDayId.value = first?.id ?? null
  } catch (e) {
    console.error(e)
    error.value = parseDRFError(e) || '루트 정보를 불러오지 못했습니다.'
  } finally {
    loading.value = false
  }
}

// ✅ [핵심 기능] 수정사항 저장 (제목/설명 저장 후 페이지 이동)
async function saveRouteMeta() {
  if (!route.value) return
  metaSaving.value = true // 로딩 시작
  
  try {
    const routeId = route.value.id
    
    // 1. 서버에 PUT 요청으로 제목과 설명을 저장합니다.
    const { data } = await api.put(`/routes/${routeId}/`, {
      title: edit.value.title,
      description: edit.value.description,
    })
    
    // 2. 로컬 상태 업데이트 (화면 갱신)
    route.value.title = data.title
    route.value.description = data.description

    // 3. 사용자에게 저장 완료 알림
    alert('수정사항이 저장되었습니다!')

    // 4. 마이페이지의 '저장한 경로' 탭으로 이동
    // (사용자는 장소 변경까지 이때 다 저장된 것으로 인지하게 됩니다)
    router.push({ path: '/mypage', query: { tab: 'routes' } })

  } catch (e) {
    console.error(e)
    alert(parseDRFError(e) || '저장에 실패했습니다.')
  } finally {
    metaSaving.value = false // 로딩 끝
  }
}

// DAY 추가 함수
async function addDay() {
  if (!route.value) return
  daySaving.value = true
  try {
    const routeId = route.value.id
    // 현재 가장 큰 day 번호를 찾아 +1
    const maxDay = Math.max(0, ...(route.value.days || []).map(d => d.day))
    const nextDay = maxDay + 1

    // POST /routes/{id}/days/
    const { data } = await api.post(`/routes/${routeId}/days/`, { day: nextDay })
    
    // 배열에 추가하고 바로 해당 DAY 선택
    route.value.days.push(data)
    selectedDayId.value = data.id
  } catch (e) {
    console.error(e)
    alert(parseDRFError(e) || 'DAY 추가에 실패했습니다.')
  } finally {
    daySaving.value = false
  }
}

// DAY 삭제 함수
async function deleteDay() {
  if (!selectedDay.value) return
  if (!confirm(`DAY ${selectedDay.value.day}를 삭제할까요? (해당 DAY의 장소도 모두 삭제됩니다)`)) return

  daySaving.value = true
  try {
    const dayId = selectedDay.value.id
    // DELETE /routes/days/{dayId}/
    await api.delete(`/routes/days/${dayId}/`)

    // 로컬 배열에서 제거
    route.value.days = (route.value.days || []).filter(d => d.id !== dayId)

    // 삭제 후 첫 번째 DAY로 포커스 이동
    const first = sortedDays.value[0]
    selectedDayId.value = first?.id ?? null
  } catch (e) {
    console.error(e)
    alert(parseDRFError(e) || 'DAY 삭제에 실패했습니다.')
  } finally {
    daySaving.value = false
  }
}

// 장소 추가 함수 (검색 결과 선택 시 호출)
async function addPlaceToSelectedDay(place) {
  const d = selectedDay.value
  if (!d) return

  placeBusy.value = true
  try {
    // 현재 장소들의 order 중 가장 큰 값 + 1 로 순서 지정
    const orders = (d.places || []).map(p => Number(p.order || 0))
    const nextOrder = (orders.length ? Math.max(...orders) : 0) + 1

    // API에 보낼 데이터 구성 (사진 URL 포함)
    const payload = {
      order: nextOrder,
      name: place.name,
      address: place.address ?? '',
      latitude: place.latitude ?? null,
      longitude: place.longitude ?? null,
      place_url: place.place_url ?? '',
      photo_url: place.photo_url ?? '', 
      memo: '',
    }

    // POST /routes/days/{dayId}/places/
    const { data } = await api.post(`/routes/days/${d.id}/places/`, payload)
    d.places.push(data) // 화면에 즉시 반영
  } catch (e) {
    console.error(e)
    alert(parseDRFError(e) || '장소 추가에 실패했습니다.')
  } finally {
    placeBusy.value = false
  }
}

// 장소 삭제 함수
async function removePlace(placeId) {
  const d = selectedDay.value
  if (!d) return
  if (!confirm('이 장소를 삭제할까요?')) return

  placeBusy.value = true
  try {
    // DELETE /routes/places/{placeId}/
    await api.delete(`/routes/places/${placeId}/`)
    d.places = (d.places || []).filter(p => p.id !== placeId)
    
    // 삭제 후 순서가 비지 않도록 재정렬 (1, 3, 4 -> 1, 2, 3)
    await persistReorder(d)
  } catch (e) {
    console.error(e)
    alert(parseDRFError(e) || '장소 삭제에 실패했습니다.')
  } finally {
    placeBusy.value = false
  }
}

// 장소 순서 이동 (위/아래 화살표)
async function movePlace(idx, dir) {
  const d = selectedDay.value
  if (!d) return

  // 현재 순서대로 정렬된 배열 복사
  const arr = [...(d.places || [])].sort((a, b) => (a.order ?? 0) - (b.order ?? 0))
  const next = idx + dir
  
  // 범위 벗어나면 무시
  if (next < 0 || next >= arr.length) return

  // 배열 내에서 위치 교환 (Swap)
  const tmp = arr[idx]
  arr[idx] = arr[next]
  arr[next] = tmp

  // 로컬 order 값 재할당
  arr.forEach((p, i) => { p.order = i + 1 })
  d.places = arr

  placeBusy.value = true
  try {
    // DB에 바뀐 순서 저장
    await persistReorder(d)
  } catch (e) {
    console.error(e)
    alert(parseDRFError(e) || '순서 저장에 실패했습니다. 새로고침 후 다시 시도해주세요.')
    await reload() // 실패 시 데이터 원복을 위해 새로고침
  } finally {
    placeBusy.value = false
  }
}

// 순서 재정렬 및 DB 저장 로직
async function persistReorder(dayObj) {
  const places = [...(dayObj.places || [])].sort((a, b) => (a.order ?? 0) - (b.order ?? 0))
  if (!places.length) return

  // [DB Unique 제약 조건 회피용 트릭]
  // 1. 먼저 모든 순서를 1000번대 임시 값으로 변경
  for (let i = 0; i < places.length; i++) {
    await api.patch(`/routes/places/${places[i].id}/`, { order: 1000 + i + 1 })
  }

  // 2. 다시 1번부터 차례대로 올바른 순서 부여
  for (let i = 0; i < places.length; i++) {
    const finalOrder = i + 1
    const { data } = await api.patch(`/routes/places/${places[i].id}/`, { order: finalOrder })
    places[i].order = data.order
  }

  dayObj.places = places
}

// 메모 저장 함수 (input blur 시 호출)
async function savePlaceMemo(p) {
  if (!p?.id) return
  try {
    await api.patch(`/routes/places/${p.id}/`, { memo: p.memo ?? '' })
  } catch (e) {
    console.error(e)
    // 메모 저장은 실패해도 사용자에게 굳이 알리지 않음 (조용한 실패)
  }
}

// Django REST Framework 에러 메시지 파싱 헬퍼
function parseDRFError(err) {
  const data = err?.response?.data
  if (!data) return ''

  if (typeof data === 'string') return data
  if (data.detail && typeof data.detail === 'string') return data.detail

  // { field: ["error message"] } 형태일 때
  if (typeof data === 'object') {
    const msgs = []
    for (const [k, v] of Object.entries(data)) {
      if (Array.isArray(v)) msgs.push(`${k}: ${v.join(' / ')}`)
      else if (typeof v === 'string') msgs.push(`${k}: ${v}`)
    }
    return msgs.join('\n')
  }
  return ''
}
</script>

<style scoped>
.page {
  max-width: 1200px;
  margin: 0 auto;
}

.card {
  border: 1px solid #eee;
  border-radius: 12px;
  padding: 16px;
  background: #fff;
}

.error {
  color: #dc2626;
}

.topRow {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 10px;
  margin: 10px 0 14px;
}

.title {
  margin: 0;
}

.sub {
  margin: 6px 0 0;
  color: #666;
  font-size: 13px;
}

.topActions {
  display: flex;
  gap: 8px;
}

.layout {
  display: grid;
  grid-template-columns: 420px 1fr;
  gap: 16px;
  margin-top: 14px;
}

.left {
  min-height: 520px;
}

.right {
  min-height: 520px;
  display: flex;
}

.routeMeta {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.metaRow {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.label {
  font-size: 12px;
  color: #555;
}

.input {
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 10px;
}

.metaActions {
  display: flex;
  justify-content: flex-end;
}

.hr {
  border: none;
  border-top: 1px solid #f0f0f0;
  margin: 14px 0;
}

.dayTabs {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.dayTab {
  padding: 8px 10px;
  border: 1px solid #ddd;
  border-radius: 999px;
  background: #fff;
  cursor: pointer;
  font-size: 13px;
}

.dayTab.active {
  border-color: #111827;
  font-weight: 700;
}

.dayPlus {
  padding: 8px 10px;
  border: 1px dashed #ddd;
  border-radius: 999px;
  background: #fff;
  cursor: pointer;
  font-size: 13px;
  color: #555;
}

.dayHeader {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin: 12px 0;
}

.dayTitle {
  display: flex;
  align-items: baseline;
  gap: 8px;
}

.placeList {
  list-style: none;
  padding: 0;
  margin: 12px 0 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

/* 리스트 아이템에 클릭 가능 커서 추가 */
.placeItem {
  border: 1px solid #f0f0f0;
  border-radius: 10px;
  padding: 10px;
  cursor: pointer;
}
.placeItem:hover {
  background-color: #fcfcfc;
}

.placeTop {
  display: flex;
  align-items: center;
  gap: 10px;
}

.placeAddr {
  color: #666;
  font-size: 12px;
  margin-top: 6px;
}

.memo {
  width: 100%;
  margin-top: 8px;
  padding: 10px 12px;
  border: 1px solid #eee;
  border-radius: 10px;
  font-size: 13px;
}

.miniBtns {
  margin-left: auto;
  display: flex;
  gap: 6px;
}

.btn {
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 10px;
  background: #fff;
  cursor: pointer;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 저장 버튼 강조 스타일 */
.btn.primary {
  background-color: #111827;
  color: white;
  border-color: #111827;
}
.btn.primary:disabled {
  background-color: #6b7280;
  border-color: #6b7280;
}

.mini {
  padding: 6px 10px;
  border: 1px solid #ddd;
  border-radius: 999px;
  background: #fff;
  cursor: pointer;
  font-size: 12px;
}

.mini:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.danger {
  border-color: #fca5a5;
  color: #991b1b;
}

.mutedSmall {
  color: #777;
  font-size: 12px;
}

/* 링크 스타일 */
.link {
  font-size: 12px;
  color: #2563eb;
  text-decoration: none;
  margin-left: 6px;
}
.link:hover { text-decoration: underline; }

/* 사진 표시 스타일 */
.placePhoto {
  margin-top: 10px;
}

.placePhoto img {
  width: 100%;
  max-height: 220px;
  object-fit: cover;
  border-radius: 10px;
  border: 1px solid #eee;
}

.routeDesc { margin: 0; color:#555; font-size: 13px; }

@media (max-width: 900px) {
  .layout {
    grid-template-columns: 1fr;
  }

  .right {
    min-height: 420px;
  }
}
</style>