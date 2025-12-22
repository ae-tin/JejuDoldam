<!-- src/views/CommunityPostListView.vue -->
<template>
  <div class="page">
    <div class="page-head">
      <div>
        <h1>커뮤니티</h1>
        <p class="sub">다른 여행자들의 경험을 둘러보고 공유해보세요.</p>
      </div>
      <RouterLink to="/community/new" class="btn primary">글 작성</RouterLink>
    </div>

    <div class="card">
      <p v-if="loading">불러오는 중...</p>
      <p v-else-if="error" class="error">{{ error }}</p>

      <ul v-else-if="posts.length" class="post-list">
        <li
          v-for="post in posts"
          :key="post.id"
          class="post-item"
          @click="goDetail(post.id)"
        >
          <div class="title">{{ post.title }}</div>
          <div class="content-preview">{{ post.content }}</div>
          <div class="meta">
            <span>{{ formatDate(post.created_at) }}</span>
            <span>댓글 {{ post.comment_count }}</span>
            <span>좋아요 {{ post.like_count }}</span>
            <span v-if="post.route">연결된 루트: {{ post.route.title }}</span>
          </div>
        </li>
      </ul>

      <p v-else>아직 작성된 게시글이 없습니다. 첫 글을 남겨보세요!</p>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/api/client'

const router = useRouter()
const posts = ref([])
const loading = ref(false)
const error = ref('')

const formatDate = (iso) => {
  if (!iso) return '-'
  try { return new Date(iso).toLocaleString() } catch { return iso }
}

const goDetail = (postId) => {
  router.push({ name: 'community-detail', params: { postId } })
}

const fetchPosts = async () => {
  loading.value = true
  error.value = ''
  try {
    const { data } = await api.get('/posts/')
    posts.value = data
  } catch (e) {
    console.error(e)
    error.value = '게시글 목록을 불러오지 못했습니다.'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchPosts()
})
</script>

<style scoped>
.page { max-width: 960px; margin: 0 auto; }
.page-head { display: flex; justify-content: space-between; align-items: center; gap: 12px; margin-bottom: 12px; flex-wrap: wrap; }
.sub { color: #6b7280; margin-top: 4px; }
.card { border: 1px solid #e5e7eb; border-radius: 12px; padding: 16px; background: #fff; }
.btn { border: 1px solid #d1d5db; padding: 8px 12px; border-radius: 10px; text-decoration: none; color: inherit; display: inline-block; }
.btn.primary { background: #111827; color: #fff; border-color: #111827; }
.error { color: #dc2626; }
.post-list { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 12px; }
.post-item { border: 1px solid #f3f4f6; border-radius: 10px; padding: 12px; cursor: pointer; transition: border-color 0.2s, box-shadow 0.2s; }
.post-item:hover { border-color: #d1d5db; box-shadow: 0 6px 12px rgba(0,0,0,0.04); }
.title { font-weight: 700; margin-bottom: 6px; }
.content-preview { color: #4b5563; margin-bottom: 8px; white-space: pre-line; }
.meta { display: flex; flex-wrap: wrap; gap: 10px; color: #6b7280; font-size: 13px; }
</style>
