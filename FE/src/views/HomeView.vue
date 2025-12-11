<template>
  <div class="home">
    <h2>JejuDoldam 메인 페이지 (뼈대)</h2>

    <p v-if="isLoggedIn">
      로그인 상태입니다. 마이페이지나 다른 기능으로 이동할 수 있게 만들 예정입니다.
    </p>
    <p v-else>
      아직 로그인하지 않았어요. 상단 로그인 버튼을 눌러 로그인해 주세요.
    </p>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const isLoggedIn = computed(() => {
  return !!localStorage.getItem('access')
})
</script>

<style scoped>
.home {
  max-width: 800px;
  margin: 0 auto;
}
</style>
