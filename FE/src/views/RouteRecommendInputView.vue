<template>
  <div class="page-container">
    
    <div class="bg-decoration circle-1"></div>
    <div class="bg-decoration circle-2"></div>

    <header class="header-section fade-in-up">
      <div class="title-group">
        <span class="sub-badge">AI TRAVEL PLANNER</span>
        <h1 class="title">제주 여행, <span>AI</span>가 설계해드려요</h1>
        <p class="subtitle">
          복잡한 계획은 그만! 취향만 알려주시면 <b>최적의 동선</b>을 만들어 드립니다.
        </p>
      </div>
    </header>

    <div class="grid-layout fade-in-up delay-1">
      
      <section class="step-card wide-card">
        <div class="card-content-wrapper">
          <div class="step-info">
            <span class="step-number">01</span>
            <h3 class="step-title">일정 선택</h3>
            <p class="step-desc">제주에 며칠 동안 머무르시나요?</p>
          </div>
          
          <div class="options-grid days-grid">
            <button
              v-for="d in howLongOptions"
              :key="d"
              type="button"
              class="selection-card day-card"
              :class="{ active: form.HOW_LONG === d }"
              @click="form.HOW_LONG = d"
            >
              <span class="day-label">{{ d }}일</span>
              <span class="day-sub" v-if="d === 1">당일치기</span>
              <span class="day-sub" v-else>{{ d-1 }}박 {{ d }}일</span>
            </button>
          </div>
        </div>
      </section>

      <section class="step-card wide-card">
        <div class="card-content-wrapper">
          <div class="step-info">
            <span class="step-number">02</span>
            <h3 class="step-title">여행 스타일</h3>
            <p class="step-desc">자연 속 힐링인가요, 도심 속 핫플인가요?</p>
          </div>
          
          <div class="slider-area">
            <div class="visual-labels">
              <div class="label-box nature" :class="{ on: form.TRAVEL_STYL_1 <= 3 }">
                <span class="icon">🌿</span>
                <strong>자연 힐링</strong>
              </div>
              <div class="label-box city" :class="{ on: form.TRAVEL_STYL_1 >= 5 }">
                <span class="icon">🏙️</span>
                <strong>도시 핫플</strong>
              </div>
            </div>
            
            <div class="style-track">
              <div class="track-bg"></div>
              <div class="track-fill" :style="{ width: ((form.TRAVEL_STYL_1 - 1) / 6 * 100) + '%' }"></div>
              
              <button
                v-for="o in styleOptions"
                :key="o.value"
                type="button"
                class="style-point"
                :class="{ active: form.TRAVEL_STYL_1 === o.value }"
                @click="form.TRAVEL_STYL_1 = o.value"
                :style="{ left: ((o.value - 1) / 6 * 100) + '%' }"
              >
                <div class="tooltip">{{ o.label }}</div>
              </button>
            </div>
          </div>
        </div>
      </section>

      <section class="step-card">
        <div class="step-header-simple">
          <span class="step-number-small">03</span>
          <h3 class="step-title-small">여행의 주된 목적</h3>
        </div>
        
        <div class="options-grid motive-grid">
          <button
            v-for="(m, idx) in motiveOptions"
            :key="m"
            type="button"
            class="selection-card box-card"
            :class="{ active: form.TRAVEL_MOTIVE_1 === m }"
            @click="form.TRAVEL_MOTIVE_1 = m"
          >
            <span class="card-icon">{{ getMotiveIcon(idx) }}</span>
            <span class="card-text">{{ m }}</span>
          </button>
        </div>
      </section>

      <section class="step-card">
        <div class="step-header-simple">
          <span class="step-number-small">04</span>
          <h3 class="step-title-small">동반자 유형</h3>
        </div>
        
        <div class="options-grid accompany-grid">
          <button
            v-for="(c, idx) in accompanyOptions"
            :key="c"
            type="button"
            class="selection-card box-card"
            :class="{ active: form.TRAVEL_STATUS_ACCOMPANY === c }"
            @click="form.TRAVEL_STATUS_ACCOMPANY = c"
          >
            <span class="card-icon">{{ getAccompanyIcon(idx) }}</span>
            <span class="card-text">{{ c }}</span>
          </button>
        </div>
      </section>

    </div>

    <div class="action-bar fade-in-up delay-2">
      <div class="action-content">
        <div class="status-msg">
          <span v-if="canSubmit" class="ready">✨ 모든 준비가 완료되었어요!</span>
          <span v-else class="not-ready">👉 아직 선택하지 않은 항목이 있어요</span>
          <p v-if="submitError" class="error-text">{{ submitError }}</p>
        </div>
        <button 
          class="submit-btn-lg" 
          type="button" 
          @click="goRecommend" 
          :disabled="!canSubmit"
        >
          AI 일정 생성하기
          <span class="arrow">→</span>
        </button>
      </div>
    </div>

  </div>
</template>

<script setup>
import { reactive, computed, ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const submitError = ref('')

// [데이터 유지]
const form = reactive({
  TRAVEL_STYL_1: 4,
  TRAVEL_STATUS_ACCOMPANY: '',
  TRAVEL_MOTIVE_1: '',
  HOW_LONG: 3,
})

const howLongOptions = [1, 2, 3, 4, 5, 6, 7]

const styleOptions = [
  { value: 1, label: '완전 자연' },
  { value: 2, label: '자연 위주' },
  { value: 3, label: '자연 약간' },
  { value: 4, label: '반반' },
  { value: 5, label: '도시 약간' },
  { value: 6, label: '도시 위주' },
  { value: 7, label: '완전 도시' },
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

// [UI 꾸미기용 아이콘 매핑 함수 (로직 영향 X)]
const getMotiveIcon = (idx) => {
  const icons = ['🏃', '🍃', '🤝', '🧘', '📸', '💪', '🔥', '🎓', '🎉', '🎸']
  return icons[idx] || '✨'
}

const getAccompanyIcon = (idx) => {
  const icons = ['🎒', '👫', '👨‍👩‍👧‍👦', '💑', '👶', '👵', '🚌']
  return icons[idx] || '✈️'
}

const canSubmit = computed(() => {
  return (
    Number.isFinite(form.HOW_LONG) &&
    Number.isFinite(form.TRAVEL_STYL_1) &&
    !!form.TRAVEL_STATUS_ACCOMPANY &&
    !!form.TRAVEL_MOTIVE_1
  )
})

function goRecommend() {
  submitError.value = ''
  if (!canSubmit.value) {
    submitError.value = '필수 항목을 모두 선택해주세요.'
    return
  }
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
/* [PC 최적화: 데스크톱 앱 스타일] */
.page-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 80px 20px 140px; /* 하단 액션바 공간 확보 */
  background-color: #f8f9fa;
  min-height: 100vh;
  position: relative;
  overflow: hidden; /* 배경 장식 잘림 처리 */
  font-family: -apple-system, BlinkMacSystemFont, "Pretendard", Roboto, sans-serif;
}

/* 배경 장식 (은은한 원형) */
.bg-decoration {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  z-index: 0;
  opacity: 0.4;
}
.circle-1 { top: -100px; right: -100px; width: 500px; height: 500px; background: #d1fae5; }
.circle-2 { bottom: 100px; left: -100px; width: 400px; height: 400px; background: #e0f2fe; }

/* 1. 헤더 (타이포그래피 강화) */
.header-section {
  text-align: center;
  margin-bottom: 60px;
  position: relative;
  z-index: 1;
}
.sub-badge {
  display: inline-block;
  font-size: 0.85rem;
  font-weight: 800;
  color: #2cb398;
  letter-spacing: 0.1em;
  margin-bottom: 12px;
  background: rgba(44, 179, 152, 0.1);
  padding: 6px 12px;
  border-radius: 20px;
}
.title {
  font-size: 3rem;
  font-weight: 900;
  color: #111;
  margin-bottom: 16px;
  letter-spacing: -0.03em;
}
.title span { color: #2cb398; }
.subtitle {
  font-size: 1.1rem;
  color: #555;
  line-height: 1.6;
}

/* 2. 그리드 레이아웃 */
.grid-layout {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 30px;
  position: relative;
  z-index: 1;
}

/* 카드 공통 스타일 (박스형 + 부드러운 그림자) */
.step-card {
  background: white;
  border-radius: 24px;
  padding: 40px;
  box-shadow: 0 10px 40px rgba(0,0,0,0.03);
  border: 1px solid rgba(0,0,0,0.02);
  transition: transform 0.3s ease;
}
.step-card:hover { transform: translateY(-5px); box-shadow: 0 15px 50px rgba(0,0,0,0.06); }
.wide-card { grid-column: span 2; }

/* 카드 내부 헤더 (좌측 정보 + 우측 컨텐츠 구조) */
.card-content-wrapper {
  display: flex;
  gap: 40px;
  align-items: center;
}
.step-info {
  width: 240px;
  flex-shrink: 0;
  border-right: 1px solid #f0f0f0;
  padding-right: 20px;
}
.step-number {
  font-size: 3rem;
  font-weight: 900;
  color: #e0e0e0;
  line-height: 1;
  margin-bottom: 10px;
  display: block;
}
.step-title { font-size: 1.5rem; font-weight: 800; margin: 0 0 8px; color: #222; }
.step-desc { font-size: 0.95rem; color: #888; margin: 0; line-height: 1.4; }

/* STEP 3, 4용 심플 헤더 */
.step-header-simple {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f5f5f5;
}
.step-number-small {
  font-size: 1.1rem; font-weight: 800; color: #2cb398;
  background: #e6f7f4; padding: 4px 10px; border-radius: 8px;
}
.step-title-small { font-size: 1.3rem; font-weight: 800; color: #333; margin: 0; }


/* --- [STEP 1: 캘린더 스타일 날짜 선택] --- */
.options-grid.days-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  flex: 1;
}
.selection-card {
  border: 2px solid #f0f0f0;
  background: #fff;
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.25, 0.8, 0.25, 1);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}
.day-card {
  width: 80px; height: 90px;
}
.day-label { font-size: 1.3rem; font-weight: 800; color: #333; }
.day-sub { font-size: 0.75rem; color: #999; margin-top: 4px; }

.selection-card:hover { border-color: #2cb398; background: #f0fdfa; }
.selection-card.active {
  border-color: #2cb398;
  background: #2cb398;
  box-shadow: 0 8px 20px rgba(44, 179, 152, 0.3);
  transform: scale(1.05);
}
.selection-card.active * { color: white; }


/* --- [STEP 2: 고급 슬라이더] --- */
.slider-area { flex: 1; padding: 0 20px; }
.visual-labels {
  display: flex; justify-content: space-between; margin-bottom: 30px;
}
.label-box {
  display: flex; flex-direction: column; align-items: center; opacity: 0.4; transition: opacity 0.3s;
}
.label-box.on { opacity: 1; }
.label-box .icon { font-size: 2rem; margin-bottom: 6px; }
.label-box strong { font-size: 0.9rem; color: #333; }

.style-track { position: relative; height: 40px; display: flex; align-items: center; }
.track-bg {
  position: absolute; top: 50%; left: 0; right: 0; height: 8px;
  background: #eee; border-radius: 4px; transform: translateY(-50%);
}
.track-fill {
  position: absolute; top: 50%; left: 0; height: 8px;
  background: #2cb398; border-radius: 4px; transform: translateY(-50%);
  transition: width 0.3s ease;
}
.style-point {
  position: absolute; top: 50%; width: 24px; height: 24px;
  background: #fff; border: 4px solid #ddd; border-radius: 50%;
  transform: translate(-50%, -50%); cursor: pointer; transition: all 0.2s;
  z-index: 2;
}
.style-point:hover { transform: translate(-50%, -50%) scale(1.2); }
.style-point.active {
  background: #2cb398; border-color: #2cb398;
  width: 32px; height: 32px;
  box-shadow: 0 0 0 5px rgba(44, 179, 152, 0.2);
}
.tooltip {
  position: absolute; bottom: 35px; left: 50%; transform: translateX(-50%);
  background: #333; color: white; padding: 4px 10px; border-radius: 6px;
  font-size: 0.8rem; white-space: nowrap; opacity: 0; transition: 0.2s;
  pointer-events: none;
}
.style-point.active .tooltip, .style-point:hover .tooltip { opacity: 1; transform: translateX(-50%) translateY(-5px); }


/* --- [STEP 3 & 4: 박스형 그리드] --- */
.options-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); /* 반응형 그리드 */
  gap: 16px;
}
.box-card {
  padding: 20px 10px;
  height: 110px; /* 카드 높이 고정 */
}
.card-icon { font-size: 2rem; margin-bottom: 10px; }
.card-text { font-size: 0.95rem; font-weight: 600; color: #555; text-align: center; }


/* --- [하단 액션 바] --- */
.action-bar {
  position: fixed; bottom: 0; left: 0; right: 0;
  background: white; border-top: 1px solid #eee;
  padding: 20px 0; z-index: 100;
  box-shadow: 0 -5px 20px rgba(0,0,0,0.05);
}
.action-content {
  max-width: 1200px; margin: 0 auto; padding: 0 20px;
  display: flex; justify-content: space-between; align-items: center;
}
.status-msg { font-size: 0.95rem; font-weight: 600; }
.ready { color: #2cb398; }
.not-ready { color: #888; }
.error-text { color: #e74c3c; font-size: 0.8rem; margin-top: 4px; }

.submit-btn-lg {
  padding: 16px 40px; font-size: 1.1rem; font-weight: 800; color: white;
  background-color: #2cb398; border: none; border-radius: 12px;
  cursor: pointer; transition: all 0.2s; display: flex; align-items: center; gap: 10px;
}
.submit-btn-lg:hover:not(:disabled) {
  background-color: #24917d; transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(44, 179, 152, 0.3);
}
.submit-btn-lg:disabled { background-color: #ccc; cursor: not-allowed; }
.arrow { font-size: 1.2rem; transition: transform 0.2s; }
.submit-btn-lg:hover .arrow { transform: translateX(4px); }

/* 애니메이션 */
.fade-in-up { opacity: 0; transform: translateY(20px); animation: fadeInUp 0.8s ease forwards; }
.delay-1 { animation-delay: 0.1s; }
.delay-2 { animation-delay: 0.2s; }
@keyframes fadeInUp { to { opacity: 1; transform: translateY(0); } }

/* 반응형 (태블릿/모바일) */
@media (max-width: 900px) {
  .grid-layout { grid-template-columns: 1fr; }
  .wide-card { grid-column: span 1; }
  .card-content-wrapper { flex-direction: column; align-items: flex-start; gap: 20px; }
  .step-info { width: 100%; border-right: none; border-bottom: 1px solid #f0f0f0; padding-bottom: 16px; margin-bottom: 10px; }
  .slider-area { width: 100%; padding: 0; }
  .action-content { flex-direction: column; gap: 16px; text-align: center; }
  .submit-btn-lg { width: 100%; justify-content: center; }
}
</style>