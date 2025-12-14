<template>
  <div class="signup">
    <h2>회원가입</h2>

    <form class="card" @submit.prevent="handleSubmit">
      <!-- 전체 에러(네트워크/서버 등) -->
      <p v-if="error" class="error">{{ error }}</p>

      <div class="field">
        <label>아이디</label>
        <input v-model="form.username" type="text" autocomplete="username" />
        <p v-if="fieldErrors.username" class="field-error">{{ fieldErrors.username }}</p>
      </div>

      <div class="field">
        <label>비밀번호</label>
        <input v-model="form.password" type="password" autocomplete="new-password" />
        <p v-if="fieldErrors.password" class="field-error">{{ fieldErrors.password }}</p>
      </div>

      <div class="field">
        <label>생년월일</label>
        <input v-model="form.birth_date" type="date" />
        <p v-if="fieldErrors.birth_date" class="field-error">{{ fieldErrors.birth_date }}</p>
      </div>

      <div class="field">
        <label>성별</label>
        <div class="row">
          <label class="radio">
            <input type="radio" value="남" v-model="form.gender" />
            남
          </label>
          <label class="radio">
            <input type="radio" value="여" v-model="form.gender" />
            여
          </label>
        </div>
        <p v-if="fieldErrors.gender" class="field-error">{{ fieldErrors.gender }}</p>
      </div>

      <div class="field">
        <label>혼인상태</label>
        <select v-model="form.marriage_status">
          <option disabled value="">선택</option>
          <option v-for="x in marriageOptions" :key="x" :value="x">{{ x }}</option>
        </select>
        <p v-if="fieldErrors.marriage_status" class="field-error">{{ fieldErrors.marriage_status }}</p>
      </div>

      <div class="field">
        <label>직업</label>
        <select v-model="form.job">
          <option disabled value="">선택</option>
          <option v-for="x in jobOptions" :key="x" :value="x">{{ x }}</option>
        </select>
        <p v-if="fieldErrors.job" class="field-error">{{ fieldErrors.job }}</p>
      </div>

      <div class="field">
        <label>소득</label>
        <select v-model="form.income">
          <option disabled value="">선택</option>
          <option v-for="x in incomeOptions" :key="x" :value="x">{{ x }}</option>
        </select>
        <p v-if="fieldErrors.income" class="field-error">{{ fieldErrors.income }}</p>
      </div>

      <div class="field">
        <label>연간 여행 횟수</label>
        <select v-model.number="form.travel_num">
          <option disabled value="">선택</option>
          <option v-for="n in travelNumOptions" :key="n" :value="n">{{ n }}</option>
        </select>
        <p v-if="fieldErrors.travel_num" class="field-error">{{ fieldErrors.travel_num }}</p>
      </div>

      <div class="field">
        <label>거주지</label>
        <select v-model="form.residence">
          <option disabled value="">선택</option>
          <option v-for="x in residenceOptions" :key="x" :value="x">{{ x }}</option>
        </select>
        <p v-if="fieldErrors.residence" class="field-error">{{ fieldErrors.residence }}</p>
      </div>

      <button class="btn" type="submit" :disabled="loading">
        {{ loading ? '가입 중...' : '회원가입' }}
      </button>
    </form>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/api/client'

const router = useRouter()
const loading = ref(false)
const error = ref('')

const form = reactive({
  username: '',
  password: '',
  birth_date: '',
  gender: '',
  marriage_status: '',
  job: '',
  income: '',
  travel_num: '',
  residence: '',
})

// ✅ 필드별 에러 저장소
const fieldErrors = reactive({
  username: '',
  password: '',
  birth_date: '',
  gender: '',
  marriage_status: '',
  job: '',
  income: '',
  travel_num: '',
  residence: '',
})

// 에러 초기화
function resetErrors() {
  error.value = ''
  for (const k of Object.keys(fieldErrors)) fieldErrors[k] = ''
}

// DRF serializer.errors 형태를 fieldErrors에 반영
function applyDRFErrors(data) {
  // data: { field: ["msg"], ... } or { detail: "..." }
  if (!data || typeof data !== 'object') return

  if (data.detail) {
    error.value = String(data.detail)
    return
  }

  for (const [key, msgs] of Object.entries(data)) {
    const text = Array.isArray(msgs) ? msgs.join(', ') : String(msgs)

    // 우리가 가진 필드면 필드 아래로
    if (key in fieldErrors) fieldErrors[key] = text
    // 그 외는 전체 에러로
    else error.value = error.value ? `${error.value} / ${key}: ${text}` : `${key}: ${text}`
  }
}

const marriageOptions = ['미혼', '기혼', '사별', '이혼', '기타']
const jobOptions = [
  '관리자','전문가 및 관련 종사자','사무 종사자','서비스 종사자','판매 종사자',
  '농림어업 숙련 종사자','기능원 및 관련 기능 종사자','장치.기계 조작 및 조립 종사자',
  '단순노무종사자','군인','전업주부','학생','기타',
]
const incomeOptions = [
  '소득없음','월평균 100만원 미만','월평균 100만원 ~ 200만원 미만','월평균 200만원 ~ 300만원 미만',
  '월평균 300만원 ~ 400만원 미만','월평균 400만원 ~ 500만원 미만','월평균 500만원 ~ 600만원 미만',
  '월평균 600만원 ~ 700만원 미만','월평균 700만원 ~ 800만원 미만','월평균 800만원 ~ 900만원 미만',
  '월평균 900만원 ~ 1,000만원 미만','월평균 1,000만원 이상',
]
const travelNumOptions = [1,2,3,4,5,6,7,8,9,10,11,12,15,20,25,30]
const residenceOptions = [
  '서울특별시','경기도','인천광역시','대전광역시','충청북도','충청남도','광주광역시',
  '전라북도','전라남도','울산광역시','대구광역시','부산광역시','경상북도','경상남도','강원도','제주특별자치도',
]

const handleSubmit = async () => {
  resetErrors()
  loading.value = true

  try {
    await api.post('/auth/signup/', { ...form })
    alert('회원가입 성공! 로그인 페이지로 이동합니다.')
    router.push('/login')
  } catch (err) {
    console.error(err)

    // ✅ 네트워크/서버 다운
    if (!err.response) {
      error.value = '네트워크 오류가 발생했습니다. 서버 상태를 확인해주세요.'
      return
    }

    // ✅ DRF가 준 serializer.errors 반영
    applyDRFErrors(err.response.data)

    // 혹시 아무것도 못 뽑았으면 기본 메시지
    if (!error.value && Object.values(fieldErrors).every(v => !v)) {
      error.value = '회원가입에 실패했습니다.'
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.signup { max-width: 520px; margin: 40px auto 0; }
.card { border: 1px solid #eee; border-radius: 12px; padding: 18px; }
.field { display: flex; flex-direction: column; gap: 6px; margin-bottom: 12px; }
.row { display: flex; gap: 12px; }
input, select { padding: 10px 12px; border: 1px solid #ddd; border-radius: 10px; }
.btn { width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 10px; background: #fff; cursor: pointer; }
.error { margin: 0 0 10px; color: #dc2626; font-size: 13px; }
.field-error { margin: 0; color: #dc2626; font-size: 12px; }
.radio { display:flex; align-items:center; gap:6px; }
</style>
