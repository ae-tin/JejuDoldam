<!-- src/views/community/CommunityPostCreateView.vue -->
<template>
  <div class="page">
    <div class="page-head">
      <div>
        <h1>글 작성</h1>
        <p class="sub">여행 경험을 공유하고 다른 여행자들에게 영감을 주세요.</p>
      </div>
      <RouterLink to="/community" class="btn">목록으로</RouterLink>
    </div>

    <div class="card">
      <form class="form" @submit.prevent="handleSubmit">
        <div class="field">
          <label for="title">제목</label>
          <input id="title" v-model="form.title" type="text" required placeholder="제목을 입력하세요" />
        </div>

        <div class="field">
          <label for="content">내용</label>
          <textarea
            id="content"
            v-model="form.content"
            rows="8"
            required
            placeholder="여행 후기를 자유롭게 작성하세요"
          ></textarea>
        </div>

        <div class="field">
          <label for="route">연결할 루트(선택)</label>
          <select id="route" v-model="form.route">
            <option :value="null">선택 안 함</option>
            <option v-for="r in routes" :key="r.id" :value="r.id">{{ r.title }}</option>
          </select>
        </div>

        <div class="actions">
          <button type="submit" class="btn primary" :disabled="loading">
            {{ loading ? '작성 중...' : '등록하기' }}
          </button>
        </div>

        <p v-if="error" class="error">{{ error }}</p>
      </form>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/api/client'

const router = useRouter()

const form = ref({
  title: '',
  content: '',
  route: null,
})

const routes = ref([])
const loading = ref(false)
const error = ref('')

const loadRoutes = async () => {
  try {
    const { data } = await api.get('/routes/')
    routes.value = data
  } catch (e) {
    console.error(e)
  }
}

const handleSubmit = async () => {
  if (!form.value.title.trim() || !form.value.content.trim()) return
  loading.value = true
  error.value = ''
  try {
    const payload = {
      title: form.value.title,
      content: form.value.content,
      // route 필드는 null을 보낼 수 있으므로 명시적으로 포함
      route: form.value.route,
    }
    await api.post('/posts/create/', payload)
    alert('게시글이 등록되었습니다.')
    router.push({ name: 'community-list' })
  } catch (e) {
    console.error(e)
    error.value = '게시글 등록에 실패했습니다.'
  } finally {
    loading.value = false
  }
}

onMounted(loadRoutes)
</script>

<style scoped>
.page { max-width: 800px; margin: 0 auto; }
.page-head { display: flex; justify-content: space-between; align-items: center; gap: 12px; margin-bottom: 12px; flex-wrap: wrap; }
.sub { color: #6b7280; margin-top: 4px; }
.card { border: 1px solid #e5e7eb; border-radius: 12px; padding: 16px; background: #fff; }
.form { display: flex; flex-direction: column; gap: 14px; }
.field { display: flex; flex-direction: column; gap: 6px; }
label { font-weight: 600; }
input, textarea, select { border: 1px solid #d1d5db; border-radius: 8px; padding: 10px; font-size: 14px; }
textarea { resize: vertical; }
.actions { display: flex; justify-content: flex-end; }
.btn { border: 1px solid #d1d5db; padding: 8px 12px; border-radius: 10px; background: #fff; cursor: pointer; text-decoration: none; color: inherit; }
.btn.primary { background: #111827; color: #fff; border-color: #111827; }
.error { color: #dc2626; }
</style>
