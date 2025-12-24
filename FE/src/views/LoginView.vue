<template>
  <div class="login-container">
    <div class="login-card fade-in">
      <div class="text-center mb-6">
        <h1 class="logo-text" @click="router.push('/')">JejuDoldam</h1>
        <h2 class="welcome-text">다시 만나서 반가워요! 👋</h2>
        <p class="sub-text">나만의 여행 계획을 확인해보세요.</p>
      </div>

      <form @submit.prevent="handleSubmit">
        <div class="input-group">
          <label for="username">아이디</label>
          <input
            id="username"
            v-model="username"
            type="text"
            placeholder="아이디를 입력하세요"
            autocomplete="username"
            :class="{ 'error-input': error }"
          />
        </div>

        <div class="input-group">
          <label for="password">비밀번호</label>
          <input
            id="password"
            v-model="password"
            type="password"
            placeholder="비밀번호를 입력하세요"
            autocomplete="current-password"
            :class="{ 'error-input': error }"
          />
        </div>

        <p v-if="error" class="error-msg">
          ⚠️ {{ error }}
        </p>

        <button type="submit" class="submit-btn" :disabled="loading">
          <span v-if="loading" class="spinner"></span>
          {{ loading ? '로그인 중...' : '로그인' }}
        </button>
      </form>

      <div class="kakao-btn" @click="kakaoLogin">
        <span class="kakao-symbol">💬</span>
        <span>카카오 로그인</span>
      </div>

      <div class="footer-links">
        <p>
          아직 계정이 없으신가요?
          <RouterLink to="/signup" class="link">회원가입</RouterLink>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import api from '@/api/client';
import { useAuthStore } from '@/stores/auth';

const router = useRouter();
const route = useRoute();
const auth = useAuthStore();

const username = ref('');
const password = ref('');
const loading = ref(false);
const error = ref('');

// [추가됨] 카카오 로그인 로직
const kakaoLogin = async () => {
  try {
    // 1. 백엔드에 "카카오 로그인 URL 좀 줘" 라고 요청
    // (URL 경로는 백엔드 urls.py 설정에 맞춰 수정하세요. 예: /auth/kakao/login-url/)
    const response = await api.get('/auth/kakao/url/');
    
    // 2. 받아온 카카오 인증 URL로 브라우저 이동
    if (response.data.url) {
      window.location.href = response.data.url;
    }
  } catch (err) {
    console.error('카카오 로그인 URL 로드 실패:', err);
    alert('카카오 로그인 서버에 연결할 수 없습니다.');
  }
};

const handleSubmit = async () => {
  error.value = '';
  loading.value = true;

  try {
    // 1) JWT 로그인 요청
    const { data } = await api.post('/auth/jwt/login/', {
      username: username.value,
      password: password.value,
    });

    // 2) Pinia에 토큰 저장
    auth.login(data.access, data.refresh);

    // 3) 페이지 이동
    const nextPath = route.query.next;
    if (typeof nextPath === 'string') {
      router.push(nextPath);
    } else {
      router.push({ name: 'home' });
    }

  } catch (err) {
    console.error(err);
    if (err.response && err.response.status === 401) {
      error.value = '아이디 또는 비밀번호가 일치하지 않습니다.';
    } else {
      error.value = '로그인 중 문제가 발생했습니다.';
    }
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
/* 기존 스타일 그대로 유지 */
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f5f7fa; 
  padding: 20px;
}

.login-card {
  width: 100%;
  max-width: 420px;
  background: white;
  padding: 40px;
  border-radius: 16px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.05);
  border: 1px solid rgba(0, 0, 0, 0.02);
}

.text-center { text-align: center; }
.mb-6 { margin-bottom: 24px; }

.logo-text {
  font-size: 1.5rem;
  font-weight: 800;
  color: #2cb398;
  margin-bottom: 10px;
  cursor: pointer;
  display: inline-block;
}

.welcome-text {
  font-size: 1.6rem;
  font-weight: 700;
  color: #333;
  margin: 0 0 8px 0;
}

.sub-text {
  color: #888;
  font-size: 0.95rem;
}

.input-group {
  margin-bottom: 20px;
  text-align: left;
}

.input-group label {
  display: block;
  font-size: 0.9rem;
  font-weight: 600;
  color: #555;
  margin-bottom: 8px;
}

.input-group input {
  width: 100%;
  padding: 12px 16px;
  font-size: 1rem;
  border: 1px solid #ddd;
  border-radius: 8px;
  background-color: #fafafa;
  transition: all 0.2s ease;
  box-sizing: border-box;
}

.input-group input:focus {
  border-color: #2cb398;
  background-color: #fff;
  outline: none;
  box-shadow: 0 0 0 3px rgba(44, 179, 152, 0.1);
}

.input-group input.error-input {
  border-color: #e74c3c;
  background-color: #fff5f5;
}

.submit-btn {
  width: 100%;
  padding: 14px;
  font-size: 1.1rem;
  font-weight: bold;
  color: white;
  background-color: #2cb398;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.2s, transform 0.1s;
  margin-top: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.submit-btn:hover {
  background-color: #249e85;
}

.submit-btn:active {
  transform: scale(0.98);
}

.submit-btn:disabled {
  background-color: #a8d5cc;
  cursor: not-allowed;
}

.error-msg {
  color: #e74c3c;
  font-size: 0.9rem;
  margin-bottom: 16px;
  text-align: center;
  background-color: #fff5f5;
  padding: 8px;
  border-radius: 6px;
}

.footer-links {
  margin-top: 24px;
  text-align: center;
  font-size: 0.95rem;
  color: #666;
}

.link {
  color: #2cb398;
  font-weight: 600;
  text-decoration: none;
  margin-left: 5px;
}

.link:hover {
  text-decoration: underline;
}

.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid #ffffff;
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.fade-in {
  animation: fadeInUp 0.5s ease-out;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* [추가됨] 카카오 로그인 버튼 스타일 */
.kakao-btn {
  width: 100%;
  padding: 14px;
  margin-top: 12px; /* 일반 로그인 버튼과의 간격 */
  font-size: 1.1rem;
  font-weight: bold;
  color: #381e1f; /* 카카오 글자색 (짙은 갈색) */
  background-color: #fee500; /* 카카오 공식 노란색 */
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: background-color 0.2s, transform 0.1s;
  box-sizing: border-box;
}

.kakao-btn:hover {
  background-color: #fada0a; /* 호버 시 약간 진해짐 */
}

.kakao-btn:active {
  transform: scale(0.98);
}

.kakao-symbol {
  font-size: 1.2rem;
}

@media (max-width: 480px) {
  .login-card {
    padding: 30px 20px;
    box-shadow: none;
    background: transparent;
  }
  .login-container {
    background: white;
    align-items: flex-start;
    padding-top: 60px;
  }
  .input-group input {
    font-size: 16px;
  }
}
</style>