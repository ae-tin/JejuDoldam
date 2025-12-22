<!-- src/views/community/CommunityPostDetailView.vue -->
<template>
  <div class="page">
    <div class="page-head">
      <div>
        <p class="eyebrow">커뮤니티</p>
        <h1>{{ post?.title ?? '게시글 상세' }}</h1>
        <p class="sub" v-if="post">{{ formatDate(post.created_at) }}</p>
      </div>
      <RouterLink to="/community" class="btn">목록으로</RouterLink>
    </div>

    <div class="card" v-if="loading">
      불러오는 중...
    </div>
    <div class="card error" v-else-if="error">
      {{ error }}
    </div>

    <template v-else-if="post">
      <section v-if="post.route" class="route-section">
        <div class="map-hero card">
          <div class="map-head">
            <div>
              <p class="route-label">선택된 루트</p>
              <h2 class="route-title">{{ routeDetail?.title ?? post.route.title }}</h2>
              <p class="route-desc" v-if="routeDetail?.description">{{ routeDetail.description }}</p>
            </div>
            <RouterLink :to="{ name: 'route-detail', params: { routeId: post.route.id } }" class="route-link">
              루트 상세보기
            </RouterLink>
          </div>
          <div class="map-shell">
            <KakaoMap :places="dayPlaces" />
          </div>
          <div class="map-meta">
            <div class="pill">총 {{ sortedDays.length }}일</div>
            <div class="pill">{{ totalPlaces }}곳</div>
            <div class="pill" v-if="selectedDay">현재 Day {{ selectedDay.day }}</div>
          </div>
        </div>

        <div class="tabs" v-if="routeDetail">
          <button
            v-for="d in sortedDays"
            :key="d.id"
            type="button"
            class="tab"
            :class="{ active: d.id === selectedDayId }"
            @click="selectedDayId = d.id"
          >
            Day {{ d.day }}
          </button>
        </div>

        <div class="day-card card">
          <p v-if="routeLoading">루트를 불러오는 중...</p>
          <p v-else-if="routeError" class="error">{{ routeError }}</p>

          <template v-else-if="routeDetail && selectedDay">
            <div class="day-head">
              <div>
                <p class="mini-label">Day {{ selectedDay.day }}</p>
                <h3>
                  <template v-if="dayPlaces.length">
                    <template v-if="dayPlaces.length > 1">{{ `${dayPlaces[0].name} 외 ${dayPlaces.length - 1}곳` }}</template>
                    <template v-else>{{ dayPlaces[0].name }}</template>
                  </template>
                  <template v-else>일정이 비어 있어요</template>
                </h3>
                <p class="muted">{{ daySummary }}</p>
              </div>
              <button
                type="button"
                class="add-route"
                :disabled="addBusy || routeLoading || !!routeError"
                @click="addRouteToMine"
              >
                {{ addBusy ? '추가 중...' : '내 경로로 추가하기' }}
              </button>
            </div>

            <ul v-if="dayPlaces.length" class="place-list">
              <li v-for="(p, idx) in dayPlaces" :key="p.id" class="place">
                <div class="place-order">{{ idx + 1 }}</div>
                <div class="place-info">
                  <p class="place-name">{{ p.name }}</p>
                  <p class="place-addr">{{ p.address || '주소 없음' }}</p>
                  <p class="place-memo" v-if="p.memo">{{ p.memo }}</p>
                </div>
              </li>
            </ul>
            <p v-else class="muted">해당 DAY에 장소가 없습니다.</p>
          </template>

          <p v-else class="muted">루트 정보를 불러오지 못했습니다.</p>
        </div>
      </section>

      <section class="card story">
        <div class="story-head">
          <div>
            <p class="mini-label">여행 이야기</p>
            <h3>{{ post.title }}</h3>
          </div>
          <div class="story-stats">
            <span>좋아요 {{ post.like_count }}</span>
            <span>댓글 {{ post.writed_comments?.length ?? 0 }}</span>
          </div>
        </div>
        <div class="content">{{ post.content }}</div>
      </section>

      <section class="card reactions">
        <button type="button" class="heart-btn" @click="toggleLike" :disabled="likeBusy">
          <span class="sr-only">좋아요</span>
          <span v-if="post.is_liked" class="heart filled">❤</span>
          <span v-else class="heart empty">♡</span>
        </button>
        <div class="reaction-counts">
          <span>좋아요 {{ post.like_count }}</span>
          <span>댓글 {{ post.writed_comments?.length ?? 0 }}</span>
        </div>
      </section>

      <section class="card comments">
        <div class="comment-head">
          <h3>댓글</h3>
          <span class="muted">{{ post.writed_comments?.length ?? 0 }}개</span>
        </div>
        <ul v-if="post.writed_comments?.length" class="comment-list">
          <li v-for="c in post.writed_comments" :key="c.id" class="comment">
            <div class="c-head">
              <span class="author">작성자 #{{ c.user }}</span>
              <span class="time">{{ formatDate(c.created_at) }}</span>
            </div>
            <div class="c-body">{{ c.content }}</div>
          </li>
        </ul>
        <p v-else class="muted">첫 댓글을 남겨보세요.</p>

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
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/api/client'
import KakaoMap from '@/components/KakaoMap.vue'

const route = useRoute()
const router = useRouter()

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
const addBusy = ref(false)

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

const totalPlaces = computed(() => {
  const days = routeDetail.value?.days || []
  return days.reduce((sum, d) => sum + (d.places?.length || 0), 0)
})

const daySummary = computed(() => {
  if (!dayPlaces.value.length) return '등록된 장소가 없습니다.'
  const first = dayPlaces.value[0]
  return first.address || '주소 정보가 없습니다.'
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

const addRouteToMine = async () => {
  if (!routeDetail.value) return

  addBusy.value = true
  try {
    const payload = {
      title: routeDetail.value.title,
      description: routeDetail.value.description ?? '',
      days: (routeDetail.value.days || []).map((d) => ({
        day: d.day,
        places: (d.places || [])
          .sort((a, b) => (a.order ?? 0) - (b.order ?? 0))
          .map((p, idx) => ({
            order: p.order ?? idx + 1,
            name: p.name,
            address: p.address ?? '',
            latitude: p.latitude ?? null,
            longitude: p.longitude ?? null,
            memo: p.memo ?? '',
          })),
      })),
    }

    const { data } = await api.post('/routes/confirm/', payload)
    router.push({ name: 'route-detail', params: { routeId: data.id } })
  } catch (e) {
    console.error(e)
    alert('내 경로로 추가하지 못했습니다.')
  } finally {
    addBusy.value = false
  }
}

onMounted(fetchPost)

watch(() => route.params.postId, fetchPost)
</script>

<style scoped>
.page { max-width: 1080px; margin: 0 auto; padding-bottom: 40px; }
.page-head { display: flex; justify-content: space-between; align-items: flex-start; gap: 12px; margin-bottom: 16px; flex-wrap: wrap; }
.eyebrow { color: #7c8aa1; font-size: 13px; margin: 0 0 4px; }
.sub { color: #6b7280; margin-top: 4px; }
.card { border: 1px solid #e5e7eb; border-radius: 16px; padding: 16px; background: #fff; box-shadow: 0 10px 26px rgba(0, 0, 0, 0.04); }
.error { color: #dc2626; }
.btn { border: 1px solid #d1d5db; padding: 10px 14px; border-radius: 10px; background: #fff; cursor: pointer; text-decoration: none; color: inherit; }
.btn.primary { background: #111827; color: #fff; border-color: #111827; }
.route-section { display: flex; flex-direction: column; gap: 14px; }
.map-hero { padding: 18px; background: linear-gradient(180deg, #f8fbff 0%, #fff 70%); border: 1px solid #e5e7eb; }
.map-head { display: flex; justify-content: space-between; align-items: flex-start; gap: 12px; flex-wrap: wrap; margin-bottom: 12px; }
.route-label { color: #6b7280; font-size: 13px; margin: 0 0 4px; }
.route-title { margin: 0 0 4px; }
.route-desc { margin: 0; color: #4b5563; }
.route-link { color: #2563eb; text-decoration: none; font-weight: 700; }
.map-shell { border: 1px solid #e5e7eb; border-radius: 14px; overflow: hidden; height: 340px; background: #eef2ff; }
.map-shell :deep(.kakao-map) { height: 100%; }
.map-meta { display: flex; gap: 8px; margin-top: 12px; flex-wrap: wrap; }
.pill { padding: 8px 12px; border-radius: 999px; background: #eef2ff; color: #374151; font-weight: 700; font-size: 13px; }
.tabs { display: flex; gap: 8px; flex-wrap: wrap; }
.tab { padding: 12px 18px; border-radius: 999px; border: 1px solid #d1d5db; background: #fff; cursor: pointer; font-weight: 700; color: #4b5563; }
.tab.active { background: #2563eb; color: #fff; border-color: #2563eb; box-shadow: 0 6px 14px rgba(37, 99, 235, 0.2); }
.day-card { display: flex; flex-direction: column; gap: 12px; }
.day-head { display: flex; align-items: center; justify-content: space-between; gap: 12px; flex-wrap: wrap; }
.mini-label { color: #7c8aa1; font-size: 12px; margin: 0 0 6px; text-transform: uppercase; letter-spacing: 0.02em; }
.muted { color: #6b7280; font-size: 13px; }
.place-list { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 10px; }
.place { background: #f5f7fb; border: 1px solid #e5e7eb; border-radius: 12px; padding: 14px; display: grid; grid-template-columns: 44px 1fr; gap: 10px; align-items: start; }
.place-order { width: 36px; height: 36px; border-radius: 50%; background: #2563eb; color: #fff; display: inline-flex; align-items: center; justify-content: center; font-weight: 700; font-size: 15px; }
.place-name { font-weight: 800; margin: 0 0 4px; }
.place-addr { color: #4b5563; margin: 0 0 4px; font-size: 14px; }
.place-memo { color: #6b7280; font-size: 13px; margin: 0; }
.add-route { padding: 12px 18px; border-radius: 999px; border: none; background: linear-gradient(90deg, #2563eb, #3b82f6); color: #fff; font-weight: 800; cursor: pointer; box-shadow: 0 12px 26px rgba(37, 99, 235, 0.25); }
.add-route:disabled { opacity: 0.7; cursor: not-allowed; box-shadow: none; }
.story { display: flex; flex-direction: column; gap: 10px; margin-top: 12px; }
.story-head { display: flex; justify-content: space-between; align-items: flex-start; gap: 12px; flex-wrap: wrap; }
.content { white-space: pre-line; line-height: 1.7; color: #1f2937; font-size: 15px; }
.story-stats { display: flex; gap: 12px; color: #6b7280; font-size: 14px; }
.reactions { display: flex; align-items: center; justify-content: space-between; gap: 12px; margin-top: 12px; }
.heart-btn { width: 52px; height: 52px; border-radius: 50%; border: 1px solid #d1d5db; background: #fff; display: inline-flex; align-items: center; justify-content: center; font-size: 22px; cursor: pointer; transition: transform 0.15s ease, box-shadow 0.15s ease; }
.heart-btn:hover { transform: translateY(-1px); box-shadow: 0 8px 18px rgba(0,0,0,0.08); }
.heart { font-size: 24px; line-height: 1; }
.heart.filled { color: #ef4444; }
.heart.empty { color: #9ca3af; }
.reaction-counts { display: flex; gap: 12px; color: #4b5563; font-weight: 600; }
.comments { margin-top: 12px; display: flex; flex-direction: column; gap: 12px; }
.comment-head { display: flex; justify-content: space-between; align-items: center; }
.comment-list { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 10px; }
.comment { border: 1px solid #f3f4f6; border-radius: 12px; padding: 12px; background: #f9fafb; }
.c-head { display: flex; justify-content: space-between; color: #6b7280; font-size: 13px; }
.c-body { margin-top: 6px; white-space: pre-line; color: #1f2937; }
.comment-form { display: flex; flex-direction: column; gap: 8px; }
textarea { width: 100%; padding: 12px; border: 1px solid #d1d5db; border-radius: 10px; resize: vertical; font-size: 14px; }
.sr-only { position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px; overflow: hidden; clip: rect(0, 0, 0, 0); white-space: nowrap; border: 0; }

@media (max-width: 900px) {
  .map-shell { height: 260px; }
  .day-head { align-items: flex-start; }
}
</style>
