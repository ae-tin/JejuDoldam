<template>
  <div class="signup-container">
    <div class="signup-content fade-element">
      
      <header class="page-header">
        <h1 class="logo" @click="router.push('/')">MyTrip</h1>
        <h2>환영합니다! 👋</h2>
        <p class="sub-text">회원가입하고 나만의 여행 지도를 완성해보세요.</p>
      </header>

      <form class="signup-card" @submit.prevent="handleSubmit">
        
        <div v-if="error" class="global-error">
          ⚠️ {{ error }}
        </div>

        <section class="form-section">
          <h3 class="section-title">계정 정보</h3>
          
          <div class="input-group">
            <label>아이디</label>
            <input 
              v-model="form.username" 
              type="text" 
              autocomplete="username" 
              placeholder="사용하실 아이디를 입력하세요"
              class="custom-input"
              :class="{ 'has-error': fieldErrors.username }"
            />
            <p v-if="fieldErrors.username" class="field-error">{{ fieldErrors.username }}</p>
          </div>

          <div class="input-group">
            <label>비밀번호</label>
            <input 
              v-model="form.password" 
              type="password" 
              autocomplete="new-password" 
              placeholder="비밀번호를 입력하세요"
              class="custom-input"
              :class="{ 'has-error': fieldErrors.password }"
            />
            <p v-if="fieldErrors.password" class="field-error">{{ fieldErrors.password }}</p>
          </div>
        </section>

        <hr class="divider" />

        <section class="form-section">
          <h3 class="section-title">개인 정보</h3>

          <div class="row-group">
            <div class="input-group half">
              <label>생년월일</label>
              <input 
                v-model="form.birth_date" 
                type="date" 
                class="custom-input"
                :class="{ 'has-error': fieldErrors.birth_date }"
              />
              <p v-if="fieldErrors.birth_date" class="field-error">{{ fieldErrors.birth_date }}</p>
            </div>

            <div class="input-group half">
              <label>성별</label>
              <div class="gender-options">
                <label class="gender-btn" :class="{ active: form.gender === '남' }">
                  <input type="radio" value="남" v-model="form.gender" /> 남성
                </label>
                <label class="gender-btn" :class="{ active: form.gender === '여' }">
                  <input type="radio" value="여" v-model="form.gender" /> 여성
                </label>
              </div>
              <p v-if="fieldErrors.gender" class="field-error">{{ fieldErrors.gender }}</p>
            </div>
          </div>

          <div class="input-group">
            <label>거주지</label>
            <div class="select-wrapper">
              <select v-model="form.residence" class="custom-select" :class="{ 'has-error': fieldErrors.residence }">
                <option disabled value="">거주 지역을 선택해주세요</option>
                <option v-for="x in residenceOptions" :key="x" :value="x">{{ x }}</option>
              </select>
            </div>
            <p v-if="fieldErrors.residence" class="field-error">{{ fieldErrors.residence }}</p>
          </div>
        </section>

        <hr class="divider" />

        <section class="form-section">
          <h3 class="section-title">여행 취향 분석용</h3>
          
          <div class="input-group">
            <label>혼인상태</label>
            <div class="select-wrapper">
              <select v-model="form.marriage_status" class="custom-select">
                <option disabled value="">선택해주세요</option>
                <option v-for="x in marriageOptions" :key="x" :value="x">{{ x }}</option>
              </select>
            </div>
            <p v-if="fieldErrors.marriage_status" class="field-error">{{ fieldErrors.marriage_status }}</p>
          </div>

          <div class="input-group">
            <label>직업</label>
            <div class="select-wrapper">
              <select v-model="form.job" class="custom-select">
                <option disabled value="">직군을 선택해주세요</option>
                <option v-for="x in jobOptions" :key="x" :value="x">{{ x }}</option>
              </select>
            </div>
            <p v-if="fieldErrors.job" class="field-error">{{ fieldErrors.job }}</p>
          </div>

          <div class="row-group">
            <div class="input-group half">
              <label>소득 구간</label>
              <div class="select-wrapper">
                <select v-model="form.income" class="custom-select">
                  <option disabled value="">선택</option>
                  <option v-for="x in incomeOptions" :key="x" :value="x">{{ x }}</option>
                </select>
              </div>
              <p v-if="fieldErrors.income" class="field-error">{{ fieldErrors.income }}</p>
            </div>

            <div class="input-group half">
              <label>연간 여행 횟수</label>
              <div class="select-wrapper">
                <select v-model.number="form.travel_num" class="custom-select">
                  <option disabled value="">선택</option>
                  <option v-for="n in travelNumOptions" :key="n" :value="n">{{ n }}회</option>
                </select>
              </div>
              <p v-if="fieldErrors.travel_num" class="field-error">{{ fieldErrors.travel_num }}</p>
            </div>
          </div>
        </section>

        <div class="action-area">
          <button class="submit-btn" type="submit" :disabled="loading">
            <span v-if="loading" class="spinner"></span>
            {{ loading ? '가입 처리 중...' : '회원가입 완료' }}
          </button>
          
          <p class="login-link">
            이미 계정이 있으신가요? 
            <RouterLink to="/login">로그인하기</RouterLink>
          </p>
        </div>

      </form>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
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

const fieldErrors = reactive({
  username: '', password: '', birth_date: '', gender: '',
  marriage_status: '', job: '', income: '', travel_num: '', residence: '',
})

function resetErrors() {
  error.value = ''
  for (const k of Object.keys(fieldErrors)) fieldErrors[k] = ''
}

function applyDRFErrors(data) {
  if (!data || typeof data !== 'object') return
  if (data.detail) {
    error.value = String(data.detail)
    return
  }
  for (const [key, msgs] of Object.entries(data)) {
    const text = Array.isArray(msgs) ? msgs.join(', ') : String(msgs)
    if (key in fieldErrors) fieldErrors[key] = text
    else error.value = error.value ? `${error.value} / ${key}: ${text}` : `${key}: ${text}`
  }
}

// 옵션 데이터 (기존 유지)
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
    if (!err.response) {
      error.value = '네트워크 오류가 발생했습니다. 서버 상태를 확인해주세요.'
      return
    }
    applyDRFErrors(err.response.data)
    if (!error.value && Object.values(fieldErrors).every(v => !v)) {
      error.value = '회원가입에 실패했습니다.'
    }
  } finally {
    loading.value = false
  }
}

// 등장 애니메이션
onMounted(() => {
  setTimeout(() => {
    document.querySelector('.fade-element')?.classList.add('visible')
  }, 100)
})
</script>

<style scoped>
/* 컨테이너 */
.signup-container {
  min-height: 100vh;
  padding: 40px 20px 80px; /* Navbar 고려 여백 */
  background-color: #f5f7fa;
  font-family: -apple-system, BlinkMacSystemFont, "Pretendard", Roboto, sans-serif;
  color: #333;
}

.signup-content {
  max-width: 500px;
  margin: 0 auto;
}

/* 헤더 */
.page-header {
  text-align: center;
  margin-bottom: 30px;
}
.logo {
  font-size: 1.5rem;
  font-weight: 800;
  color: #2cb398;
  margin-bottom: 10px;
  cursor: pointer;
  display: inline-block;
}
.page-header h2 { font-size: 1.8rem; font-weight: 700; margin-bottom: 8px; }
.sub-text { color: #666; font-size: 0.95rem; }

/* 폼 카드 */
.signup-card {
  background: white;
  padding: 30px;
  border-radius: 20px;
  box-shadow: 0 10px 25px rgba(0,0,0,0.05);
  border: 1px solid #f0f0f0;
}

/* 섹션 구분 */
.section-title {
  font-size: 0.9rem;
  color: #888;
  margin-bottom: 16px;
  font-weight: 600;
  border-left: 3px solid #2cb398;
  padding-left: 8px;
}

.divider { border: 0; height: 1px; background: #eee; margin: 24px 0; }

/* 입력 그룹 */
.input-group { margin-bottom: 20px; }
.input-group label {
  display: block;
  font-weight: 700;
  margin-bottom: 8px;
  font-size: 0.9rem;
  color: #444;
}

.row-group { display: flex; gap: 12px; }
.half { flex: 1; }

/* Input & Select 공통 스타일 */
.custom-input, .custom-select {
  width: 100%;
  padding: 12px 14px;
  border: 1px solid #ddd;
  border-radius: 12px;
  font-size: 0.95rem;
  background-color: #fafafa;
  transition: all 0.2s;
  outline: none;
  font-family: inherit;
}

.custom-input:focus, .custom-select:focus {
  background-color: #fff;
  border-color: #2cb398;
  box-shadow: 0 0 0 3px rgba(44, 179, 152, 0.1);
}

.has-error { border-color: #dc2626; background-color: #fff5f5; }

/* 셀렉트박스 화살표 처리 */
.select-wrapper { position: relative; }
/* 브라우저 기본 화살표 스타일 제거 (선택사항) */
.custom-select { appearance: auto; } 

/* 성별 버튼 (Radio Custom) */
.gender-options { display: flex; gap: 10px; }
.gender-btn {
  flex: 1;
  text-align: center;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 12px;
  background-color: #fafafa;
  cursor: pointer;
  transition: all 0.2s;
  font-weight: 600;
  color: #666;
}
.gender-btn input { display: none; /* 실제 라디오 숨김 */ }

.gender-btn.active {
  background-color: #e6f7f4;
  border-color: #2cb398;
  color: #2cb398;
  font-weight: bold;
}
.gender-btn:hover:not(.active) { background-color: #eee; }

/* 에러 메시지 */
.global-error {
  background-color: #fff5f5;
  color: #dc2626;
  padding: 12px;
  border-radius: 8px;
  margin-bottom: 20px;
  font-size: 0.9rem;
  text-align: center;
  border: 1px solid #fecaca;
}
.field-error { color: #dc2626; font-size: 0.8rem; margin-top: 5px; margin-left: 2px; }

/* 버튼 영역 */
.action-area { margin-top: 30px; }
.submit-btn {
  width: 100%;
  padding: 15px;
  background-color: #2cb398;
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 1.1rem;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
}
.submit-btn:hover { background-color: #249e85; transform: translateY(-2px); }
.submit-btn:disabled { background-color: #ccc; cursor: not-allowed; transform: none; }

.login-link {
  text-align: center; margin-top: 15px; font-size: 0.9rem; color: #666;
}
.login-link a { color: #2cb398; font-weight: bold; text-decoration: none; }
.login-link a:hover { text-decoration: underline; }

/* 로딩 스피너 */
.spinner {
  width: 16px; height: 16px; border: 2px solid rgba(255,255,255,0.3); border-top-color: white; border-radius: 50%; animation: spin 0.8s infinite linear;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* 애니메이션 */
.fade-element { opacity: 0; transform: translateY(20px); transition: 0.8s ease; }
.fade-element.visible { opacity: 1; transform: translateY(0); }

/* 모바일 대응 */
@media (max-width: 480px) {
  .signup-container { padding: 20px 16px; }
  .signup-card { padding: 20px; }
  .row-group { flex-direction: column; gap: 0; }
  .input-group.half { margin-bottom: 20px; }
}
</style>