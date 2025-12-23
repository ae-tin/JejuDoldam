<template>
  <div class="likes-tab-content">
    
    <div class="header">
      <h3>❤️ 내가 좋아한 이야기</h3>
      <span class="count" v-if="likes.length">총 {{ likes.length }}개</span>
    </div>

    <div v-if="loading" class="state-msg">
      <div class="spinner"></div> 목록을 불러오고 있어요...
    </div>

    <div v-else-if="error" class="state-msg error">
      ⚠️ {{ error }}
    </div>

    <div v-else-if="likes.length" class="post-grid">
      <article 
        v-for="post in likes" 
        :key="post.id" 
        class="post-card"
        @click="goDetail(post.id)"
      >
        <div class="card-header">
          <span v-if="post.route" class="route-badge">📍 루트 후기</span>
          <span v-else class="text-badge">📝 일반글</span>
        </div>

        <div class="card-body">
          <h4 class="title">{{ post.title }}</h4>
          <p class="preview">{{ post.content }}</p>
        </div>

        <div class="card-footer">
          <div class="meta-left">
            <span class="author">by {{ post.user?.username || '알 수 없음' }}</span>
            <span class="date">· {{ formatDate(post.created_at) }}</span>
          </div>
          
          <div class="meta-right heart-active">
            ❤️ Liked
          </div>
        </div>
      </article>
    </div>

    <div v-else class="empty-state">
      <div class="icon">💔</div>
      <p>아직 좋아요한 게시글이 없습니다.<br>마음에 드는 여행기를 찾아보세요!</p>
      <button class="btn-action" @click="router.push('/community')">
        커뮤니티 둘러보기
      </button>
    </div>

  </div>
</template>

<script setup>
// Vue 핵심 기능 임포트
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
// API 클라이언트 (axios)
import api from '@/api/client'

const router = useRouter()

// --- [상태 변수] ---
const likes = ref([])      // 데이터 저장소
const loading = ref(false) // 로딩 상태
const error = ref('')      // 에러 메시지

// --- [함수: 페이지 이동] ---
const goDetail = (postId) => {
  // 클릭 시 해당 게시글의 상세 페이지로 이동
  router.push({ name: 'community-detail', params: { postId } })
}

// --- [함수: 날짜 변환] ---
// ISO 날짜(2025-12-23...)를 보기 편한 형식(2025.12.23)으로 변환
const formatDate = (iso) => {
  if (!iso) return '-'
  const d = new Date(iso)
  return `${d.getFullYear()}.${d.getMonth() + 1}.${d.getDate()}`
}

// --- [함수: API 요청] ---
// async/await를 사용하여 비동기 통신을 처리합니다.
const fetchLikedPosts = async () => {
  loading.value = true
  error.value = ''
  
  try {
    // 1. GET 요청 전송
    const { data } = await api.get('/posts/my/like/')
    
    // 2. 데이터 유효성 검사 및 정렬
    // 배열이 맞는지 확인 후, ID 역순(최신순)으로 정렬하여 저장
    if (Array.isArray(data)) {
      likes.value = data.sort((a, b) => b.id - a.id)
    } else {
      likes.value = []
    }
  } catch (e) {
    console.error(e)
    error.value = '목록을 불러오지 못했습니다. 아직 좋아요한 게시글이 없을 수 있습니다!'
  } finally {
    loading.value = false
  }
}

// --- [라이프사이클] ---
// 컴포넌트가 화면에 나타나면 데이터를 즉시 요청합니다.
onMounted(() => {
  fetchLikedPosts()
})
</script>

<style scoped>
/* [스타일링 전략]
  MyPagePosts.vue와 완전히 동일한 클래스명을 사용하여 시각적 통일감을 줍니다.
*/

/* 헤더 영역 */
.header {
  display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px;
}
.header h3 { font-size: 1.3rem; font-weight: 700; color: #333; }
.count { color: #ff6b6b; font-weight: 600; } /* 좋아요 포인트 컬러 */

/* 그리드 레이아웃 (반응형) */
.post-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 24px;
}

/* 카드 디자인 (MyPagePosts와 동일) */
.post-card {
  background: white;
  border-radius: 16px;
  border: 1px solid #eee;
  box-shadow: 0 4px 15px rgba(0,0,0,0.05);
  cursor: pointer;
  transition: transform 0.2s, border-color 0.2s;
  display: flex;
  flex-direction: column;
  height: 220px; /* 높이 고정 */
  position: relative;
  overflow: hidden;
}

/* 호버 효과 */
.post-card:hover {
  transform: translateY(-5px);
  border-color: #2cb398; /* 민트색 테두리 */
  box-shadow: 0 10px 25px rgba(0,0,0,0.1);
}

/* 카드 상단 뱃지 */
.card-header { padding: 20px 20px 0; margin-bottom: 10px; }

.route-badge {
  background-color: #e6f7f4; color: #2cb398;
  padding: 4px 10px; border-radius: 20px;
  font-size: 0.75rem; font-weight: 700;
}

.text-badge {
  background-color: #f5f5f5; color: #666;
  padding: 4px 10px; border-radius: 20px;
  font-size: 0.75rem; font-weight: 600;
}

/* 카드 본문 */
.card-body { padding: 0 20px; flex: 1; }

.title {
  font-size: 1.15rem; font-weight: 700; margin-bottom: 8px; color: #222;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}

.preview {
  color: #666; font-size: 0.95rem; line-height: 1.5;
  display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden;
}

/* 카드 푸터 */
.card-footer {
  padding: 15px 20px;
  border-top: 1px solid #f9f9f9;
  display: flex; justify-content: space-between; align-items: center;
  margin-top: auto;
}

.meta-left { font-size: 0.85rem; color: #999; }
.author { font-weight: 600; color: #555; }

.meta-right { font-size: 0.85rem; font-weight: 600; }
.heart-active { color: #ff6b6b; } /* 좋아요 강조색 */

/* 로딩, 에러, 빈 상태 */
.state-msg { text-align: center; padding: 60px 0; color: #888; }
.error { color: #e74c3c; }

.empty-state {
  text-align: center; padding: 80px 0;
  background: #fdfdfd; border-radius: 16px; border: 1px dashed #eee; color: #999;
}
.icon { font-size: 3rem; margin-bottom: 16px; }

.btn-action {
  margin-top: 20px; background-color: #333; color: white; border: none;
  padding: 12px 24px; border-radius: 30px; font-weight: 700; cursor: pointer;
}
.spinner {
  display: inline-block; width: 20px; height: 20px;
  border: 3px solid #ddd; border-top-color: #2cb398;
  border-radius: 50%; animation: spin 1s infinite linear; margin-right: 8px; vertical-align: middle;
}
@keyframes spin { to { transform: rotate(360deg); } }
</style>