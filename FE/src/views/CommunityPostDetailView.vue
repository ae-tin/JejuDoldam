<template>
  <div class="detail-container">
    <header class="post-header fade-element">
      <div class="header-top">
        <span class="category-badge">커뮤니티</span>
        
        <div class="header-actions">
          <RouterLink to="/community" class="back-link">
            <span class="icon">←</span> 목록으로
          </RouterLink>

          <div v-if="isMyPost" class="owner-btn-group">
            <button @click="goEdit" class="text-btn edit">수정</button>
            <span class="sep">|</span>
            <button @click="deletePost" class="text-btn delete">삭제</button>
          </div>
        </div>
      </div>
      
      <h1 class="post-title">{{ post?.title || '게시글 불러오는 중...' }}</h1>
      
      <div class="post-meta" v-if="post">
        <span class="meta-item author">작성자 {{ post.user.username || 'Unknown' }}</span>
        <span class="divider">·</span>
        <span class="meta-item date">{{ formatDate(post.created_at) }}</span>
      </div>
    </header>

    <div v-if="loading" class="status-msg">
      <div class="spinner"></div> 내용을 불러오고 있어요...
    </div>
    <div v-else-if="error" class="status-msg error">⚠️ {{ error }}</div>

    <div v-else-if="post" class="content-wrapper fade-element delay-100">
      
      <section v-if="post.route" class="route-card-wrapper">
        <div class="route-header">
          <div class="route-info">
            <span class="label">📍 연결된 여행 경로</span>
            <h2 class="route-name">{{ routeDetail?.title || post.route.title }}</h2>
            <p class="route-desc" v-if="routeDetail?.description">
              {{ routeDetail.description }}
            </p>
          </div>
          <button 
            class="save-route-btn desktop-only" 
            :disabled="addBusy || routeLoading"
            @click="addRouteToMine"
          >
            <span class="btn-icon">📥</span>
            {{ addBusy ? '저장 중...' : '내 여행으로 가져오기' }}
          </button>
        </div>

        <div class="map-container">
          <KakaoMap :places="dayPlaces" :key="selectedDayId" />
          <div class="map-overlay-info">
            <span class="badge">총 {{ sortedDays.length }}일</span>
            <span class="badge" v-if="selectedDay">Day {{ selectedDay.day }}</span>
          </div>
        </div>

        <div class="day-tabs" v-if="routeDetail">
          <button
            v-for="(d, index) in sortedDays"
            :key="d.id || index"
            class="tab-btn"
            :class="{ active: d.id === selectedDayId }"
            @click="selectedDayId = d.id"
          >
            Day {{ d.day }}
          </button>
        </div>

        <div class="day-detail-box">
          <div v-if="routeLoading" class="loading-text">루트 정보 로딩 중...</div>
          <div v-else-if="routeDetail && selectedDay" class="day-content">
            <h3 class="day-title">
              Day {{ selectedDay.day }} 일정
              <span class="place-count" v-if="dayPlaces.length">({{ dayPlaces.length }}곳)</span>
            </h3>
            <ul v-if="dayPlaces.length" class="timeline-list">
              <li v-for="(p, idx) in dayPlaces" :key="p.id" class="timeline-item">
                <div class="marker">{{ idx + 1 }}</div>
                <div class="place-card">
                  <strong class="place-name">{{ p.name }}</strong>
                  <p class="place-addr">{{ p.address || '주소 정보 없음' }}</p>
                  <p class="place-memo" v-if="p.memo">💡 {{ p.memo }}</p>
                </div>
              </li>
            </ul>
            <p v-else class="empty-text">이 날은 등록된 장소가 없습니다.</p>
          </div>
          <p v-else class="error-text">루트 정보를 불러올 수 없습니다.</p>
          <button class="save-route-btn mobile-only" :disabled="addBusy" @click="addRouteToMine">
            📥 내 여행으로 가져오기
          </button>
        </div>
      </section>

      <section class="post-body-section">
        <div class="post-content">{{ post.content }}</div>
        <div class="reaction-area">
          <button class="like-btn" :class="{ active: post.is_liked }" @click="toggleLike" :disabled="likeBusy">
            <span class="heart-icon">{{ post.is_liked ? '❤️' : '🤍' }}</span>
            <span class="like-count">{{ post.like_count }}</span>
          </button>
        </div>
      </section>

      <section class="comments-section">
        <h3 class="section-title">댓글 <span class="count">{{ commentCount }}</span></h3>
        <ul v-if="post.writed_comments?.length" class="comment-list">
          <li v-for="c in post.writed_comments" :key="c.id" class="comment-item">
            <div class="comment-header">
              <span class="comment-author">{{ c.user.username }}</span>
              <span class="comment-date">{{ formatDate(c.created_at) }}</span>
            </div>
            <p class="comment-content">{{ c.content }}</p>
          </li>
        </ul>
        <div v-else class="no-comments">첫 번째 댓글을 남겨보세요! 👇</div>
        <form class="comment-form" @submit.prevent="submitComment">
          <textarea v-model="commentInput" rows="3" placeholder="따뜻한 댓글을 남겨주세요 :)" class="comment-input"></textarea>
          <button type="submit" class="submit-btn" :disabled="commentBusy || !commentInput.trim()">등록</button>
        </form>
      </section>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/api/client'
import KakaoMap from '@/components/KakaoMap.vue'

const route = useRoute()
const router = useRouter()

// 상태값 (기존 유지)
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

// ✅ [수정됨] 백엔드에서 주는 is_writer 필드 활용
const isMyPost = computed(() => {
  // post 데이터가 있고, is_writer가 true일 때만 true 반환
  return post.value?.is_writer === true
})

const commentCount = computed(() => post.value?.writed_comments?.length ?? 0)

const formatDate = (iso) => {
  if (!iso) return '-'
  const date = new Date(iso)
  return `${date.getFullYear()}. ${date.getMonth() + 1}. ${date.getDate()}`
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
  return [...(d.places || [])].sort((a, b) => (a.order ?? 0) - (b.order ?? 0))
})

const fetchPost = async () => {
  loading.value = true
  error.value = ''
  try {
    const { data } = await api.get(`/posts/${route.params.postId}/`)
    post.value = data // is_writer 필드가 포함된 전체 데이터 저장

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

const fetchRouteDetail = async (routeId) => {
  routeLoading.value = true
  try {
    const { data } = await api.get(`/routes/post/${routeId}/`)
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

// ✅ 게시글 수정 페이지로 이동
const goEdit = () => {
  router.push({ name: 'community-edit', params: { postId: post.value.id } })
}

// ✅ 게시글 삭제 API 요청
const deletePost = async () => {
  if (!confirm('정말 이 게시글을 삭제하시겠습니까?')) return

  try {
    await api.delete(`/posts/${post.value.id}/`)
    alert('게시글이 삭제되었습니다.')
    router.replace('/community') // 목록으로 이동
  } catch (e) {
    console.error('삭제 실패:', e)
    alert('게시글 삭제 중 오류가 발생했습니다.')
  }
}

const toggleLike = async () => {
  if (!post.value) return
  likeBusy.value = true
  try {
    const { data } = await api.post(`/posts/${post.value.id}/like/`)
    post.value = data.post
  } catch (e) {
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
    alert('댓글 등록 실패')
  } finally {
    commentBusy.value = false
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
        places: (d.places || []).map((p, idx) => ({
          order: p.order ?? idx + 1,
          name: p.name,
          address: p.address ?? '',
          latitude: p.latitude,
          longitude: p.longitude,
          memo: p.memo ?? '',
        })),
      })),
    }
    const { data } = await api.post('/routes/confirm/', payload)
    if(confirm('내 경로에 저장되었습니다! 확인하러 가시겠습니까?')) {
      router.push({ name: 'route-detail', params: { routeId: data.id } })
    }
  } catch (e) {
    alert('저장 실패')
  } finally {
    addBusy.value = false
  }
}

onMounted(() => {
  fetchPost()
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(e => { if(e.isIntersecting) e.target.classList.add('visible') })
  }, { threshold: 0.1 })
  
  setTimeout(() => {
    document.querySelectorAll('.fade-element').forEach(el => observer.observe(el))
  }, 100)
})

watch(() => route.params.postId, fetchPost)
</script>

<style scoped>
/* 기존 스타일 유지 */
.detail-container {
  max-width: 900px;
  margin: 0 auto;
  padding: 100px 20px 60px;
  font-family: -apple-system, BlinkMacSystemFont, "Pretendard", Roboto, sans-serif;
  color: #333;
}

.post-header { margin-bottom: 40px; text-align: center; }
.header-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.category-badge { background-color: #e6f7f4; color: #2cb398; padding: 6px 12px; border-radius: 20px; font-size: 0.85rem; font-weight: 700; }

.header-actions { display: flex; align-items: center; gap: 16px; }

.back-link { color: #666; font-size: 0.9rem; text-decoration: none; display: flex; align-items: center; gap: 4px; }
.back-link:hover { color: #2cb398; }

/* ✅ 수정/삭제 버튼 그룹 스타일 */
.owner-btn-group {
  display: flex;
  align-items: center;
  gap: 8px;
}
.text-btn {
  background: none;
  border: none;
  font-size: 0.9rem;
  cursor: pointer;
  color: #888;
  padding: 4px 8px;
  border-radius: 6px;
  transition: all 0.2s;
}
.text-btn.edit:hover { color: #3b82f6; background-color: #eff6ff; }
.text-btn.delete:hover { color: #ef4444; background-color: #fef2f2; }
.sep { color: #ddd; font-size: 0.8rem; }

.post-title { font-size: 2.2rem; font-weight: 800; margin-bottom: 16px; line-height: 1.3; word-break: keep-all; }
.post-meta { color: #888; font-size: 0.95rem; }
.divider { margin: 0 8px; color: #ddd; }

/* 루트 카드 스타일 및 나머지 스타일들은 기존 코드 유지 */
.route-card-wrapper { background: #fff; border-radius: 20px; border: 1px solid #eee; box-shadow: 0 10px 30px rgba(0,0,0,0.05); overflow: hidden; margin-bottom: 50px; }
.route-header { padding: 24px; background: #fafafa; border-bottom: 1px solid #eee; display: flex; justify-content: space-between; align-items: flex-start; }
.route-info .label { font-size: 0.8rem; color: #2cb398; font-weight: 700; margin-bottom: 8px; display: block; }
.route-name { font-size: 1.4rem; margin-bottom: 6px; font-weight: 700; }
.route-desc { color: #666; font-size: 0.95rem; }

.save-route-btn { background-color: #2cb398; color: white; border: none; padding: 10px 20px; border-radius: 30px; font-weight: bold; cursor: pointer; transition: all 0.2s; display: flex; align-items: center; gap: 6px; }
.save-route-btn:hover { background-color: #249e85; transform: translateY(-2px); }
.save-route-btn:disabled { background-color: #a8d5cc; cursor: not-allowed; }
.mobile-only { display: none; width: 100%; justify-content: center; margin-top: 20px; }

.map-container { height: 350px; position: relative; background-color: #eee; z-index: 0; }
.map-overlay-info { position: absolute; bottom: 16px; right: 16px; z-index: 2; display: flex; gap: 8px; }
.badge { background: rgba(255,255,255,0.9); padding: 6px 12px; border-radius: 12px; font-size: 0.8rem; font-weight: bold; color: #333; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }

.day-tabs { position: relative; z-index: 10; display: flex; gap: 10px; padding: 20px; overflow-x: auto; background-color: #fff; border-bottom: 1px solid #f0f0f0; min-height: 60px; align-items: center; }
.tab-btn { background: #f5f5f5; border: none; padding: 8px 16px; border-radius: 20px; color: #666; font-weight: 600; cursor: pointer; white-space: nowrap; flex-shrink: 0; transition: all 0.2s; }
.tab-btn.active { background: #2cb398; color: white; box-shadow: 0 4px 10px rgba(44, 179, 152, 0.3); transform: translateY(-2px); }
.tab-btn:hover { background-color: #e0e0e0; }

.day-detail-box { padding: 24px; }
.day-title { font-size: 1.2rem; margin-bottom: 20px; font-weight: 700; }
.place-count { color: #888; font-size: 0.9rem; font-weight: normal; margin-left: 4px; }

.timeline-list { list-style: none; padding: 0; margin: 0; position: relative; }
.timeline-item { display: flex; gap: 16px; margin-bottom: 24px; position: relative; }
.timeline-item:not(:last-child)::after { content: ''; position: absolute; top: 36px; left: 14px; bottom: -20px; width: 2px; background-color: #eee; }
.marker { width: 30px; height: 30px; background-color: #2cb398; color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 0.9rem; flex-shrink: 0; z-index: 1; }
.place-card { background: #f9f9f9; flex: 1; padding: 16px; border-radius: 12px; }
.place-name { font-size: 1.05rem; display: block; margin-bottom: 4px; }
.place-addr { color: #888; font-size: 0.9rem; margin-bottom: 8px; }
.place-memo { background: #fff; padding: 8px 12px; border-radius: 8px; font-size: 0.9rem; color: #555; border: 1px dashed #ddd; }

.post-body-section { margin-bottom: 60px; line-height: 1.8; font-size: 1.1rem; color: #333; }
.post-content { white-space: pre-line; margin-bottom: 40px; }
.reaction-area { text-align: center; }
.like-btn { background: white; border: 2px solid #eee; padding: 10px 24px; border-radius: 50px; cursor: pointer; display: inline-flex; align-items: center; gap: 8px; transition: all 0.2s; font-size: 1.1rem; }
.like-btn:hover { border-color: #ff6b6b; color: #ff6b6b; }
.like-btn.active { border-color: #ff6b6b; background-color: #fff0f0; color: #ff6b6b; }
.like-count { font-weight: bold; }

.comments-section { border-top: 1px solid #eee; padding-top: 40px; }
.section-title { font-size: 1.3rem; margin-bottom: 24px; }
.section-title .count { color: #2cb398; margin-left: 4px; }
.comment-list { list-style: none; padding: 0; margin-bottom: 30px; }
.comment-item { padding: 20px 0; border-bottom: 1px solid #f5f5f5; }
.comment-header { display: flex; justify-content: space-between; margin-bottom: 8px; font-size: 0.9rem; }
.comment-author { font-weight: bold; color: #333; }
.comment-date { color: #aaa; }
.comment-content { color: #555; line-height: 1.5; white-space: pre-line; }
.no-comments { text-align: center; color: #999; padding: 30px 0; background: #fafafa; border-radius: 12px; margin-bottom: 20px; }
.comment-form { position: relative; }
.comment-input { width: 100%; padding: 16px; padding-right: 80px; border: 1px solid #ddd; border-radius: 12px; resize: none; font-family: inherit; transition: border-color 0.2s; outline: none; }
.comment-input:focus { border-color: #2cb398; }
.submit-btn { position: absolute; bottom: 12px; right: 12px; background: #333; color: white; border: none; padding: 8px 16px; border-radius: 8px; font-weight: bold; cursor: pointer; font-size: 0.9rem; }
.submit-btn:hover { background: #111; }
.submit-btn:disabled { background: #ccc; cursor: not-allowed; }

.fade-element { opacity: 0; transform: translateY(20px); transition: 0.8s ease; }
.fade-element.visible { opacity: 1; transform: translateY(0); }
.delay-100 { transition-delay: 0.1s; }
.status-msg { text-align: center; padding: 60px; color: #888; }
.spinner { display: inline-block; width: 20px; height: 20px; border: 3px solid #ddd; border-top-color: #2cb398; border-radius: 50%; animation: spin 1s infinite linear; margin-right: 10px; vertical-align: middle; }
@keyframes spin { to { transform: rotate(360deg); } }

@media (max-width: 768px) {
  .detail-container { padding-top: 80px; }
  .post-title { font-size: 1.6rem; }
  .desktop-only { display: none; }
  .mobile-only { display: flex; }
  .route-header { flex-direction: column; gap: 10px; }
}
</style>