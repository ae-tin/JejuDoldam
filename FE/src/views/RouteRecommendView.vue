<template>
  <div class="recommend-page">
    <h2>제주 여행 루트 추천 받기 (뼈대)</h2>

    <!-- 입력 폼 -->
    <form class="recommend-form" @submit.prevent="handleSubmit">
      <div class="field">
        <label for="days">여행 일수</label>
        <select id="days" v-model.number="form.days">
          <option :value="1">1일</option>
          <option :value="2">2일</option>
          <option :value="3">3일</option>
          <option :value="4">4일</option>
        </select>
      </div>

      <div class="field">
        <label for="companion">동행 타입</label>
        <select id="companion" v-model="form.companionType">
          <option value="COUPLE">연인</option>
          <option value="FRIENDS">친구</option>
          <option value="FAMILY">가족</option>
          <option value="SOLO">혼자</option>
        </select>
      </div>

      <div class="field">
        <label for="transport">이동 수단</label>
        <select id="transport" v-model="form.transport">
          <option value="CAR">렌트카</option>
          <option value="BUS">대중교통</option>
        </select>
      </div>

      <div class="field">
        <label>여행 스타일</label>
        <div class="checkbox-group">
          <label>
            <input type="checkbox" value="HEALING" v-model="form.themes" />
            힐링
          </label>
          <label>
            <input type="checkbox" value="CAFE" v-model="form.themes" />
            카페
          </label>
          <label>
            <input type="checkbox" value="FOOD" v-model="form.themes" />
            맛집
          </label>
          <label>
            <input type="checkbox" value="ACTIVITY" v-model="form.themes" />
            액티비티
          </label>
        </div>
      </div>

      <button type="submit" :disabled="loading">
        {{ loading ? '추천 생성 중...' : '루트 추천 받기' }}
      </button>
    </form>

    <hr />

    <!-- 추천 결과 -->
    <section v-if="results.length" class="results">
      <h3>추천된 루트 목록 (더미)</h3>

      <div v-for="route in results" :key="route.id" class="route-card">
        <h4>{{ route.title }}</h4>
        <p>{{ route.description }}</p>
        <p>일수: {{ route.days }}일</p>
        <ul>
          <li v-for="(place, idx) in route.places" :key="idx">
            Day {{ place.day }} - {{ place.name }}
          </li>
        </ul>

        <div class="card-actions">
          <!-- 나중에 '상세보기/편집' 버튼도 추가 가능 -->
          <button type="button">
            이 루트로 편집하기 (TODO)
          </button>

          <!-- ⭐ 지금 당장 사용할 '확정 저장' 버튼 -->
          <button type="button" :disabled="savingId === route.id" @click="handleConfirm(route)">
            {{ savingId === route.id ? '저장 중...' : '이 루트 확정해서 저장' }}
          </button>
        </div>
      </div>
    </section>

    <p v-else class="no-results">
      아직 추천 결과가 없습니다. 조건을 입력하고 추천을 받아보세요.
    </p>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import api from '@/api/client'   // ✅ 공통 axios 인스턴스

const form = reactive({
  days: 3,
  companionType: 'COUPLE',
  transport: 'CAR',
  themes: [],   // ['HEALING', 'CAFE']
})

const loading = ref(false)
const results = ref([])

// 확정 저장 중인 route id(버튼 disable)
const savingId = ref(null)

const handleSubmit = async () => {
  loading.value = true

  try {
    // 1) FE 폼을 BE가 기대하는 형태로 매핑
    const payload = {
      days: form.days,
      companion_type: form.companionType,
      transport: form.transport,
      themes: form.themes,
    }

    // 2) 실제 백엔드 추천 API 호출
    //    baseURL이 http://127.0.0.1:8000/api/v1 라면,
    //    여기 path는 '/routes/recommend/' 가 맞음
    const { data } = await api.post('/routes/recommend/', payload)

    // 3) 응답 데이터(추천 루트 리스트)를 화면에 뿌림
    results.value = data
  } catch (err) {
    console.error(err)
    alert('추천 생성 중 오류가 발생했습니다.')
  } finally {
    loading.value = false
  }
}

// 추천으로 받은 route 중 하나를 확정 저장하는 함수
const handleConfirm = async (route) => {
  if (!confirm('이 루트를 확정해서 저장할까요?')) {
    return
  }

  savingId.value = route.id

  try {
    // 1) 추천 응답(route)을 confirm API 요청 형태로 변환
    const confirmPayload = mapRouteToConfirmPayload(route)

    // 2) 백엔드 확정 API 호출
    const { data } = await api.post('/routes/confirm/', confirmPayload)

    // 3) 일단은 알림만 + 콘솔 확인
    console.log('확정 저장 결과:', data)
    alert('루트가 저장되었습니다! (나중에 마이페이지에서 확인 가능하게 만들자)')
  } catch (err) {
    console.error(err)
    alert('루트 저장 중 오류가 발생했습니다.')
  } finally {
    savingId.value = null
  }
}

// 추천 route -> confirm API 요청 형태로 변환하는 헬퍼 함수
function mapRouteToConfirmPayload(route) {
  // 백엔드의 confirm API가 기대하는 데이터 구성으로 현재 데이터를 변환함
  // day별로 묶기 위한 임시 객체
  const dayMap = {}

  for (const place of route.places) {
    const day = place.day
    if (!dayMap[day]) {
      dayMap[day] = []
    }

    dayMap[day].push({
      order: place.order ?? dayMap[day].length + 1,
      name: place.name,
      address: place.address ?? '',
      latitude: place.latitude ?? null,
      longitude: place.longitude ?? null,
      memo: place.memo ?? '',
    })
  }

  // day 숫자 오름차순으로 정렬해서 배열로 변환
  const days = Object.entries(dayMap)
    .map(([day, places]) => ({
      day: Number(day),
      places: places.sort((a, b) => a.order - b.order),
    }))
    .sort((a, b) => a.day - b.day)

  return {
    title: route.title,
    description: route.description ?? '',
    days,
  }
}
</script>


<style scoped>
.recommend-page {
  max-width: 900px;
  margin: 0 auto;
}

.recommend-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 24px;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.checkbox-group {
  display: flex;
  flex-wrap: wrap;
  gap: 8px 16px;
}

.results {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.route-card {
  border: 1px solid #ddd;
  padding: 12px 16px;
  border-radius: 8px;
}

.no-results {
  margin-top: 16px;
  color: #666;
}

.card-actions {
  margin-top: 8px;
  display: flex;
  gap: 8px;
}
</style>
