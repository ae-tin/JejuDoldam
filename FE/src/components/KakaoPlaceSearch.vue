<template>
  <div class="searchBox">
    <!-- ✅ 1) 이벤트: 검색어 입력 + 검색 버튼 -->
    <div class="row">
      <input
        v-model="q"
        class="input"
        type="text"
        placeholder="장소 검색 (예: 성산일출봉)"
        @keydown.enter.prevent="search"
      />
      <button class="btn" type="button" @click="search" :disabled="loading || !q.trim()">
        {{ loading ? '검색중...' : '검색' }}
      </button>
    </div>

    <p v-if="err" class="err">{{ err }}</p>

    <!-- ✅ 3) 응답(results)을 화면에 뿌림 -->
    <ul v-if="results.length" class="list">
      <li v-for="p in results" :key="p.id" class="item">
        <div class="name">{{ p.name }}</div>
        <div class="addr">{{ p.address || '주소 없음' }}</div>

        <div class="actions">
          <a v-if="p.place_url" class="link" :href="p.place_url" target="_blank" rel="noreferrer">
            링크
          </a>
          <!-- ✅ 선택 이벤트: RouteRecommendView로 place 객체를 emit -->
          <button class="mini" type="button" @click="select(p)">추가</button>
        </div>
      </li>
    </ul>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import api from '@/api/client'

/**
 * 프론트 최소 이해 세트:
 * - 이벤트: search(), select()
 * - API: GET /places/search/?q=...
 * - 응답: results에 넣고 화면에 렌더
 */
const emit = defineEmits(['select'])

const q = ref('')
const loading = ref(false)
const err = ref('')
const results = ref([])

const search = async () => {
  err.value = ''
  results.value = []
  loading.value = true

  try {
    // ✅ 2) API 호출: 백엔드로 검색어만 전송
    const { data } = await api.get('/routes/search/', {
      params: { q: q.value.trim() },
    })

    // ✅ 응답 데이터 저장 -> 화면 렌더링
    results.value = data
    console.log(data)
  } catch (e) {
    // 백엔드에서 {"detail": "..."} 형태로 내려주므로 그걸 우선 표시
    err.value = e?.response?.data?.detail || '검색에 실패했습니다.'
  } finally {
    loading.value = false
  }
}

function select(p) {
  // RouteRecommendView가 바로 addPlaceToSelectedDay(place)로 받을 수 있게 통일
  emit('select', {
    name: p.name,
    address: p.address ?? '',
    latitude: p.latitude ?? null,
    longitude: p.longitude ?? null,
    place_url: p.place_url ?? '',
  })
}
</script>

<style scoped>
.searchBox { border:1px solid #f0f0f0; border-radius: 12px; padding: 12px; }
.row { display:flex; gap: 8px; }
.input { flex:1; padding: 10px 12px; border:1px solid #ddd; border-radius: 10px; }
.btn { padding: 10px 12px; border:1px solid #ddd; border-radius: 10px; background:#fff; cursor:pointer; }
.err { color:#dc2626; font-size: 12px; margin: 8px 0 0; }
.list { list-style:none; padding:0; margin: 10px 0 0; display:flex; flex-direction:column; gap: 8px; }
.item { border:1px solid #f3f3f3; border-radius: 10px; padding: 10px; display:flex; align-items:center; gap: 10px; }
.name { font-weight:700; }
.addr { flex:1; color:#666; font-size: 12px; }
.actions { display:flex; align-items:center; gap: 8px; }
.link { font-size: 12px; color:#2563eb; text-decoration:none; }
.mini { padding: 6px 10px; border:1px solid #ddd; border-radius: 999px; background:#fff; cursor:pointer; font-size: 12px; }
</style>
