<template>
  <div class="community-container">
    <div class="page-header fade-element">
      <div class="header-text">
        <h1>여행 이야기 🗣️</h1>
        <p class="sub-text">다른 여행자들의 생생한 경험을 둘러보고 공유해보세요.</p>
      </div>
      <RouterLink to="/community/new" class="write-btn">
        <span>✏️ 글 작성하기</span>
      </RouterLink>
    </div>

    <div class="content-area fade-element delay-100">
      <div v-if="loading" class="status-msg">
        <div class="spinner"></div> 여행 이야기를 불러오는 중...
      </div>

      <div v-else-if="error" class="status-msg error">
        ⚠️ {{ error }}
      </div>

      <div v-else-if="posts.length" class="post-list">
        <article
          v-for="post in posts"
          :key="post.id"
          class="post-card"
          @click="goDetail(post.id)"
        > 

        <div class="info-container">
          <div v-if="post.route" class="route-badge">
            <span class="badge-icon">📍</span>
            <span class="badge-text">{{ post.route.title }}</span>
          </div>
          <div class="route-badge">
            <span class="badge-text">{{ post.user.username }}</span>
          </div>
        </div>
          <div class="card-body">
            <h3 class="post-title">{{ post.title }}</h3>
            <p class="post-preview">{{ post.content }}</p>
          </div>

          <div class="card-footer">
            <span class="date">{{ formatDate(post.created_at) }}</span>
            <div class="stats">
              <span class="stat-item">
                <i class="icon">💬</i> {{ post.comment_count }}
              </span>
              <span class="stat-item">
                <i class="icon">❤️</i> {{ post.like_count }}
              </span>
            </div>
          </div>
        </article>
      </div>

      <div v-else class="empty-state">
        <div class="empty-icon">📝</div>
        <p>아직 작성된 이야기가 없어요.</p>
        <RouterLink to="/community/new" class="link-text">
          첫 번째 이야기의 주인공이 되어보세요!
        </RouterLink>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/api/client'

const router = useRouter()
const posts = ref([])
const loading = ref(false)
const error = ref('')

// 날짜 포맷팅 (조금 더 깔끔하게 연-월-일 만 표시하거나, 상대 시간 사용 추천)
const formatDate = (iso) => {
  if (!iso) return '-'
  const date = new Date(iso)
  return `${date.getFullYear()}. ${date.getMonth() + 1}. ${date.getDate()}`
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

// 애니메이션 옵저버 로직 (HomeView와 동일)
let observer = null
onMounted(() => {
  fetchPosts()

  observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) entry.target.classList.add('visible')
    })
  }, { threshold: 0.1 })

  document.querySelectorAll('.fade-element').forEach(el => observer.observe(el))
})

onUnmounted(() => {
  if (observer) observer.disconnect()
})
</script>

<style scoped>
/* 전체 컨테이너 (Navbar 높이 고려) */
.community-container {
  max-width: 900px; /* 읽기 편한 너비 */
  margin: 0 auto;
  padding: 100px 20px 60px; /* 상단 여백 넉넉히 */
  font-family: -apple-system, BlinkMacSystemFont, "Pretendard", Roboto, sans-serif;
  color: #333;
}

/* 헤더 영역 */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 40px;
  flex-wrap: wrap;
  gap: 20px;
}

.header-text h1 {
  font-size: 2rem;
  font-weight: 800;
  margin-bottom: 8px;
  color: #111;
}

.sub-text {
  color: #666;
  font-size: 1rem;
}

/* 글 작성 버튼 (민트색 포인트) */
.write-btn {
  background-color: #2cb398;
  color: white;
  padding: 12px 24px;
  border-radius: 30px;
  font-weight: bold;
  text-decoration: none;
  transition: all 0.2s;
  box-shadow: 0 4px 12px rgba(44, 179, 152, 0.3);
  display: inline-flex;
  align-items: center;
}

.write-btn:hover {
  background-color: #249e85;
  transform: translateY(-2px);
}

/* 게시글 리스트 레이아웃 */
.post-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* 게시글 카드 스타일 */
.post-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  border: 1px solid #eee;
  box-shadow: 0 2px 8px rgba(0,0,0,0.03);
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
  overflow: hidden;
}

.post-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0,0,0,0.08);
  border-color: #2cb398; /* 호버 시 테두리 민트색 */
}

/* 연결된 루트 뱃지 */
.route-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background-color: #e6f7f4; /* 아주 연한 민트 배경 */
  color: #2cb398;
  padding: 6px 12px;
  border-radius: 8px;
  font-size: 0.85rem;
  font-weight: 600;
  margin-bottom: 12px;
}

/* 카드 본문 */
.post-title {
  font-size: 1.3rem;
  font-weight: 700;
  margin-bottom: 8px;
  color: #222;
  line-height: 1.3;
}

.post-preview {
  color: #666;
  font-size: 1rem;
  line-height: 1.6;
  margin-bottom: 20px;
  
  /* 두 줄 말줄임 처리 (CSS line-clamp) */
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 카드 푸터 (메타 정보) */
.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.9rem;
  color: #999;
  border-top: 1px solid #f5f5f5;
  padding-top: 16px;
}

.stats {
  display: flex;
  gap: 16px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #777;
}

.icon {
  font-style: normal;
  font-size: 1rem;
}

/* 로딩 & 에러 & 빈 상태 */
.status-msg {
  text-align: center;
  padding: 60px 0;
  color: #888;
  font-size: 1.1rem;
}
.error { color: #e74c3c; }

.spinner {
  display: inline-block;
  width: 16px; height: 16px;
  border: 2px solid #ddd;
  border-top-color: #2cb398;
  border-radius: 50%;
  animation: spin 1s infinite linear;
  margin-right: 8px;
}
@keyframes spin { to { transform: rotate(360deg); } }

.empty-state {
  text-align: center;
  padding: 80px 20px;
  background: #f9fafb;
  border-radius: 16px;
  color: #666;
}
.empty-icon { font-size: 3rem; margin-bottom: 16px; }
.link-text {
  display: block;
  margin-top: 10px;
  color: #2cb398;
  font-weight: bold;
  text-decoration: none;
}
.link-text:hover { text-decoration: underline; }

/* 애니메이션 */
.fade-element { opacity: 0; transform: translateY(20px); transition: 0.8s ease; }
.fade-element.visible { opacity: 1; transform: translateY(0); }
.delay-100 { transition-delay: 0.1s; }

/* 모바일 대응 */
@media (max-width: 600px) {
  .page-header { flex-direction: column; align-items: flex-start; gap: 15px; }
  .write-btn { width: 100%; justify-content: center; }
  .header-text h1 { font-size: 1.6rem; }
}

.info-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
</style>