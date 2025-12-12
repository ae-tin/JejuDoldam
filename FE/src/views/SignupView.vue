<template>
  <div class="signup">
    <h2>회원가입</h2>

    <form class="card" @submit.prevent="handleSubmit">
      <div class="field">
        <label>아이디</label>
        <input v-model="form.username" type="text" autocomplete="username" />
      </div>

      <div class="field">
        <label>비밀번호</label>
        <input v-model="form.password" type="password" autocomplete="new-password" />
      </div>

      <div class="field">
        <label>생년월일</label>
        <input v-model="form.birth_date" type="date" />
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
      </div>

      <div class="field">
        <label>혼인상태</label>
        <select v-model="form.marriage_status">
          <option disabled value="">선택</option>
          <option v-for="x in marriageOptions" :key="x" :value="x">{{ x }}</option>
        </select>
      </div>

      <div class="field">
        <label>직업</label>
        <select v-model="form.job">
          <option disabled value="">선택</option>
          <option v-for="x in jobOptions" :key="x" :value="x">{{ x }}</option>
        </select>
      </div>

      <div class="field">
        <label>소득</label>
        <select v-model="form.income">
          <option disabled value="">선택</option>
          <option v-for="x in incomeOptions" :key="x" :value="x">{{ x }}</option>
        </select>
      </div>

      <div class="field">
        <label>연간 여행 횟수</label>
        <select v-model.number="form.travel_num">
          <option disabled value="">선택</option>
          <option v-for="n in travelNumOptions" :key="n" :value="n">{{ n }}</option>
        </select>
      </div>

      <div class="field">
        <label>거주지</label>
        <select v-model="form.residence">
          <option disabled value="">선택</option>
          <option v-for="x in residenceOptions" :key="x" :value="x">{{ x }}</option>
        </select>
      </div>

      <button class="btn" type="submit" :disabled="loading">
        {{ loading ? '가입 중...' : '회원가입' }}
      </button>

      <p v-if="error" class="error">{{ error }}</p>
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
  birth_date: '',      // "YYYY-MM-DD"
  gender: '',          // "남" | "여"
  marriage_status: '', // choices 라벨 그대로
  job: '',
  income: '',
  travel_num: '',      // number로 변환(v-model.number)
  residence: '',
})

const marriageOptions = ['미혼', '기혼', '사별', '이혼', '기타']

const jobOptions = [
  '관리자',
  '전문가 및 관련 종사자',
  '사무 종사자',
  '서비스 종사자',
  '판매 종사자',
  '농림어업 숙련 종사자',
  '기능원 및 관련 기능 종사자',
  '장치.기계 조작 및 조립 종사자',
  '단순노무종사자',
  '군인',
  '전업주부',
  '학생',
  '기타',
]

const incomeOptions = [
  '소득없음',
  '월평균 100만원 미만',
  '월평균 100만원 ~ 200만원 미만',
  '월평균 200만원 ~ 300만원 미만',
  '월평균 300만원 ~ 400만원 미만',
  '월평균 400만원 ~ 500만원 미만',
  '월평균 500만원 ~ 600만원 미만',
  '월평균 600만원 ~ 700만원 미만',
  '월평균 700만원 ~ 800만원 미만',
  '월평균 800만원 ~ 900만원 미만',
  '월평균 900만원 ~ 1,000만원 미만',
  '월평균 1,000만원 이상',
]

const travelNumOptions = [1,2,3,4,5,6,7,8,9,10,11,12,15,20,25,30]

const residenceOptions = [
  '서울특별시', '경기도', '인천광역시', '대전광역시',
  '충청북도', '충청남도', '광주광역시',
  '전라북도', '전라남도',
  '울산광역시', '대구광역시', '부산광역시',
  '경상북도', '경상남도',
  '강원도', '제주특별자치도',
]

const handleSubmit = async () => {
  error.value = ''
  loading.value = true

  try {
    await api.post('/auth/signup/', {
      ...form,
    })

    alert('회원가입 성공! 로그인 페이지로 이동합니다.')
    router.push('/login')
  } catch (err) {
    console.error(err)
    // 서버가 serializer.errors를 내려주는 구조니까 일단 일반 메시지
    error.value = '회원가입에 실패했습니다. 입력값을 확인해주세요.'
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
.error { margin-top: 10px; color: #dc2626; font-size: 13px; }
.radio { display:flex; align-items:center; gap:6px; }
</style>
