<template>
  <div class="page-container">
    
    <header class="header-section fade-in-up">
      <h1 class="title">AI와 함께하는 제주 여행 🍊</h1>
      <p class="subtitle">
        취향을 선택해주시면 <b>딱 맞는 여행 코스</b>를 만들어드려요.
      </p>
    </header>

    <div class="grid-layout fade-in-up delay-1">
      
      <section class="step-card wide-card">
        <div class="step-header centered-header">
          <div class="badge-row">
            <span class="step-badge">STEP 1</span>
          </div>
          <h2 class="question">제주에 얼마나 머무르시나요?</h2>
          <p class="hint">1일 ~ 7일 중 선택</p>
        </div>
        
        <div class="options-wrapper days-wrapper">
          <button
            v-for="d in howLongOptions"
            :key="d"
            type="button"
            class="option-pill circle-pill"
            :class="{ active: form.HOW_LONG === d }"
            @click="form.HOW_LONG = d"
          >
            <span class="day-num">{{ d }}</span>
            <span class="day-text">일</span>
          </button>
        </div>
      </section>

      <section class="step-card wide-card">
        <div class="step-header centered-header">
          <div class="badge-row">
            <span class="step-badge">STEP 2</span>
          </div>
          <h2 class="question">선호하는 여행 스타일은?</h2>
          <p class="hint">자연 속 힐링 vs 도심 속 핫플레이스</p>
        </div>
        
        <div class="style-slider-container">
          <div class="style-labels">
            <span>🌿 자연 선호</span>
            <span>중립</span>
            <span>도시 선호 🏙️</span>
          </div>
          
          <div class="style-track">
            <button
              v-for="o in styleOptions"
              :key="o.value"
              type="button"
              class="style-node"
              :class="{ active: form.TRAVEL_STYL_1 === o.value }"
              @click="form.TRAVEL_STYL_1 = o.value"
              :title="o.label"
            >
              <span class="node-label" :class="{ show: form.TRAVEL_STYL_1 === o.value }">
                {{ o.label }}
              </span>
            </button>
            <div class="track-line"></div>
          </div>
        </div>
      </section>

      <section class="step-card">
        <div class="step-header">
          <div class="badge-row">
            <span class="step-badge">STEP 3</span>
          </div>
          <h2 class="question">여행의 주된 목적은?</h2>
          <p class="hint">가장 중요한 이유 하나</p>
        </div>
        <div class="options-wrapper motive-grid">
          <button
            v-for="m in motiveOptions"
            :key="m"
            type="button"
            class="option-pill"
            :class="{ active: form.TRAVEL_MOTIVE_1 === m }"
            @click="form.TRAVEL_MOTIVE_1 = m"
          >
            {{ m }}
          </button>
        </div>
      </section>

      <section class="step-card">
        <div class="step-header">
          <div class="badge-row">
            <span class="step-badge">STEP 4</span>
          </div>
          <h2 class="question">누구와 함께인가요?</h2>
          <p class="hint">동반자 유형 선택</p>
        </div>
        <div class="options-wrapper">
          <button
            v-for="c in accompanyOptions"
            :key="c"
            type="button"
            class="option-pill"
            :class="{ active: form.TRAVEL_STATUS_ACCOMPANY === c }"
            @click="form.TRAVEL_STATUS_ACCOMPANY = c"
          >
            {{ c }}
          </button>
        </div>
      </section>

    </div>

    <div class="action-section fade-in-up delay-2">
      <p v-if="submitError" class="error-msg">⚠️ {{ submitError }}</p>
      
      <button 
        class="submit-btn" 
        type="button" 
        @click="goRecommend" 
        :disabled="!canSubmit"
      >
        <span v-if="canSubmit">AI 맞춤 일정 생성하기 ✨</span>
        <span v-else>모든 항목을 선택해주세요</span>
      </button>
    </div>

  </div>
</template>

<script setup>
/**
 * [Vue 3 Composition API]
 * - reactive: 객체 형태의 반응형 상태를 선언할 때 사용합니다. (폼 데이터용)
 * - computed: 종속된 데이터가 변할 때마다 자동으로 다시 계산되는 값입니다. (유효성 검사용)
 * - ref: 단일 값(숫자, 문자열 등)의 반응형 상태를 선언할 때 사용합니다. (에러 메시지용)
 */
import { reactive, computed, ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const submitError = ref('')

// --- [Form 데이터 상태 관리] ---
// 주의: 백엔드 API(Serializer2)가 요구하는 필드명(대문자 포함)을 
// 절대 변경하면 안 됩니다. 화면에 어떻게 보이든 데이터 키값은 유지해야 합니다.
const form = reactive({
  TRAVEL_STYL_1: 4,        // 여행 스타일 (1:자연 ~ 7:도시), 기본값 4(중립)
  TRAVEL_STATUS_ACCOMPANY: '', // 동반자 (문자열)
  TRAVEL_MOTIVE_1: '',     // 여행 동기 (문자열)
  HOW_LONG: 3,             // 여행 기간 (1~7일), 기본값 3
})

// --- [선택지 데이터 (상수)] ---
// 화면 렌더링을 위한 배열 데이터입니다.
const howLongOptions = [1, 2, 3, 4, 5, 6, 7]

const styleOptions = [
  { value: 1, label: '자연 매우선호' },
  { value: 2, label: '자연 중간선호' },
  { value: 3, label: '자연 약간선호' },
  { value: 4, label: '중립' },
  { value: 5, label: '도시 약간선호' },
  { value: 6, label: '도시 중간선호' },
  { value: 7, label: '도시 매우선호' },
]

const accompanyOptions = [
  '나홀로 여행',
  '2인 여행(가족 외)',
  '3인 이상 여행(가족 외)',
  '2인 가족 여행',
  '자녀 동반 여행',
  '부모 동반 여행',
  '3대 동반 여행(친척 포함)',
]

const motiveOptions = [
  '일상 탈출',
  '휴식과 충전',
  '동반자와의 유대감',
  '자아 성찰',
  'SNS / 과시',
  '운동 / 건강',
  '새로운 경험',
  '문화 탐방 / 교육',
  '특별한 목적(칠순 등)',
  '기타',
]

// --- [유효성 검사 (Computed)] ---
// 사용자가 폼을 조작할 때마다 실시간으로 이 함수가 실행되어 
// 버튼 활성화 여부(true/false)를 결정합니다.
const canSubmit = computed(() => {
  return (
    Number.isFinite(form.HOW_LONG) && form.HOW_LONG >= 1 && form.HOW_LONG <= 7 &&
    Number.isFinite(form.TRAVEL_STYL_1) && form.TRAVEL_STYL_1 >= 1 && form.TRAVEL_STYL_1 <= 7 &&
    !!form.TRAVEL_STATUS_ACCOMPANY && // 빈 문자열 체크
    !!form.TRAVEL_MOTIVE_1            // 빈 문자열 체크
  )
})

// --- [페이지 이동 함수] ---
function goRecommend() {
  submitError.value = ''

  // 한 번 더 방어 코드: 필수 값이 없으면 함수 종료
  if (!canSubmit.value) {
    submitError.value = '필수 항목(여행기간/여행스타일/여행동기/동반현황)을 확인해주세요.'
    return
  }

  // 결과 페이지로 이동하면서 입력받은 데이터를 Query String으로 넘깁니다.
  // 예: /recommend/result?HOW_LONG=3&TRAVEL_STYL_1=4...
  // 이렇게 해야 결과 페이지에서 새로고침해도 입력값이 유지됩니다.
  router.push({
    name: 'route-recommend-results',
    query: {
      HOW_LONG: String(form.HOW_LONG),
      TRAVEL_STYL_1: String(form.TRAVEL_STYL_1),
      TRAVEL_STATUS_ACCOMPANY: form.TRAVEL_STATUS_ACCOMPANY,
      TRAVEL_MOTIVE_1: form.TRAVEL_MOTIVE_1,
    },
  })
}
</script>

<style scoped>
/* [스타일링 전략: PC 중심의 Wide Layout]
  - max-width: 1200px 설정으로 대화면 모니터에서도 안정감 있게 보입니다.
  - Grid Layout을 활용해 2열 배치를 기본으로 하되, 
    미디어 쿼리(@media)를 통해 모바일에서는 1열로 자동 전환합니다.
*/

/* 페이지 전체 래퍼 */
.page-container {
  max-width: 1200px; 
  margin: 0 auto;
  padding: 60px 20px 100px; /* 상단 여백 넉넉히, 하단 버튼 공간 확보 */
  background-color: #f5f7fa; /* 아주 연한 회색 배경 */
  min-height: 100vh;
  font-family: -apple-system, BlinkMacSystemFont, "Pretendard", Roboto, sans-serif;
}

/* 헤더 텍스트 */
.header-section {
  text-align: center;
  margin-bottom: 50px;
}
.title {
  font-size: 2.5rem; 
  font-weight: 800;
  color: #222;
  margin-bottom: 16px;
  letter-spacing: -0.03em;
}
.subtitle {
  font-size: 1.1rem;
  color: #666;
  line-height: 1.6;
}
.subtitle b { color: #2cb398; }

/* [CSS Grid Layout]
  - grid-template-columns: repeat(2, 1fr); -> 화면을 정확히 반반(1:1)으로 나눕니다.
  - gap: 24px; -> 카드 사이의 간격을 띄웁니다.
*/
.grid-layout {
  display: grid;
  grid-template-columns: repeat(2, 1fr); 
  gap: 24px;
  margin-bottom: 60px;
}

/* [카드 컴포넌트 스타일]
  - 흰색 배경에 둥근 모서리, 그리고 은은한 그림자(box-shadow)를 주어
    배경 위로 떠 있는 듯한 입체감을 줍니다.
*/
.step-card {
  background: white;
  border-radius: 24px;
  padding: 40px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.03);
  border: 1px solid rgba(0,0,0,0.02);
  display: flex;
  flex-direction: column;
}

/* [Wide Card 유틸리티 클래스]
  - grid-column: span 2; -> 그리드의 2칸을 혼자 다 차지하게 만듭니다.
  - STEP 1, STEP 2 처럼 가로로 넓게 보여줘야 할 때 사용합니다.
*/
.wide-card {
  grid-column: span 2;
}

/* 카드 내부 헤더 */
.step-header { margin-bottom: 24px; text-align: left; }
.centered-header { text-align: center; } /* wide-card일 때는 중앙 정렬 */

.badge-row { margin-bottom: 12px; }
.step-badge {
  font-size: 0.85rem; font-weight: 800; color: #2cb398;
  background: #e6f7f4; padding: 6px 10px; border-radius: 8px;
}
.question { font-size: 1.5rem; font-weight: 700; color: #333; margin: 0 0 6px; }
.hint { font-size: 0.95rem; color: #999; margin: 0; }

/* 옵션 버튼들을 감싸는 컨테이너 */
.options-wrapper {
  display: flex;
  flex-wrap: wrap; /* 공간이 부족하면 자동으로 줄바꿈 */
  gap: 12px;
}

/* 날짜 선택 버튼 래퍼 (중앙 정렬) */
.days-wrapper { 
  justify-content: center; 
  gap: 20px; 
}

/* [기본 알약(Pill) 버튼 스타일]
  - transition 속성으로 마우스 호버나 활성화 시 부드럽게 색이 변하도록 합니다.
*/
.option-pill {
  padding: 14px 24px;
  background-color: #f8f9fa;
  border: 1px solid #eee;
  border-radius: 12px;
  font-size: 1rem;
  color: #555;
  cursor: pointer;
  transition: all 0.2s ease;
  font-weight: 500;
}
.option-pill:hover { background-color: #edf2f7; transform: translateY(-2px); }
/* 선택되었을 때 (.active) 민트색으로 강조 */
.option-pill.active {
  background-color: #2cb398; color: white; border-color: #2cb398;
  font-weight: 700; 
  box-shadow: 0 4px 12px rgba(44, 179, 152, 0.3);
  transform: translateY(-2px);
}

/* STEP 1용 원형 버튼 */
.circle-pill {
  width: 74px; height: 74px; /* 정사각형 */
  border-radius: 50%; /* 완전한 원 */
  padding: 0;
  display: flex; flex-direction: column; justify-content: center; align-items: center;
}
.day-num { font-size: 1.5rem; font-weight: 700; line-height: 1; }
.day-text { font-size: 0.85rem; margin-top: 2px; }

/* STEP 2용 스타일 슬라이더 UI */
.style-slider-container { padding: 20px 10px; }
.style-labels { display: flex; justify-content: space-between; font-size: 0.9rem; color: #888; margin-bottom: 12px; font-weight: 600; }

.style-track {
  position: relative;
  display: flex; justify-content: space-between; align-items: center;
  height: 60px;
}
/* 슬라이더 배경 선 */
.track-line {
  position: absolute; top: 50%; left: 10px; right: 10px; height: 4px;
  background: #eee; z-index: 1; border-radius: 2px;
}
/* 슬라이더 노드(점) */
.style-node {
  width: 24px; height: 24px; border-radius: 50%;
  background: white; border: 4px solid #ddd;
  z-index: 2; cursor: pointer; position: relative; transition: all 0.2s;
  padding: 0;
}
.style-node:hover { transform: scale(1.2); border-color: #aaa; }
.style-node.active {
  background: #2cb398; border-color: #2cb398; transform: scale(1.3);
  box-shadow: 0 0 0 4px rgba(44, 179, 152, 0.2);
}
/* 노드 선택 시 뜨는 말풍선 */
.node-label {
  position: absolute; top: -35px; left: 50%; transform: translateX(-50%);
  background: #333; color: white; padding: 4px 8px; border-radius: 6px;
  font-size: 0.8rem; white-space: nowrap; opacity: 0; transition: opacity 0.2s; pointer-events: none;
}
.node-label.show { opacity: 1; }

/* 하단 버튼 섹션 */
.action-section { text-align: center; margin-top: 40px; }
.submit-btn {
  padding: 20px 60px; font-size: 1.2rem; font-weight: 800; color: white;
  background-color: #2cb398; border: none; border-radius: 16px; cursor: pointer;
  transition: all 0.2s; box-shadow: 0 10px 25px rgba(44, 179, 152, 0.4);
}
.submit-btn:hover:not(:disabled) {
  background-color: #24917d; transform: translateY(-3px);
  box-shadow: 0 15px 30px rgba(44, 179, 152, 0.5);
}
.submit-btn:disabled { background-color: #ccc; cursor: not-allowed; box-shadow: none; }
.error-msg { color: #e74c3c; margin-bottom: 16px; font-weight: 600; animation: shake 0.4s; }

/* 흔들림 애니메이션 (에러 발생 시) */
@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-5px); }
  75% { transform: translateX(5px); }
}

/* 등장 애니메이션 */
.fade-in-up { opacity: 0; transform: translateY(20px); animation: fadeInUp 0.8s ease forwards; }
.delay-1 { animation-delay: 0.1s; }
.delay-2 { animation-delay: 0.2s; }
@keyframes fadeInUp { to { opacity: 1; transform: translateY(0); } }

/* [반응형 미디어 쿼리]
  - 768px 이하(모바일/태블릿 세로)에서는 
    그리드를 1열로 바꾸고, wide-card 속성을 해제하여 모든 카드가 한 줄씩 차지하게 합니다.
*/
@media (max-width: 768px) {
  .grid-layout { grid-template-columns: 1fr; }
  .wide-card { grid-column: span 1; } 
  .title { font-size: 1.8rem; }
  .page-container { padding: 40px 16px 80px; }
  .submit-btn { width: 100%; }
}
</style>