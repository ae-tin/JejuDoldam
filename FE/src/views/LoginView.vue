<template>
  <div class="login">
    <h2>로그인</h2>

    <form @submit.prevent="handleSubmit">
      <div class="field">
        <label for="username">아이디</label>
        <input
          id="username"
          v-model="username"
          type="text"
          autocomplete="username"
        />
      </div>

      <div class="field">
        <label for="password">비밀번호</label>
        <input
          id="password"
          v-model="password"
          type="password"
          autocomplete="current-password"
        />
      </div>

      <button type="submit" :disabled="loading">
        {{ loading ? '로그인 중...' : '로그인' }}
      </button>

      <p v-if="error" class="error">{{ error }}</p>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import api from '@/api/client';

const router = useRouter();

const username = ref('');
const password = ref('');
const loading = ref(false);
const error = ref('');

const handleSubmit = async () => {
  error.value = '';
  loading.value = true;

  try {
    // 1) JWT 로그인 요청
    const { data } = await api.post('/auth/jwt/login/', {
      username: username.value,
      password: password.value,
    });

    // access / refresh 토큰 저장
    // TODO: 로컬 스토리지에 저장된 토큰을 httponly 저장 구조로 설계
    localStorage.setItem('access', data.access);
    localStorage.setItem('refresh', data.refresh);


    alert(`로그인 성공! 안녕, ${username.value}`);

    // TODO: 나중에 루트 목록 페이지 만들면 여기로 이동
    // router.push('/routes');
  } catch (err) {
    console.error(err);
    error.value = '아이디 또는 비밀번호를 다시 확인해주세요.';
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.login {
  max-width: 400px;
  margin: 80px auto;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-bottom: 12px;
}

input {
  padding: 8px 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

button {
  margin-top: 8px;
  padding: 8px 12px;
  border-radius: 4px;
  border: none;
  cursor: pointer;
}

.error {
  margin-top: 8px;
  color: red;
}
</style>
