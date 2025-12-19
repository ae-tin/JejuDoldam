/*
프론트 최소 이해 세트
1) 앱이 시작될 때 createApp 실행 이벤트로 Pinia와 라우터가 등록된다.
2) API 호출은 없지만 전역 테마 CSS를 불러 앱 전체에 시그니처 컬러를 적용한다.
3) 응답/상태는 없고, 라우터 렌더링 결과가 App.vue에 표시된다.
4) 흐름: main.js 로드 → 전역 스타일(theme.css) 적용 → Pinia/라우터 플러그인 주입 → #app에 마운트.
*/
import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'
import './assets/theme.css'

const app = createApp(App)

app.use(createPinia())
app.use(router)

app.mount('#app')
