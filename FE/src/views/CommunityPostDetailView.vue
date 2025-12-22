<!-- src/views/community/CommunityPostDetailView.vue -->
<template>
  <div class="page">
    <div class="page-head">
      <div>
        <h1>{{ post?.title ?? '게시글 상세' }}</h1>
        <p class="sub" v-if="post">{{ formatDate(post.created_at) }}</p>
      </div>
      <RouterLink to="/community" class="btn">목록으로</RouterLink>
    </div>

    <div class="card">
      <p v-if="loading">불러오는 중...</p>
      <p v-else-if="error" class="error">{{ error }}</p>

      <div v-else-if="post" class="post-body">
        <div class="content">{{ post.content }}</div>

        <div class="route" v-if="post.route">
          연결된 루트: <RouterLink :to="{ name: 'route-detail', params: { routeId: post.route.id } }">{{ post.route.title }}</RouterLink>
        </div>

        <div class="meta">
          <span>좋아요 {{ post.like_count }}</span>
          <span>댓글 {{ post.writed_comments?.length ?? 0 }}</span>
        </div>

        <div class="actions">
          <button type="button" class="btn primary" @click="toggleLike" :disabled="likeBusy">
            {{ post.is_liked ? '좋아요 취소' : '좋아요' }}
          </button>
        </div>

        <section class="comments">
          <h3>댓글</h3>
          <ul v-if="post.writed_comments?.length" class="comment-list">
            <li v-for="c in post.writed_comments" :key="c.id" class="comment">
              <div class="c-head">
                <span class="author">작성자 #{{ c.user }}</span>
                <span class="time">{{ formatDate(c.created_at) }}</span>
              </div>
              <div class="c-body">{{ c.content }}</div>
            </li>
          </ul>
          <p v-else>첫 댓글을 남겨보세요.</p>

          <form class="comment-form" @submit.prevent="submitComment">
            <textarea
              v-model="commentInput"
              rows="3"
              placeholder="댓글을 입력하세요"
            ></textarea>
            <button type="submit" class="btn primary" :disabled="commentBusy || !commentInput.trim()">
              {{ commentBusy ? '등록 중...' : '댓글 등록' }}
            </button>
          </form>
        </section>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import api from '@/api/client'

const route = useRoute()

const post = ref(null)
const loading = ref(false)
const error = ref('')
const likeBusy = ref(false)
const commentInput = ref('')
const commentBusy = ref(false)

const formatDate = (iso) => {
  if (!iso) return '-'
  try { return new Date(iso).toLocaleString() } catch { return iso }
}

const fetchPost = async () => {
  loading.value = true
  error.value = ''
  try {
    const { data } = await api.get(`/posts/${route.params.postId}/`)
    post.value = data
  } catch (e) {
    console.error(e)
    error.value = '게시글을 불러오지 못했습니다.'
  } finally {
    loading.value = false
  }
}

const toggleLike = async () => {
  if (!post.value) return
  likeBusy.value = true
  try {
    const { data } = await api.post(`/posts/${post.value.id}/like/`)
    post.value = data.post
  } catch (e) {
    console.error(e)
    alert('좋아요 처리 중 오류가 발생했습니다.')
  } finally {
    likeBusy.value = false
  }
}

const submitComment = async () => {
  if (!commentInput.value.trim()) return
  commentBusy.value = true
  try {
    const { data } = await api.post(`/posts/${route.params.postId}/comment/`, { content: commentInput.value })
    post.value = {
      ...post.value,
      writed_comments: [...(post.value?.writed_comments ?? []), data],
    }
    commentInput.value = ''
  } catch (e) {
    console.error(e)
    alert('댓글 등록에 실패했습니다.')
  } finally {
    commentBusy.value = false
  }
}

onMounted(fetchPost)

watch(() => route.params.postId, fetchPost)
</script>

<style scoped>
.page { max-width: 960px; margin: 0 auto; }
.page-head { display: flex; justify-content: space-between; align-items: center; gap: 12px; margin-bottom: 12px; flex-wrap: wrap; }
.sub { color: #6b7280; margin-top: 4px; }
.card { border: 1px solid #e5e7eb; border-radius: 12px; padding: 16px; background: #fff; }
.error { color: #dc2626; }
.post-body { display: flex; flex-direction: column; gap: 12px; }
.content { white-space: pre-line; line-height: 1.6; }
.route { color: #2563eb; font-size: 14px; }
.meta { display: flex; gap: 14px; color: #6b7280; font-size: 13px; }
.actions { display: flex; gap: 8px; }
.btn { border: 1px solid #d1d5db; padding: 8px 12px; border-radius: 10px; background: #fff; cursor: pointer; }
.btn.primary { background: #111827; color: #fff; border-color: #111827; }
.comments { margin-top: 12px; }
.comment-list { list-style: none; padding: 0; margin: 10px 0 0; display: flex; flex-direction: column; gap: 10px; }
.comment { border: 1px solid #f3f4f6; border-radius: 10px; padding: 10px; }
.c-head { display: flex; justify-content: space-between; color: #6b7280; font-size: 13px; }
.c-body { margin-top: 6px; white-space: pre-line; }
.comment-form { display: flex; flex-direction: column; gap: 8px; margin-top: 12px; }
textarea { width: 100%; padding: 10px; border: 1px solid #d1d5db; border-radius: 8px; resize: vertical; }
</style>
