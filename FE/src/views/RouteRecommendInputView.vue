<!-- RouteRecommendInputView.vue (Serializer2 적용 버전) -->
<template>
  <div class="page">
    <header class="hero">
      <h1>AI와 함께 제주 여행 계획하기</h1>
      <p class="sub">
        아래 내용을 한 번에 입력하면, AI가 나에게 어울리는 제주 여행 일정을 만들어줘요.
      </p>
    </header>

    <!-- STEP 1: 여행 기간(HOW_LONG) -->
    <section class="stepCard">
      <div class="stepTop">
        <span class="stepBadge">STEP 1</span>
        <h2>얼마나 머무를 예정인가요?</h2>
        <p class="hint">총 여행 날짜(1~7일)를 선택해주세요.</p>
      </div>

      <div class="pillRow">
        <button
          v-for="d in howLongOptions"
          :key="d"
          type="button"
          class="pill"
          :class="{ active: form.HOW_LONG === d }"
          @click="form.HOW_LONG = d"
        >
          {{ d }}일
        </button>
      </div>
    </section>

    <!-- STEP 2: 여행 스타일(TRAVEL_STYL_1: 1~7 숫자) -->
    <section class="stepCard">
      <div class="stepTop">
        <span class="stepBadge">STEP 2</span>
        <h2>여행스타일은 어떤 쪽에 가까운가요?</h2>
        <p class="hint">자연/도시 선호도를 선택해주세요.</p>
      </div>

      <div class="pillRow">
        <button
          v-for="o in styleOptions"
          :key="o.value"
          type="button"
          class="pill"
          :class="{ active: form.TRAVEL_STYL_1 === o.value }"
          @click="form.TRAVEL_STYL_1 = o.value"
        >
          {{ o.label }}
        </button>
      </div>
    </section>

    <!-- STEP 3: 여행 동기(TRAVEL_MOTIVE_1: 단일 선택) -->
    <section class="stepCard">
      <div class="stepTop">
        <span class="stepBadge">STEP 3</span>
        <h2>여행동기는 무엇인가요?</h2>
        <p class="hint">하나만 선택해주세요.</p>
      </div>

      <div class="pillRow">
        <button
          v-for="m in motiveOptions"
          :key="m"
          type="button"
          class="pill"
          :class="{ active: form.TRAVEL_MOTIVE_1 === m }"
          @click="form.TRAVEL_MOTIVE_1 = m"
        >
          {{ m }}
        </button>
      </div>
    </section>

    <!-- STEP 4: 동반 현황(TRAVEL_STATUS_ACCOMPANY) -->
    <section class="stepCard">
      <div class="stepTop">
        <span class="stepBadge">STEP 4</span>
        <h2>동반현황은 어떻게 되나요?</h2>
        <p class="hint">누구와 떠나는지 선택해주세요.</p>
      </div>

      <div class="pillRow">
        <button
          v-for="c in accompanyOptions"
          :key="c"
          type="button"
          class="pill"
          :class="{ active: form.TRAVEL_STATUS_ACCOMPANY === c }"
          @click="form.TRAVEL_STATUS_ACCOMPANY = c"
        >
          {{ c }}
        </button>
      </div>
    </section>

    <!-- CTA -->
    <div class="ctaWrap">
      <button class="cta" type="button" @click="goRecommend" :disabled="!canSubmit">
        AI에게 제주 일정 만들기
      </button>
      <p v-if="submitError" class="warn center">{{ submitError }}</p>
    </div>
  </div>
</template>

<script setup>
/**
 * ✅ 프론트 최소 이해 세트(이 파일)
 * 1) 클릭 이벤트로 form 값을 채운다
 * 2) 버튼 클릭(goRecommend) → 결과 페이지로 이동(router.push)
 * 3) 이때 "query"로 입력값을 전달한다(새로고침해도 남음)
 */

import { reactive, computed, ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const submitError = ref('')

/** ✅ Serializer2 필드명 그대로 form을 만든다(대문자 포함) */
const form = reactive({
  TRAVEL_STYL_1: 4, // 기본: 중립(1~7)
  TRAVEL_STATUS_ACCOMPANY: '',
  TRAVEL_MOTIVE_1: '',
  HOW_LONG: 3, // 1~7
})

/** 선택지 */
const howLongOptions = [1,2,3,4,5,6,7]

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
  '특별한 목적(칠순, 신혼, 수학여행 등)',
  '기타',
]

/** 제출 가능 조건(필수값) */
const canSubmit = computed(() => {
  return (
    Number.isFinite(form.HOW_LONG) && form.HOW_LONG >= 1 && form.HOW_LONG <= 7 &&
    Number.isFinite(form.TRAVEL_STYL_1) && form.TRAVEL_STYL_1 >= 1 && form.TRAVEL_STYL_1 <= 7 &&
    !!form.TRAVEL_STATUS_ACCOMPANY &&
    !!form.TRAVEL_MOTIVE_1
  )
})

function goRecommend() {
  submitError.value = ''

  if (!canSubmit.value) {
    submitError.value = '필수 항목(여행기간/여행스타일/여행동기/동반현황)을 확인해주세요.'
    return
  }

  // ✅ 결과 페이지로 query 전달(Serializer2 키 그대로)
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
/* 너 기존 스타일 그대로 써도 됨 */
.page { max-width: 900px; margin: 0 auto; padding: 34px 18px 60px; background: #f7f9ff; min-height: 100vh; }
.hero { margin: 10px 0 18px; }
.hero h1 { margin: 0 0 8px; font-size: 30px; letter-spacing: -0.3px; }
.sub { margin: 0; color: #6b7a9a; font-size: 14px; }
.stepCard { background: #fff; border: 1px solid #e9efff; border-radius: 16px; padding: 18px; margin-top: 14px; }
.stepTop { margin-bottom: 12px; }
.stepBadge { display: inline-block; font-size: 12px; color: #6b7a9a; margin-bottom: 8px; }
.stepTop h2 { margin: 0 0 6px; font-size: 18px; }
.hint { margin: 0; font-size: 13px; color: #7d8aa7; }
.pillRow { display: flex; flex-wrap: wrap; gap: 10px; }
.pill { border: 1px solid #cfe0ff; background: #fff; color: #2a4b8d; padding: 10px 14px; border-radius: 999px; cursor: pointer; font-size: 13px; }
.pill.active { border-color: #2a4b8d; font-weight: 700; }
.ctaWrap { margin-top: 22px; display: flex; flex-direction: column; gap: 10px; align-items: center; }
.cta { width: 100%; max-width: 860px; padding: 16px 18px; border-radius: 14px; border: none; background: #79aafc; color: #fff; font-size: 15px; cursor: pointer; }
.cta:disabled { opacity: 0.6; cursor: not-allowed; }
.warn { margin: 10px 0 0; color: #dc2626; font-size: 12px; }
.center { text-align: center; }
</style>
