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
      <!-- 왼쪽 -->
      <section class="card left">
        <!-- 루트 제목/설명 (간단 편집) -->
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
            <button class="btn" type="button" @click="saveRouteMeta" :disabled="metaSaving">
              {{ metaSaving ? '저장 중...' : '제목/설명 저장' }}
            </button>
          </div>
        </div>

        <hr class="hr" />

        <!-- DAY 탭 -->
        <div class="dayTabs">
          <button v-for="d in sortedDays" :key="d.id" class="dayTab" :class="{ active: d.id === selectedDayId }"
            type="button" @click="selectedDayId = d.id">
            DAY {{ d.day }}
          </button>

          <button class="dayPlus" type="button" @click="addDay" :disabled="daySaving">
            + DAY
          </button>
        </div>

        <!-- 선택 DAY 정보 -->
        <div v-if="selectedDay" class="dayHeader">
          <div class="dayTitle">
            <b>DAY {{ selectedDay.day }}</b>
            <span class="mutedSmall">({{ dayPlaces.length }}곳)</span>
          </div>

          <button class="mini danger" type="button" @click="deleteDay" :disabled="daySaving">
            DAY 삭제
          </button>
        </div>

        <!-- 장소 검색 -> 현재 DAY에 추가 -->
        <KakaoPlaceSearch v-if="selectedDay" @select="addPlaceToSelectedDay" />

        <!-- 장소 목록 -->
        <ul v-if="selectedDay" class="placeList">
          <li v-for="(p, idx) in dayPlaces" :key="p.id" class="placeItem">
            <div class="placeTop">
              <b>{{ idx + 1 }}. {{ p.name }}</b>

              <div class="miniBtns">
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

            <div class="placeAddr">{{ p.address || '주소 없음' }}</div>

            <!-- (선택) 메모 수정 -->
            <input class="memo" v-model="p.memo" type="text" placeholder="메모(선택) — 입력 후 포커스가 빠지면 저장"
              @blur="savePlaceMemo(p)" :disabled="placeBusy" />
          </li>
        </ul>

        <p v-if="selectedDay && !dayPlaces.length" class="mutedSmall" style="margin-top:10px;">
          아직 장소가 없습니다. 위에서 검색해서 추가해보세요.
        </p>
      </section>

      <!-- 오른쪽: 지도 -->
      <section class="card right">
        <KakaoMap :places="dayPlaces" />
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '@/api/client'
import KakaoMap from '@/components/KakaoMap.vue'
import KakaoPlaceSearch from '@/components/KakaoPlaceSearch.vue'

const routeParam = useRoute()

const loading = ref(false)
const error = ref('')
const route = ref(null)

const selectedDayId = ref(null)

const metaSaving = ref(false)
const daySaving = ref(false)
const placeBusy = ref(false)

const edit = ref({
  title: '',
  description: '',
})

const sortedDays = computed(() => {
  const days = route.value?.days || []
  return [...days].sort((a, b) => a.day - b.day)
})

const selectedDay = computed(() => {
  if (!route.value) return null
  return (route.value.days || []).find(d => d.id === selectedDayId.value) || null
})

const dayPlaces = computed(() => {
  const d = selectedDay.value
  if (!d) return []
  const places = d.places || []
  return [...places].sort((a, b) => (a.order ?? 0) - (b.order ?? 0))
})

onMounted(() => {
  reload()
})

async function reload() {
  loading.value = true
  error.value = ''
  try {
    const routeId = routeParam.params.routeId
    const { data } = await api.get(`/routes/${routeId}/`)

    route.value = data
    edit.value.title = data.title || ''
    edit.value.description = data.description || ''

    // 첫 DAY 선택
    const first = [...(data.days || [])].sort((a, b) => a.day - b.day)[0]
    selectedDayId.value = first?.id ?? null
  } catch (e) {
    console.error(e)
    error.value = parseDRFError(e) || '루트 정보를 불러오지 못했습니다.'
  } finally {
    loading.value = false
  }
}

async function saveRouteMeta() {
  if (!route.value) return
  metaSaving.value = true
  try {
    const routeId = route.value.id
    const { data } = await api.put(`/routes/${routeId}/`, {
      title: edit.value.title,
      description: edit.value.description,
    })
    // 서버 반영값으로 갱신
    route.value.title = data.title
    route.value.description = data.description
  } catch (e) {
    console.error(e)
    alert(parseDRFError(e) || '제목/설명 저장에 실패했습니다.')
  } finally {
    metaSaving.value = false
  }
}

/**
 * DAY 추가: 마지막 day + 1 로 생성
 */
async function addDay() {
  if (!route.value) return
  daySaving.value = true
  try {
    const routeId = route.value.id
    const maxDay = Math.max(0, ...(route.value.days || []).map(d => d.day))
    const nextDay = maxDay + 1

    const { data } = await api.post(`/routes/${routeId}/days/`, { day: nextDay })
    // 응답: {id, day, places: []}
    route.value.days.push(data)
    selectedDayId.value = data.id
  } catch (e) {
    console.error(e)
    alert(parseDRFError(e) || 'DAY 추가에 실패했습니다.')
  } finally {
    daySaving.value = false
  }
}

async function deleteDay() {
  if (!selectedDay.value) return
  if (!confirm(`DAY ${selectedDay.value.day}를 삭제할까요? (해당 DAY의 장소도 모두 삭제됩니다)`)) return

  daySaving.value = true
  try {
    const dayId = selectedDay.value.id
    await api.delete(`/routes/days/${dayId}/`)

    // 로컬에서도 제거
    route.value.days = (route.value.days || []).filter(d => d.id !== dayId)

    // 다른 DAY로 이동
    const first = sortedDays.value[0]
    selectedDayId.value = first?.id ?? null
  } catch (e) {
    console.error(e)
    alert(parseDRFError(e) || 'DAY 삭제에 실패했습니다.')
  } finally {
    daySaving.value = false
  }
}

/**
 * 장소 추가(검색 컴포넌트에서 emit된 값)
 */
async function addPlaceToSelectedDay(place) {
  const d = selectedDay.value
  if (!d) return

  placeBusy.value = true
  try {
    const orders = (d.places || []).map(p => Number(p.order || 0))
    const nextOrder = (orders.length ? Math.max(...orders) : 0) + 1

    const payload = {
      order: nextOrder,
      name: place.name,
      address: place.address ?? '',
      latitude: place.latitude ?? null,
      longitude: place.longitude ?? null,
      memo: '',
    }

    const { data } = await api.post(`/routes/days/${d.id}/places/`, payload)
    d.places.push(data)
  } catch (e) {
    console.error(e)
    alert(parseDRFError(e) || '장소 추가에 실패했습니다.')
  } finally {
    placeBusy.value = false
  }
}

async function removePlace(placeId) {
  const d = selectedDay.value
  if (!d) return
  if (!confirm('이 장소를 삭제할까요?')) return

  placeBusy.value = true
  try {
    await api.delete(`/routes/places/${placeId}/`)
    d.places = (d.places || []).filter(p => p.id !== placeId)

    // 삭제 후 order 정리(중복 방지 위해 2단계 업데이트)
    await persistReorder(d)
  } catch (e) {
    console.error(e)
    alert(parseDRFError(e) || '장소 삭제에 실패했습니다.')
  } finally {
    placeBusy.value = false
  }
}

/**
 * 순서 변경(▲▼)
 * - 로컬에서 배열 순서를 바꾸고
 * - DB에는 "unique(order)" 때문에 2단계로 안전하게 반영
 */
async function movePlace(idx, dir) {
  const d = selectedDay.value
  if (!d) return

  const arr = [...(d.places || [])].sort((a, b) => (a.order ?? 0) - (b.order ?? 0))
  const next = idx + dir
  if (next < 0 || next >= arr.length) return

  // swap
  const tmp = arr[idx]
  arr[idx] = arr[next]
  arr[next] = tmp

  // 로컬 반영 + order 재부여
  arr.forEach((p, i) => { p.order = i + 1 })
  d.places = arr

  placeBusy.value = true
  try {
    await persistReorder(d)
  } catch (e) {
    console.error(e)
    alert(parseDRFError(e) || '순서 저장에 실패했습니다. 새로고침 후 다시 시도해주세요.')
    await reload()
  } finally {
    placeBusy.value = false
  }
}

/**
 * order unique_together 충돌 방지:
 * 1) 임시로 1000+order로 모두 옮겨놓고
 * 2) 최종 1..N으로 다시 저장
 */
async function persistReorder(dayObj) {
  const places = [...(dayObj.places || [])].sort((a, b) => (a.order ?? 0) - (b.order ?? 0))
  if (!places.length) return

  // 1) temp
  for (let i = 0; i < places.length; i++) {
    await api.patch(`/routes/places/${places[i].id}/`, { order: 1000 + i + 1 })
  }

  // 2) final
  for (let i = 0; i < places.length; i++) {
    const finalOrder = i + 1
    const { data } = await api.patch(`/routes/places/${places[i].id}/`, { order: finalOrder })
    places[i].order = data.order
  }

  dayObj.places = places
}

async function savePlaceMemo(p) {
  if (!p?.id) return
  try {
    await api.patch(`/routes/places/${p.id}/`, { memo: p.memo ?? '' })
  } catch (e) {
    console.error(e)
    // 메모는 조용히 실패 처리(UX)
  }
}

function parseDRFError(err) {
  const data = err?.response?.data
  if (!data) return ''

  if (typeof data === 'string') return data
  if (data.detail && typeof data.detail === 'string') return data.detail

  // {field: ["msg"]} 형태
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

.placeItem {
  border: 1px solid #f0f0f0;
  border-radius: 10px;
  padding: 10px;
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

@media (max-width: 900px) {
  .layout {
    grid-template-columns: 1fr;
  }

  .right {
    min-height: 420px;
  }
}
</style>
