<template>
  <div class="settings-page">
    
    <div v-if="loading" class="state-overlay">
      <div class="spinner"></div>
      <p>정보를 불러오는 중...</p>
    </div>

    <div v-else class="settings-container fade-in-up">
      
      <header class="page-header">
        <h2 class="page-title">프로필 설정</h2>
        <p class="page-desc">
          정확한 정보를 입력할수록 <b>더 완벽한 여행 코스</b>를 추천받을 수 있어요.
        </p>
      </header>

      <form @submit.prevent="saveProfile" class="main-form">
        
        <div class="form-layout">
          
          <section class="form-section left-section">
            <h3 class="section-title">
              <span class="icon">👤</span> 기본 정보
            </h3>
            
            <div class="input-stack">
              <div class="input-group">
                <label>아이디</label>
                <input 
                  type="text" 
                  v-model="form.username" 
                  disabled 
                  class="input-field readonly"
                />
                <span class="helper-text">* 아이디는 변경할 수 없습니다.</span>
              </div>

              <div class="input-group">
                <label>생년월일</label>
                <input 
                  type="date" 
                  v-model="form.birth_date" 
                  class="input-field" 
                  required
                />
              </div>

              <div class="row-group">
                <div class="input-group half">
                  <label>성별</label>
                  <div class="select-wrapper">
                    <select v-model="form.gender" class="input-field" required>
                      <option disabled value="">선택</option>
                      <option v-for="opt in genderOptions" :key="opt" :value="opt">{{ opt }}</option>
                    </select>
                    <span class="arrow">▼</span>
                  </div>
                </div>

                <div class="input-group half">
                  <label>결혼 여부</label>
                  <div class="select-wrapper">
                    <select v-model="form.marriage_status" class="input-field" required>
                      <option disabled value="">선택</option>
                      <option v-for="opt in marriageOptions" :key="opt" :value="opt">{{ opt }}</option>
                    </select>
                    <span class="arrow">▼</span>
                  </div>
                </div>
              </div>

              <div class="input-group">
                <label>거주지</label>
                <div class="select-wrapper">
                  <select v-model="form.residence" class="input-field" required>
                    <option disabled value="">거주 지역을 선택해주세요</option>
                    <option v-for="opt in residenceOptions" :key="opt" :value="opt">{{ opt }}</option>
                  </select>
                  <span class="arrow">▼</span>
                </div>
              </div>
            </div>
          </section>

          <section class="form-section right-section">
            <h3 class="section-title">
              <span class="icon">✈️</span> 생활 & 여행
            </h3>

            <div class="input-stack">
              <div class="input-group">
                <label>직업</label>
                <div class="select-wrapper">
                  <select v-model="form.job" class="input-field" required>
                    <option disabled value="">직업을 선택해주세요</option>
                    <option v-for="opt in jobOptions" :key="opt" :value="opt">{{ opt }}</option>
                  </select>
                  <span class="arrow">▼</span>
                </div>
              </div>

              <div class="input-group">
                <label>월 평균 소득</label>
                <div class="select-wrapper">
                  <select v-model="form.income" class="input-field" required>
                    <option disabled value="">소득 구간 선택</option>
                    <option v-for="opt in incomeOptions" :key="opt" :value="opt">{{ opt }}</option>
                  </select>
                  <span class="arrow">▼</span>
                </div>
              </div>

              <div class="input-group">
                <label>연간 여행 횟수 (회)</label>
                <div class="select-wrapper">
                  <select v-model="form.travel_num" class="input-field" required>
                    <option disabled value="">횟수 선택</option>
                    <option v-for="num in travelNumOptions" :key="num" :value="num">
                      {{ num }}회
                    </option>
                  </select>
                  <span class="arrow">▼</span>
                </div>
                <span class="helper-text">* 최근 1년간 다녀온 여행 횟수를 선택해주세요.</span>
              </div>

            </div>
          </section>

        </div>

        <div class="form-actions">
          <button type="button" class="btn-back" @click="$router.back()">취소</button>
          
          <button type="submit" class="btn-submit" :disabled="saving">
            {{ saving ? '저장 중...' : '변경사항 저장하기' }}
          </button>
        </div>

      </form>
    </div>
  </div>
</template>

<script setup>
/**
 * [Vue 3 Composition API]
 * - ref: 반응형 변수 생성 (값이 바뀌면 화면도 바뀜)
 * - onMounted: 컴포넌트가 화면에 나타날 때 실행되는 훅
 * - useRouter: 페이지 이동을 위한 라우터 객체 사용
 */
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/api/client' // 미리 설정해둔 Axios 인스턴스 (API 호출용)
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()
// --- [상태 변수] ---
const loading = ref(false) // 로딩 중 여부
const saving = ref(false)  // 저장 중 여부

// 폼 데이터 (백엔드 모델과 필드명 일치)
const form = ref({
  username: '',
  birth_date: '',
  gender: '',
  marriage_status: '',
  job: '',
  income: '',
  travel_num: '', // 초기값은 빈 문자열 (선택 유도)
  residence: '',
})

// --- [옵션 데이터 (Select Box용)] ---
const genderOptions = ["남", "여"]
const marriageOptions = ["미혼", "기혼", "사별", "이혼", "기타"]
const jobOptions = [
  "관리자", "전문가 및 관련 종사자", "사무 종사자", "서비스 종사자", "판매 종사자",
  "농림어업 숙련 종사자", "기능원 및 관련 기능 종사자", "장치.기계 조작 및 조립 종사자",
  "단순노무종사자", "군인", "전업주부", "학생", "기타"
]
const incomeOptions = [
  "소득없음", "월평균 100만원 미만", "월평균 100만원 ~ 200만원 미만",
  "월평균 200만원 ~ 300만원 미만", "월평균 300만원 ~ 400만원 미만",
  "월평균 400만원 ~ 500만원 미만", "월평균 500만원 ~ 600만원 미만",
  "월평균 600만원 ~ 700만원 미만", "월평균 700만원 ~ 800만원 미만",
  "월평균 800만원 ~ 900만원 미만", "월평균 900만원 ~ 1,000만원 미만",
  "월평균 1,000만원 이상"
]
const residenceOptions = [
  "서울특별시", "경기도", "인천광역시", "대전광역시", "충청북도", "충청남도",
  "광주광역시", "전라북도", "전라남도", "울산광역시", "대구광역시", "부산광역시",
  "경상북도", "경상남도", "강원도", "제주특별자치도"
]

// ✅ [수정됨] 백엔드 유효성 검사 로직에 맞춘 허용값 리스트
const travelNumOptions = [
  1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 15, 20, 25, 30
]

// --- [API: 내 정보 불러오기] ---
const fetchUserData = async () => {
  loading.value = true // 로딩 시작
  try {
    const { data } = await api.get('/auth/me/') // GET 요청
    // 받아온 데이터를 폼에 채워 넣습니다.
    form.value = {
      username: data.username,
      birth_date: data.birth_date,
      gender: data.gender,
      marriage_status: data.marriage_status,
      job: data.job,
      income: data.income,
      travel_num: data.travel_num, // 서버에 저장된 값 매핑
      residence: data.residence,
    }
  } catch (e) {
    console.error(e)
    alert('정보를 불러오지 못했습니다.')
    router.back() // 에러 시 뒤로가기
  } finally {
    loading.value = false // 로딩 종료
  }
}

// --- [API: 변경사항 저장하기] ---
const saveProfile = async () => {
  // [클라이언트 유효성 검사]
  // select 박스를 사용하므로 범위 외 값은 원천 차단되지만, 혹시 모를 빈 값 체크
  if (!form.value.travel_num) {
    alert('연간 여행 횟수를 선택해주세요.')
    return
  }

  saving.value = true // 저장 중 상태로 변경 (버튼 비활성화)
  try {
    // PATCH 요청: 수정된 데이터만 업데이트
    await api.patch('/auth/me/', form.value)
    // 회원 정보 업데이트
    await authStore.fetchUser()
    alert('성공적으로 저장되었습니다!')

    router.push('/mypage') // 마이페이지로 이동
    
  } catch (e) {
    console.error(e)
    // 서버에서 보내주는 에러 메시지가 있다면 표시, 없으면 기본 메시지
    const msg = e.response?.data?.detail || '저장에 실패했습니다.'
    alert(msg)
  } finally {
    saving.value = false // 저장 상태 해제
  }
}

// 컴포넌트가 마운트되면 데이터 불러오기 실행
onMounted(() => {
  fetchUserData()
})
</script>

<style scoped>
/* [스타일링: PC 와이드 레이아웃] */

/* 전체 페이지 배경 및 폰트 설정 */
.settings-page {
  background-color: #f5f7fa;
  min-height: 100vh;
  padding: 80px 20px 100px;
  font-family: -apple-system, BlinkMacSystemFont, "Pretendard", Roboto, sans-serif;
}

/* 컨텐츠 중앙 정렬 및 최대 너비 설정 */
.settings-container {
  max-width: 1200px; /* PC 화면에 맞게 넓게 */
  margin: 0 auto;
}

/* 헤더 스타일 */
.page-header {
  text-align: center;
  margin-bottom: 50px;
}
.page-title {
  font-size: 2.5rem;
  font-weight: 800;
  color: #111;
  margin-bottom: 10px;
}
.page-desc {
  font-size: 1.1rem;
  color: #666;
}
.page-desc b { color: #2cb398; } /* 강조색 */

/* [2단 분리 레이아웃 Grid] */
.form-layout {
  display: grid;
  grid-template-columns: 1fr 1fr; /* 좌우 1:1 비율 */
  gap: 40px;
  margin-bottom: 40px;
}

/* 섹션 카드 공통 스타일 */
.form-section {
  background: white;
  border-radius: 20px;
  padding: 40px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.03); /* 은은한 그림자 */
  border: 1px solid rgba(0,0,0,0.02);
}

/* 섹션 제목 스타일 */
.section-title {
  font-size: 1.3rem;
  font-weight: 700;
  color: #333;
  margin-bottom: 30px;
  display: flex;
  align-items: center;
  border-bottom: 2px solid #f0f0f0;
  padding-bottom: 15px;
}
.section-title .icon { margin-right: 10px; font-size: 1.5rem; }

/* 입력 그룹들을 감싸는 스택 (세로 정렬) */
.input-stack {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* 개별 입력 그룹 */
.input-group { display: flex; flex-direction: column; gap: 8px; }
.input-group label {
  font-size: 0.95rem;
  font-weight: 600;
  color: #444;
}

/* 입력 필드 (Input & Select 공통) */
.input-field {
  padding: 14px 16px;
  font-size: 1rem;
  border: 1px solid #ddd;
  border-radius: 10px;
  outline: none;
  transition: all 0.2s;
  background: #fff;
  width: 100%;
  font-family: inherit; /* 폰트 상속 */
}
/* 포커스 시 민트색 테두리 */
.input-field:focus { border-color: #2cb398; box-shadow: 0 0 0 3px rgba(44, 179, 152, 0.1); }

/* 읽기 전용 필드 스타일 */
.input-field.readonly {
  background-color: #f7f9fc;
  color: #888;
  cursor: not-allowed;
  border-color: #eee;
}

/* Select 박스 화살표 커스텀 */
.select-wrapper { position: relative; }
.input-field { appearance: none; -webkit-appearance: none; } /* 기본 화살표 제거 */
.arrow { 
  position: absolute; right: 16px; top: 50%; 
  transform: translateY(-50%); color: #999; font-size: 0.8rem; pointer-events: none; 
}

/* 가로 배치 그룹 (성별/결혼 여부 등) */
.row-group {
  display: flex;
  gap: 20px;
}
.half { flex: 1; }

/* 도움말 텍스트 */
.helper-text { font-size: 0.85rem; color: #888; margin-top: 4px; }

/* 하단 버튼 영역 */
.form-actions {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-top: 20px;
}

.btn-back {
  padding: 16px 40px;
  font-size: 1.1rem; font-weight: 600;
  color: #666; background: white;
  border: 1px solid #ddd; border-radius: 12px;
  cursor: pointer; transition: all 0.2s;
}
.btn-back:hover { background: #f9f9f9; }

.btn-submit {
  padding: 16px 60px;
  font-size: 1.1rem; font-weight: 700;
  color: white; background: #2cb398;
  border: none; border-radius: 12px;
  cursor: pointer; transition: all 0.2s;
  box-shadow: 0 10px 20px rgba(44, 179, 152, 0.2);
}
.btn-submit:hover:not(:disabled) {
  background: #249e85; transform: translateY(-3px);
  box-shadow: 0 15px 30px rgba(44, 179, 152, 0.3);
}
.btn-submit:disabled { background: #ccc; cursor: not-allowed; box-shadow: none; }

/* 로딩 스피너 */
.state-overlay {
  height: 80vh; display: flex; flex-direction: column; justify-content: center; align-items: center;
}
.spinner {
  width: 50px; height: 50px; border: 5px solid #f3f3f3; border-top: 5px solid #2cb398;
  border-radius: 50%; animation: spin 1s linear infinite; margin-bottom: 20px;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* 애니메이션 */
.fade-in-up { animation: fadeInUp 0.6s ease forwards; opacity: 0; transform: translateY(30px); }
@keyframes fadeInUp { to { opacity: 1; transform: translateY(0); } }

/* 반응형 (모바일) */
@media (max-width: 900px) {
  .form-layout { grid-template-columns: 1fr; gap: 24px; } /* 2열 -> 1열 */
  .page-title { font-size: 2rem; }
  .form-actions { flex-direction: column-reverse; }
  .btn-submit, .btn-back { width: 100%; }
}
</style>