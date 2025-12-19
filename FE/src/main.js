/**
 * ✅ 프론트 최소 이해 세트(main.js)
 * 1) 앱이 시작될 때 전역 테마 CSS를 불러온다.
 * 2) Pinia와 vue-router를 플러그인으로 등록한다.
 * 3) 최상단 App 컴포넌트를 #app 요소에 마운트한다.
 * 4) 라우터 네비게이션은 App.vue의 헤더가 처리한다.
 */
import { createApp } from 'vue'
import { createPinia } from 'pinia'

import './assets/theme.css'
import App from './App.vue'
import router from './router'

const app = createApp(App)

app.use(createPinia())
app.use(router)

app.mount('#app')
