<template>
  <div class="pc-layout-container" @mouseup="stopResize" @mouseleave="stopResize">
    
    <div v-if="loading" class="state-overlay">
      <div class="spinner"></div>
      <p>저장된 루트를 불러오고 있어요...</p>
    </div>

    <div v-else-if="error" class="state-overlay error">
      <p>⚠️ {{ error }}</p>
      <div class="actions">
        <button class="btn-retry" @click="reload">다시 시도</button>
      </div>
    </div>

    <div v-else-if="route" class="split-view" @mousemove="onResize">
      
      <aside class="left-panel" :style="{ width: panelWidth + 'px' }">
        
        <div class="panel-header">
          <div class="header-top">
            <span class="badge">MY ROUTE</span>
            
            <button class="btn-delete-route" @click="deleteRoute">
              🗑️ 루트 삭제
            </button>
          </div>
          
          <div class="route-meta-form">
            <div class="input-group">
              <label>여행 제목</label>
              <input type="text" v-model="edit.title" class="input-title" placeholder="여행 제목을 입력하세요" />
            </div>
            <div class="input-group">
              <label>설명</label>
              <textarea v-model="edit.description" class="input-desc" placeholder="여행에 대한 간단한 설명을 남겨보세요" rows="2"></textarea>
            </div>
            <button class="btn-save-meta" @click="saveRouteMeta" :disabled="metaSaving">
              {{ metaSaving ? '저장 중...' : '수정사항 저장 완료 ✅' }}
            </button>
          </div>
        </div>

        <div class="day-tabs-sticky">
          <div class="day-scroll-area">
            <button
              v-for="d in sortedDays"
              :key="d.id"
              class="day-chip"
              :class="{ active: d.id === selectedDayId }"
              @click="selectedDayId = d.id"
            >
              DAY {{ d.day }}
            </button>
            <button class="day-add-btn" @click="addDay" :disabled="daySaving" title="DAY 추가">+</button>
          </div>
        </div>

        <div class="place-list-container" v-if="selectedDay">
          
          <div class="day-header-row">
            <h3 class="day-title">DAY {{ selectedDay.day }} 일정</h3>
            <button class="btn-delete-day" @click="deleteDay" :disabled="daySaving">🗑️ DAY 삭제</button>
          </div>

          <div class="search-section">
            <KakaoPlaceSearch @select="addPlaceToSelectedDay" />
          </div>

          <p v-if="dayPlaces.length" class="helper-text">* 장소 클릭 시 사진/메모를 볼 수 있습니다.</p>

          <ul class="place-items">
            <li
              v-for="(p, idx) in dayPlaces"
              :key="p.id"
              class="place-row"
              :class="{ 'selected': selectedPlaceId === p.id }"
              @click="togglePlacePhoto(p)"
            >
              <div class="place-info">
                <span class="marker-num">{{ idx + 1 }}</span>
                <div class="text-wrap">
                  <strong class="name">
                    {{ p.name }}
                    <a v-if="p.place_url" :href="p.place_url" target="_blank" @click.stop class="map-link" title="카카오맵 보기">
                      <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path><polyline points="15 3 21 3 21 9"></polyline><line x1="10" y1="14" x2="21" y2="3"></line></svg>
                    </a>
                  </strong>
                  <span class="addr">{{ p.address || '주소 정보 없음' }}</span>
                </div>
              </div>

              <div class="place-actions" @click.stop>
                <div class="btn-group">
                  <button type="button" @click="movePlace(idx, -1)" :disabled="idx === 0 || placeBusy">▲</button>
                  <button type="button" @click="movePlace(idx, 1)" :disabled="idx === dayPlaces.length - 1 || placeBusy">▼</button>
                </div>
                <button type="button" class="del-btn" @click="removePlace(p.id)" :disabled="placeBusy">×</button>
              </div>

              <div v-if="selectedPlaceId === p.id" class="expand-content" @click.stop>
                
                <div class="expand-section">
                  <label class="expand-label">📝 메모</label>
                  <input 
                    class="memo-input" 
                    v-model="p.memo" 
                    type="text" 
                    placeholder="메모를 입력하세요"
                    @blur="savePlaceMemo(p)" 
                    :disabled="placeBusy" 
                  />
                </div>

                <div class="expand-section">
                  <label class="expand-label">📷 사진</label>
                  
                  <div v-if="p.photo_url" class="photo-box">
                    <img :src="p.photo_url" :alt="p.name" loading="lazy" />
                  </div>
                  
                  <div v-else class="no-photo-box">
                    <span class="no-photo-text">등록된 사진 정보가 없습니다.</span>
                    <a v-if="p.place_url" :href="p.place_url" target="_blank" class="link-btn">카카오맵에서 보기 →</a>
                  </div>
                </div>

              </div>
            </li>
          </ul>

          <div v-if="!dayPlaces.length" class="empty-placeholder">
            <span class="icon">📍</span>
            <p>아직 등록된 장소가 없습니다.<br>위 검색창에서 장소를 추가해보세요.</p>
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
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/api/client'
import KakaoMap from '@/components/KakaoMap.vue'
import KakaoPlaceSearch from '@/components/KakaoPlaceSearch.vue'

// --- Resizing Logic ---
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
  if (newWidth < 320) newWidth = 320
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

// --- Data Logic ---
const routeParam = useRoute()
const router = useRouter()

const loading = ref(false)
const error = ref('')
const route = ref(null)

const selectedDayId = ref(null)
const metaSaving = ref(false)
const daySaving = ref(false)
const placeBusy = ref(false)
const selectedPlaceId = ref(null)

const edit = ref({ title: '', description: '' })

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
  return [...(d.places || [])].sort((a, b) => (a.order ?? 0) - (b.order ?? 0))
})

onMounted(() => {
  reload()
})

function togglePlacePhoto(place) {
  selectedPlaceId.value = selectedPlaceId.value === place.id ? null : place.id
}

async function reload() {
  loading.value = true
  error.value = ''
  selectedPlaceId.value = null
  try {
    const routeId = routeParam.params.routeId
    const { data } = await api.get(`/routes/${routeId}/`)
    route.value = data
    edit.value.title = data.title || ''
    edit.value.description = data.description || ''
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
    route.value.title = data.title
    route.value.description = data.description
    alert('수정사항이 저장되었습니다!')
    router.push({ path: '/mypage', query: { tab: 'routes' } })
  } catch (e) {
    console.error(e)
    alert(parseDRFError(e) || '저장에 실패했습니다.')
  } finally {
    metaSaving.value = false
  }
}

// ✅ [추가됨] 루트 삭제 기능
async function deleteRoute() {
  if (!route.value) return
  if (!confirm('정말 이 여행 루트를 삭제하시겠습니까?\n삭제된 루트는 복구할 수 없습니다.')) return

  try {
    await api.delete(`/routes/${route.value.id}/`)
    alert('루트가 삭제되었습니다.')
    router.replace({ path: '/mypage', query: { tab: 'routes' } })
  } catch (e) {
    console.error(e)
    alert(parseDRFError(e) || '루트 삭제에 실패했습니다.')
  }
}

async function addDay() {
  if (!route.value) return
  daySaving.value = true
  try {
    const routeId = route.value.id
    const maxDay = Math.max(0, ...(route.value.days || []).map(d => d.day))
    const nextDay = maxDay + 1
    const { data } = await api.post(`/routes/${routeId}/days/`, { day: nextDay })
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
  if (!confirm(`DAY ${selectedDay.value.day}를 삭제할까요?`)) return
  daySaving.value = true
  try {
    const dayId = selectedDay.value.id
    await api.delete(`/routes/days/${dayId}/`)
    route.value.days = (route.value.days || []).filter(d => d.id !== dayId)
    const first = sortedDays.value[0]
    selectedDayId.value = first?.id ?? null
  } catch (e) {
    console.error(e)
    alert(parseDRFError(e) || 'DAY 삭제에 실패했습니다.')
  } finally {
    daySaving.value = false
  }
}

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
      place_url: place.place_url ?? '',
      photo_url: place.photo_url ?? '', 
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
    await persistReorder(d)
  } catch (e) {
    console.error(e)
    alert(parseDRFError(e) || '장소 삭제에 실패했습니다.')
  } finally {
    placeBusy.value = false
  }
}

async function movePlace(idx, dir) {
  const d = selectedDay.value
  if (!d) return
  const arr = [...(d.places || [])].sort((a, b) => (a.order ?? 0) - (b.order ?? 0))
  const next = idx + dir
  if (next < 0 || next >= arr.length) return
  const tmp = arr[idx]
  arr[idx] = arr[next]
  arr[next] = tmp
  arr.forEach((p, i) => { p.order = i + 1 })
  d.places = arr
  placeBusy.value = true
  try {
    await persistReorder(d)
  } catch (e) {
    console.error(e)
    alert(parseDRFError(e) || '순서 저장 실패')
    await reload()
  } finally {
    placeBusy.value = false
  }
}

async function persistReorder(dayObj) {
  const places = [...(dayObj.places || [])].sort((a, b) => (a.order ?? 0) - (b.order ?? 0))
  if (!places.length) return
  for (let i = 0; i < places.length; i++) {
    await api.patch(`/routes/places/${places[i].id}/`, { order: 1000 + i + 1 })
  }
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
  }
}

function parseDRFError(err) {
  const data = err?.response?.data
  if (!data) return ''
  if (typeof data === 'string') return data
  if (data.detail && typeof data.detail === 'string') return data.detail
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
/* PC 레이아웃 및 공통 스타일 (기존 유지) */
.pc-layout-container {
  display: flex; flex-direction: column; height: 100vh;
  padding-top: 60px; background-color: #fff; overflow: hidden; box-sizing: border-box;
}
.split-view { display: flex; flex: 1; height: 100%; overflow: hidden; }

/* Left Panel */
.left-panel {
  border-right: 1px solid #e0e0e0; background: #fff; display: flex; flex-direction: column;
  flex-shrink: 0; overflow-y: auto; position: relative; z-index: 5;
  min-width: 320px; max-width: 800px;
}

/* Header & Inputs */
.panel-header { padding: 24px; background: #fff; border-bottom: 1px solid #f0f0f0; }
.header-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.badge { background-color: #e6f7f4; color: #2cb398; font-size: 0.75rem; font-weight: 800; padding: 4px 8px; border-radius: 4px; }

/* ✅ [추가됨] 루트 삭제 버튼 스타일 */
.btn-delete-route {
  background: none;
  border: none;
  color: #999;
  font-size: 0.85rem;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  transition: all 0.2s;
  font-weight: 500;
}
.btn-delete-route:hover {
  color: #e74c3c; /* 빨간색 호버 */
  background-color: #fff0f0;
}

.route-meta-form { display: flex; flex-direction: column; gap: 12px; }
.input-group label { font-size: 0.8rem; color: #888; font-weight: 600; margin-bottom: 4px; display: block; }
.input-title, .input-desc {
  width: 100%; padding: 10px; font-size: 1rem; border: 1px solid #ddd; border-radius: 8px; outline: none; transition: border-color 0.2s;
}
.input-title:focus, .input-desc:focus { border-color: #2cb398; }
.btn-save-meta {
  width: 100%; padding: 12px; background-color: #333; color: white; border: none; border-radius: 8px; font-weight: 700; cursor: pointer;
}
.btn-save-meta:hover:not(:disabled) { background-color: #2cb398; }

/* Day Tabs */
.day-tabs-sticky { position: sticky; top: 0; background: #fff; padding: 12px 24px; border-bottom: 1px solid #f0f0f0; z-index: 10; }
.day-scroll-area { display: flex; gap: 8px; overflow-x: auto; padding-bottom: 4px; }
.day-chip {
  padding: 6px 14px; border: 1px solid #e0e0e0; border-radius: 20px; background: #fff; color: #555;
  font-size: 0.9rem; font-weight: 600; white-space: nowrap; cursor: pointer; transition: all 0.2s;
}
.day-chip.active { background: #2cb398; color: white; border-color: #2cb398; }
.day-add-btn { padding: 6px 12px; border: 1px dashed #ccc; border-radius: 20px; background: #f9f9f9; cursor: pointer; }

/* Place List */
.place-list-container { padding: 24px 24px 60px; flex: 1; }
.day-header-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.day-title { font-size: 1.1rem; font-weight: 800; margin: 0; }
.btn-delete-day { font-size: 0.8rem; color: #e74c3c; background: none; border: none; cursor: pointer; }
.helper-text { font-size: 0.8rem; color: #999; margin: 12px 0; text-align: right; }

.place-items { list-style: none; padding: 0; margin: 0; }
.place-row {
  border: 1px solid #f0f0f0; border-radius: 12px; padding: 16px; margin-bottom: 12px;
  cursor: pointer; transition: all 0.2s; background: #fff;
}
.place-row.selected { border-color: #2cb398; background-color: #fafffe; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }

.place-info { display: flex; align-items: flex-start; }
.marker-num {
  width: 24px; height: 24px; background: #2cb398; color: white; border-radius: 50%;
  text-align: center; line-height: 24px; font-size: 0.8rem; font-weight: 700; margin-right: 12px; flex-shrink: 0;
}
.text-wrap { flex: 1; }
.name { display: block; font-size: 1rem; font-weight: 700; margin-bottom: 4px; }
.addr { display: block; font-size: 0.85rem; color: #888; }
.map-link { color: #aaa; margin-left: 6px; } .map-link:hover { color: #2cb398; }

.place-actions { display: flex; justify-content: flex-end; align-items: center; margin-top: 8px; gap: 8px; }
.btn-group { display: flex; border: 1px solid #eee; border-radius: 6px; overflow: hidden; }
.btn-group button { width: 28px; height: 28px; border: none; background: #fff; cursor: pointer; border-right: 1px solid #eee; }
.btn-group button:last-child { border-right: none; }
.del-btn { background: none; border: none; color: #bbb; font-size: 1.2rem; cursor: pointer; }

/* 확장 컨텐츠 (메모+사진) 스타일 */
.expand-content {
  margin-top: 16px; border-top: 1px dashed #eee; padding-top: 16px;
  animation: slideDown 0.3s ease;
}
@keyframes slideDown { from { opacity: 0; transform: translateY(-10px); } to { opacity: 1; transform: translateY(0); } }

.expand-section { margin-bottom: 16px; }
.expand-section:last-child { margin-bottom: 0; }
.expand-label { display: block; font-size: 0.8rem; font-weight: 700; color: #2cb398; margin-bottom: 6px; }

.memo-input {
  width: 100%; padding: 10px; font-size: 0.9rem; border: 1px solid #eee; border-radius: 8px;
  background: #fafafa; outline: none; transition: all 0.2s;
}
.memo-input:focus { border-color: #2cb398; background: #fff; }

.photo-box img {
  width: 100%; border-radius: 8px; border: 1px solid #eee; display: block;
}

.no-photo-box {
  background: #f9f9f9; padding: 20px; text-align: center; border-radius: 8px; color: #aaa; font-size: 0.9rem;
}
.link-btn {
  display: inline-block; margin-top: 8px; color: #2cb398; text-decoration: none; font-size: 0.85rem; font-weight: 600;
}
.link-btn:hover { text-decoration: underline; }

/* Resizer & Right Map & Etc */
.resizer { width: 8px; background: transparent; cursor: col-resize; flex-shrink: 0; }
.right-map { flex: 1; background: #f0f0f0; }
.full-map { width: 100%; height: 100%; }

.empty-placeholder { text-align: center; padding: 40px 0; color: #aaa; }
.state-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(255,255,255,0.9); display: flex; flex-direction: column; justify-content: center; align-items: center; z-index: 100; }
.spinner { width: 40px; height: 40px; border: 4px solid #f3f3f3; border-top: 4px solid #2cb398; border-radius: 50%; animation: spin 1s linear infinite; margin-bottom: 16px; }

@media (max-width: 900px) {
  .split-view { flex-direction: column-reverse; }
  .left-panel { width: 100% !important; height: 50vh; }
  .right-map { height: 50vh; }
  .resizer { display: none; }
}
</style>