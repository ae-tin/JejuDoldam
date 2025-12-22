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

        <section v-if="post.route" class="route-detail">
          <div class="route-head">
            <div>
              <p class="route-label">선택된 루트</p>
              <h3 class="route-title">{{ routeDetail?.title ?? post.route.title }}</h3>
              <p class="route-desc" v-if="routeDetail?.description">{{ routeDetail.description }}</p>
            </div>

            <RouterLink :to="{ name: 'route-detail', params: { routeId: post.route.id } }" class="route-link">
              루트 상세 페이지로 이동
            </RouterLink>
          </div>

          <div class="route-card">
            <p v-if="routeLoading">루트를 불러오는 중...</p>
            <p v-else-if="routeError" class="error">{{ routeError }}</p>

            <div v-else-if="routeDetail" class="route-layout">
              <div class="day-tabs">
                <button
                  v-for="d in sortedDays"
                  :key="d.id"
                  class="day-tab"
                  :class="{ active: d.id === selectedDayId }"
                  type="button"
                  @click="selectedDayId = d.id"
                >
                  DAY {{ d.day }}
                </button>
              </div>

              <div class="route-body">
                <div class="places">
                  <div class="day-header" v-if="selectedDay">
                    <div class="day-title">
                      <b>DAY {{ selectedDay.day }}</b>
                      <span class="muted">({{ dayPlaces.length }}곳)</span>
                    </div>
                  </div>

                  <ul v-if="selectedDay && dayPlaces.length" class="place-list">
                    <li v-for="(p, idx) in dayPlaces" :key="p.id" class="place">
                      <div class="place-main">
                        <span class="badge">{{ idx + 1 }}</span>
                        <div>
                          <div class="place-name">{{ p.name }}</div>
                          <div class="place-addr">{{ p.address || '주소 없음' }}</div>
                          <div class="place-memo" v-if="p.memo">메모: {{ p.memo }}</div>
                        </div>
                      </div>
                    </li>
                  </ul>

                  <p v-else class="muted">해당 DAY에 장소가 없습니다.</p>
                </div>

                <div class="map-panel" v-if="selectedDay">
                  <KakaoMap :places="dayPlaces" />
                </div>
              </div>
            </div>

            <p v-else class="muted">루트 정보를 불러오지 못했습니다.</p>
          </div>
        </section>

        <div class="meta">
          <span>좋아요 {{ post.like_count }}</span>
          <span>댓글 {{ post.writed_comments?.length ?? 0 }}</span>
        </div>

        <div class="actions">
          <button type="button" class="heart-btn" @click="toggleLike" :disabled="likeBusy">
            <span class="sr-only">좋아요</span>
            <span v-if="post.is_liked" class="heart filled">❤</span>
            <span v-else class="heart empty">♡</span>
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
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import api from '@/api/client'
import KakaoMap from '@/components/KakaoMap.vue'

const route = useRoute()

const post = ref(null)
const loading = ref(false)
const error = ref('')
const likeBusy = ref(false)
const commentInput = ref('')
const commentBusy = ref(false)
const routeDetail = ref(null)
const routeLoading = ref(false)
const routeError = ref('')
const selectedDayId = ref(null)

const formatDate = (iso) => {
  if (!iso) return '-'
  try { return new Date(iso).toLocaleString() } catch { return iso }
}

const sortedDays = computed(() => {
  const days = routeDetail.value?.days || []
  return [...days].sort((a, b) => a.day - b.day)
})

const selectedDay = computed(() => {
  if (!routeDetail.value) return null
  return (routeDetail.value.days || []).find(d => d.id === selectedDayId.value) || null
})

const dayPlaces = computed(() => {
  const d = selectedDay.value
  if (!d) return []
  const places = d.places || []
  return [...places].sort((a, b) => (a.order ?? 0) - (b.order ?? 0))
})

const fetchPost = async () => {
  loading.value = true
  error.value = ''
  try {
    const { data } = await api.get(`/posts/${route.params.postId}/`)
    post.value = data

    if (data.route?.id) {
      await fetchRouteDetail(data.route.id)
    } else {
      routeDetail.value = null
      selectedDayId.value = null
    }
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

const fetchRouteDetail = async (routeId) => {
  routeLoading.value = true
  routeError.value = ''
  try {
    const { data } = await api.get(`/routes/${routeId}/`)
    routeDetail.value = data

    const first = [...(data.days || [])].sort((a, b) => a.day - b.day)[0]
    selectedDayId.value = first?.id ?? null
  } catch (e) {
    console.error(e)
    routeError.value = '루트 정보를 불러오지 못했습니다.'
  } finally {
    routeLoading.value = false
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
.route-detail { border: 1px solid #e5e7eb; border-radius: 12px; padding: 14px; background: #f9fafb; }
.route-head { display: flex; align-items: center; justify-content: space-between; gap: 12px; flex-wrap: wrap; }
.route-label { font-size: 12px; color: #6b7280; margin: 0; }
.route-title { margin: 2px 0; }
.route-desc { margin: 0; color: #4b5563; }
.route-link { color: #2563eb; text-decoration: none; font-size: 14px; }
.route-card { margin-top: 10px; border: 1px solid #e5e7eb; border-radius: 10px; background: #fff; padding: 12px; }
.route-layout { display: flex; flex-direction: column; gap: 12px; }
.day-tabs { display: flex; gap: 8px; flex-wrap: wrap; }
.day-tab { padding: 8px 10px; border: 1px solid #d1d5db; border-radius: 999px; background: #fff; cursor: pointer; font-size: 13px; }
.day-tab.active { border-color: #111827; font-weight: 700; }
.route-body { display: grid; gap: 12px; grid-template-columns: 1fr; }
.places { border: 1px solid #f3f4f6; border-radius: 10px; padding: 10px; background: #f9fafb; }
.day-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px; }
.day-title { display: flex; align-items: baseline; gap: 8px; }
.muted { color: #6b7280; font-size: 13px; }
.place-list { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 10px; }
.place { border: 1px solid #e5e7eb; border-radius: 8px; padding: 10px; background: #fff; }
.place-main { display: flex; gap: 10px; align-items: flex-start; }
.badge { display: inline-flex; align-items: center; justify-content: center; width: 26px; height: 26px; border-radius: 50%; background: #111827; color: #fff; font-weight: 700; }
.place-name { font-weight: 700; }
.place-addr { color: #4b5563; font-size: 13px; margin-top: 2px; }
.place-memo { color: #6b7280; font-size: 13px; margin-top: 4px; }
.map-panel { border: 1px solid #e5e7eb; border-radius: 10px; overflow: hidden; min-height: 280px; }
.heart-btn { width: 42px; height: 42px; border-radius: 50%; border: 1px solid #d1d5db; background: #fff; display: inline-flex; align-items: center; justify-content: center; font-size: 20px; cursor: pointer; transition: transform 0.15s ease, box-shadow 0.15s ease; }
.heart-btn:hover { transform: translateY(-1px); box-shadow: 0 6px 12px rgba(0,0,0,0.08); }
.heart { font-size: 22px; line-height: 1; }
.heart.filled { color: #ef4444; }
.heart.empty { color: #9ca3af; }
.sr-only { position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px; overflow: hidden; clip: rect(0, 0, 0, 0); white-space: nowrap; border: 0; }

@media (min-width: 900px) {
  .route-body { grid-template-columns: 1.1fr 1fr; align-items: stretch; }
  .map-panel { min-height: 360px; }
}
</style>
