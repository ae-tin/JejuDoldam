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
  <p style="margin-top:12px;">
    아직 계정이 없나요?
    <RouterLink to="/signup">회원가입</RouterLink>
  </p>
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
    // TODO: 로컬 스토리지에 저장된 토큰을 httponly 저장 구조로 설계(맨 나중에 고려 지금 프로젝트 크기면 굳이 안해도됨)
    // finia에 토큰 저장
    auth.login(data.access, data.refresh)


    alert(`로그인 성공! 안녕, ${username.value}`);

    // 로그인 하기 전에 요청했던 페이지가 있다면 해당 페이지로, 없다면 메인 페이지로 이동
    const nextPath = route.query.next
    if (typeof nextPath === 'string') {
      router.push(nextPath)
    } else {
      router.push({name: 'home'})
    }

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
