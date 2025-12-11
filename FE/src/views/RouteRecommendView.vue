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
            <input
              type="checkbox"
              value="HEALING"
              v-model="form.themes"
            />
            힐링
          </label>
          <label>
            <input
              type="checkbox"
              value="CAFE"
              v-model="form.themes"
            />
            카페
          </label>
          <label>
            <input
              type="checkbox"
              value="FOOD"
              v-model="form.themes"
            />
            맛집
          </label>
          <label>
            <input
              type="checkbox"
              value="ACTIVITY"
              v-model="form.themes"
            />
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

      <div
        v-for="route in results"
        :key="route.id"
        class="route-card"
      >
        <h4>{{ route.title }}</h4>
        <p>{{ route.summary }}</p>
        <p>일수: {{ route.days }}일</p>
        <ul>
          <li v-for="(place, idx) in route.places" :key="idx">
            Day {{ place.day }} - {{ place.name }}
          </li>
        </ul>

        <!-- 나중에 여기서 "이 루트 저장하기" 버튼으로 BE /routes/save 호출 -->
        <button type="button">
          이 루트 저장하기 (TODO)
        </button>
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
</style>
