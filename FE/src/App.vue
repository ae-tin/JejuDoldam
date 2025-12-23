<template>
  <div class="app-container">
    <NavVar />
    
    <main>
      <RouterView />
    </main>
  </div>
</template>

<script setup>
// 말씀하신 경로에 맞춰 컴포넌트를 가져옵니다.
// (파일명이 Navbar.vue가 아니라 NavVar.vue라고 가정했습니다)
import NavVar from '@/components/NavVar.vue';
</script>

<style>
/* [중요] 전역 스타일 초기화 (Reset CSS) 
  브라우저 기본 여백을 없애야 화면이 꽉 차고, 
  로그인 박스가 정확히 가운데로 옵니다.
*/
html, body {
  margin: 0;
  padding: 0;
  width: 100%;
  height: 100%;
}

#app {
  /* Vue CLI 기본 스타일인 text-align: center; margin-top: 60px; 등을 제거해야 합니다. */
  font-family: -apple-system, BlinkMacSystemFont, "Pretendard", Roboto, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  
  /* 전체 높이 확보 */
  min-height: 100vh;
}

/* 모든 요소에 box-sizing 적용 
  (패딩을 줘도 박스 크기가 커지지 않게 함)
*/
*, *::before, *::after {
  box-sizing: border-box;
}

/* 링크 기본 스타일 제거 (밑줄 등) */
a {
  text-decoration: none;
  color: inherit;
}
</style>