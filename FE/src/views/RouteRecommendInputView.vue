<template>
  <div class="page">
    <!-- SVG 상단 타이틀 영역 -->
    <header class="hero">
      <h1>AI와 함께 제주 여행 계획하기</h1>
      <p class="sub">
        아래 내용을 한 번에 입력하면, AI가 나에게 어울리는 제주 여행 일정을 만들어줘요.
      </p>
    </header>

    <!-- STEP 1: 총 여행 날짜 -->
    <section class="stepCard">
      <div class="stepTop">
        <span class="stepBadge">STEP 1</span>
        <h2>얼마나 머무를 예정인가요?</h2>
        <p class="hint">총 여행 날짜(1~8일)를 선택해주세요.</p>
      </div>

      <div class="pillRow">
        <button
          v-for="d in daysOptions"
          :key="d"
          type="button"
          class="pill"
          :class="{ active: form.days === d }"
          @click="form.days = d"
        >
          {{ d }}일
        </button>
      </div>
    </section>

    <!-- STEP 2: 여행 스타일 -->
    <section class="stepCard">
      <div class="stepTop">
        <span class="stepBadge">STEP 2</span>
        <h2>여행스타일은 어떤 쪽에 가까운가요?</h2>
        <p class="hint">자연/도시 선호도를 선택해주세요.</p>
      </div>

      <div class="pillRow">
        <button
          v-for="s in styleOptions"
          :key="s"
          type="button"
          class="pill"
          :class="{ active: form.style === s }"
          @click="form.style = s"
        >
          {{ s }}
        </button>
      </div>
    </section>

    <!-- STEP 3: 여행 동기(목적) themes (멀티 선택) -->
    <section class="stepCard">
      <div class="stepTop">
        <span class="stepBadge">STEP 3</span>
        <h2>여행동기는 무엇인가요?</h2>
        <p class="hint">최대 3개까지 선택 가능해요.</p>
      </div>

      <div class="pillRow">
        <button
          v-for="t in themeOptions"
          :key="t"
          type="button"
          class="pill"
          :class="{ active: form.themes.includes(t) }"
          @click="toggleTheme(t)"
        >
          {{ t }}
        </button>
      </div>

      <p v-if="themeError" class="warn">{{ themeError }}</p>
    </section>

    <!-- STEP 4: 동반 현황 companion_type -->
    <section class="stepCard">
      <div class="stepTop">
        <span class="stepBadge">STEP 4</span>
        <h2>동반현황은 어떻게 되나요?</h2>
        <p class="hint">누구와 떠나는지 선택해주세요.</p>
      </div>

      <div class="pillRow">
        <button
          v-for="c in companionTypeOptions"
          :key="c"
          type="button"
          class="pill"
          :class="{ active: form.companion_type === c }"
          @click="setCompanionType(c)"
        >
          {{ c }}
        </button>
      </div>
    </section>

    <!-- STEP 5: 동반자 수 companion_cnt -->
    <section class="stepCard">
      <div class="stepTop">
        <span class="stepBadge">STEP 5</span>
        <h2>여행동반자수는 몇 명인가요?</h2>
        <p class="hint">본인 포함이 아니라 “동반자 수”로 입력(0~16)해주세요.</p>
      </div>

      <div class="counterRow">
        <button type="button" class="miniBtn" @click="decCnt" :disabled="form.companion_cnt <= 0">
          −
        </button>

        <input
          class="numInput"
          type="number"
          min="0"
          max="16"
          v-model.number="form.companion_cnt"
        />

        <button type="button" class="miniBtn" @click="incCnt" :disabled="form.companion_cnt >= 16">
          +
        </button>
      </div>

      <p v-if="cntError" class="warn">{{ cntError }}</p>
    </section>

    <!-- CTA 버튼 (SVG 하단 큰 버튼 느낌) -->
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
 * 이 컴포넌트의 역할(프론트 최소 이해 세트 기준)
 * 1) 사용자 입력 이벤트(버튼 클릭/토글/숫자 입력)를 받아서 form 상태에 저장
 * 2) "AI에게 제주 일정 만들기" 클릭 시
 *    - 백엔드 API를 여기서 호출하지 않고
 *    - 추천 결과 페이지(/routes/recommend/results)로 이동하면서 query로 입력값 전달
 * 3) 결과 페이지에서 query를 읽어 API 호출 → 응답 렌더링
 */

import { reactive, computed, ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

/** ✅ 백엔드 serializer 필드명과 1:1로 맞춘 form */
const form = reactive({
  days: 3,                 // 총 여행 일자 (1~8)
  companion_type: '',      // 동반현황(ChoiceField)
  companion_cnt: 0,        // 동반자 수(0~16)
  themes: [],              // 여행동기(멀티)
  style: '',               // 여행스타일(ChoiceField)
})

/** 옵션들(서버 choices와 동일 텍스트로 맞추는 게 핵심!) */
const daysOptions = [1,2,3,4,5,6,7,8]

const companionTypeOptions = [
  "나홀로 여행",
  "2인 여행(가족 외)",
  "3인 이상 여행(가족 외)",
  "2인 가족 여행",
  "자녀 동반 여행",
  "부모 동반 여행",
  "3대 동반 여행(친척 포함)",
]

const themeOptions = [
  "일상탈출", "힐링", "관계증진", "자아성찰", "자랑/SNS",
  "건강/액티비티", "새로움/경험", "문화/교육", "행사", "기타",
]

const styleOptions = [
  "자연 매우 선호",
  "자연 중간 선호",
  "자연 약간 선호",
  "중립",
  "도시 약간 선호",
  "도시 중간 선호",
  "도시 매우 선호",
]

/** 경고/에러 메시지 상태 */
const themeError = ref('')
const cntError = ref('')
const submitError = ref('')

/** 여행동기 토글(최대 3개 제한) */
function toggleTheme(t) {
  submitError.value = ''
  themeError.value = ''

  const idx = form.themes.indexOf(t)
  if (idx >= 0) {
    form.themes.splice(idx, 1)
    return
  }

  if (form.themes.length >= 3) {
    themeError.value = '여행동기는 최대 3개까지 선택할 수 있어요.'
    return
  }

  form.themes.push(t)
}

/** 동반현황 선택 시, 동반자 수를 “추천값”으로 살짝 보정(원하면 지워도 됨) */
function setCompanionType(c) {
  submitError.value = ''
  form.companion_type = c

  // 너무 강제는 아니고, 초깃값 편의만 제공
  if (c === "나홀로 여행") form.companion_cnt = 0
  else if (c.includes("2인")) form.companion_cnt = 1
  else if (c.includes("3인 이상") || c.includes("3대")) form.companion_cnt = Math.max(form.companion_cnt, 2)
}

/** 동반자 수 +/- */
function decCnt() {
  submitError.value = ''
  form.companion_cnt = Math.max(0, (form.companion_cnt || 0) - 1)
}
function incCnt() {
  submitError.value = ''
  form.companion_cnt = Math.min(16, (form.companion_cnt || 0) + 1)
}

/** 제출 가능 조건(서버 필수값 기준) */
const canSubmit = computed(() => {
  return (
    Number.isFinite(form.days) &&
    form.days >= 1 &&
    form.days <= 8 &&
    !!form.companion_type &&
    !!form.style &&
    Number.isFinite(form.companion_cnt) &&
    form.companion_cnt >= 0 &&
    form.companion_cnt <= 16
  )
})

/**
 * ✅ 요청→처리→응답 흐름
 * - 요청: 버튼 클릭(goRecommend)
 * - 처리: 입력 검증 + router.push로 결과 페이지에 query 전달
 * - 응답: 결과 페이지가 query로 API 호출해 추천 결과 렌더링
 */
function goRecommend() {
  cntError.value = ''
  submitError.value = ''

  // 추가 검증(메시지 친절하게)
  if (!canSubmit.value) {
    submitError.value = '필수 항목(여행일수/여행스타일/동반현황/동반자수)을 확인해주세요.'
    return
  }

  // query는 새로고침에도 살아남아서 추천 결과 페이지에 유리함
  router.push({
    name: 'route-recommend-results',
    query: {
      days: String(form.days),
      companion_type: form.companion_type,
      companion_cnt: String(form.companion_cnt),
      style: form.style,
      // themes는 쉼표로 join해서 전달(결과 페이지에서 split)
      themes: form.themes.join(','),
    },
  })
}
</script>

<style scoped>
/* SVG 느낌: 배경 연한 회색 + 카드 둥글게 */
.page {
  max-width: 900px;
  margin: 0 auto;
  padding: 34px 18px 60px;
  background: #f7f9ff;
  min-height: 100vh;
}

.hero {
  margin: 10px 0 18px;
}
.hero h1 {
  margin: 0 0 8px;
  font-size: 30px;
  letter-spacing: -0.3px;
}
.sub {
  margin: 0;
  color: #6b7a9a;
  font-size: 14px;
}

.stepCard {
  background: #fff;
  border: 1px solid #e9efff;
  border-radius: 16px;
  padding: 18px;
  margin-top: 14px;
}

.stepTop { margin-bottom: 12px; }
.stepBadge {
  display: inline-block;
  font-size: 12px;
  color: #6b7a9a;
  margin-bottom: 8px;
}
.stepTop h2 {
  margin: 0 0 6px;
  font-size: 18px;
}
.hint {
  margin: 0;
  font-size: 13px;
  color: #7d8aa7;
}

.pillRow {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.pill {
  border: 1px solid #cfe0ff;
  background: #fff;
  color: #2a4b8d;
  padding: 10px 14px;
  border-radius: 999px;
  cursor: pointer;
  font-size: 13px;
}
.pill.active {
  border-color: #2a4b8d;
  font-weight: 700;
}

.counterRow {
  display: flex;
  align-items: center;
  gap: 10px;
}

.miniBtn {
  width: 42px;
  height: 42px;
  border-radius: 12px;
  border: 1px solid #dbe6ff;
  background: #fff;
  cursor: pointer;
  font-size: 18px;
}
.miniBtn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.numInput {
  width: 120px;
  height: 42px;
  border-radius: 12px;
  border: 1px solid #dbe6ff;
  padding: 0 12px;
  font-size: 14px;
}

.ctaWrap {
  margin-top: 22px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  align-items: center;
}
.cta {
  width: 100%;
  max-width: 860px;
  padding: 16px 18px;
  border-radius: 14px;
  border: none;
  background: #79aafc;
  color: #fff;
  font-size: 15px;
  cursor: pointer;
}
.cta:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.warn {
  margin: 10px 0 0;
  color: #dc2626;
  font-size: 12px;
}
.center { text-align: center; }
</style>
