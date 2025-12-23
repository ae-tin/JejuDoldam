<template>
  <div class="posts-tab-content">
    
    <div class="header">
      <h3>✍️ 내가 쓴 여행기</h3>
      <span class="count" v-if="posts.length">총 {{ posts.length }}개</span>
    </div>

    <div v-if="loading" class="state-msg">
      <div class="spinner"></div> 불러오는 중...
    </div>

    <div v-else-if="error" class="state-msg error">
      ⚠️ {{ error }}
    </div>

    <div v-else-if="posts.length" class="post-grid">
      <article 
        v-for="post in posts" 
        :key="post.id" 
        class="post-card"
        @click="goDetail(post.id)"
      >
        <div class="card-header">
          <span v-if="post.route" class="route-badge">📍 루트 연결됨</span>
          <span v-else class="text-badge">📝 일반글</span>
        </div>

        <div class="card-body">
          <h4 class="title">{{ post.title }}</h4>
          <p class="preview">{{ post.content }}</p>
        </div>

        <div class="card-footer">
          <span class="date">{{ formatDate(post.created_at) }}</span>
          
          <div class="stats">
            <span>❤️ {{ post.like_count || 0 }}</span>
            <span>💬 {{ post.comment_count || 0 }}</span>
          </div>
        </div>
      </article>
    </div>

    <div v-else class="empty-state">
      <div class="icon">📝</div>
      <p>아직 작성한 여행기가 없어요.<br>나만의 여행 이야기를 들려주세요!</p>
      <button class="btn-write" @click="router.push('/community/new')">
        첫 글 작성하러 가기
      </button>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
// 우리가 미리 만들어둔 Axios 인스턴스 (baseURL 설정됨)
import api from '@/api/client'

const router = useRouter()

// --- [상태 변수 (Reactive Data)] ---
const posts = ref([])      // 게시글 목록을 저장할 배열
const loading = ref(false) // 로딩 중 상태 (true/false)
const error = ref('')      // 에러 메시지 저장

// --- [함수: 페이지 이동] ---
const goDetail = (postId) => {
  // name 기반 라우팅을 사용하여 커뮤니티 상세 페이지로 이동
  router.push({ name: 'community-detail', params: { postId } })
}

// --- [함수: 날짜 포맷팅] ---
// ISO 날짜 문자열(2025-12-22T...)을 보기 좋은 형태(2025.12.22)로 변환
const formatDate = (iso) => {
  if (!iso) return '-'
  const d = new Date(iso)
  return `${d.getFullYear()}.${d.getMonth() + 1}.${d.getDate()}`
}

// --- [함수: API 호출] ---
const fetchMyPosts = async () => {
  // 1. 요청 시작: 로딩 상태 켜기
  loading.value = true
  error.value = ''
  
  try {
    // 2. API 요청 (GET /posts/my/)
    // api.get을 사용하면 설정된 baseURL(http://127.0.0.1:8000/api/v1) 뒤에 경로가 붙습니다.
    const { data } = await api.get('/posts/my/')
    
    // 3. 데이터 저장 (최신순 정렬: ID가 클수록 최신)
    posts.value = data.sort((a, b) => b.id - a.id)
    
  } catch (e) {
    console.error('내 게시글 로드 실패:', e)
    // 에러 발생 시 사용자에게 보여줄 메시지 설정
    error.value = '게시글 목록을 불러오지 못했습니다.'
  } finally {
    // 4. 요청 종료: 성공/실패 여부와 상관없이 로딩 끄기
    loading.value = false
  }
}

// --- [라이프사이클 훅] ---
// 컴포넌트가 화면에 나타나면(마운트되면) API를 호출합니다.
onMounted(() => {
  fetchMyPosts()
})
</script>

<style scoped>
/* 헤더 스타일 */
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}
.header h3 {
  font-size: 1.3rem;
  font-weight: 700;
  color: #333;
}
.count {
  color: #888;
  font-weight: 600;
}

/* [Grid 레이아웃]
  - MyPageRoutes와 동일한 그리드 시스템을 사용하여 일관성 유지
  - 화면 크기에 따라 열 개수가 자동 조절됨 (최소 너비 300px)
*/
.post-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 24px;
}

/* 카드 디자인 */
.post-card {
  background: white;
  border-radius: 16px;
  border: 1px solid #eee;
  box-shadow: 0 4px 15px rgba(0,0,0,0.05);
  cursor: pointer;
  transition: transform 0.2s, border-color 0.2s;
  display: flex;
  flex-direction: column;
  height: 220px; /* 게시글 카드는 높이를 고정하여 정돈된 느낌 줌 */
  position: relative;
  overflow: hidden;
}

/* 호버 효과: 위로 살짝 뜨면서 테두리가 민트색으로 변경 */
.post-card:hover {
  transform: translateY(-5px);
  border-color: #2cb398;
  box-shadow: 0 10px 25px rgba(0,0,0,0.1);
}

/* 카드 헤더 (뱃지 영역) */
.card-header {
  padding: 20px 20px 0;
  margin-bottom: 10px;
}

.route-badge {
  background-color: #e6f7f4; /* 연한 민트 배경 */
  color: #2cb398;            /* 민트 글씨 */
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 700;
}

.text-badge {
  background-color: #f5f5f5;
  color: #666;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
}

/* 카드 본문 */
.card-body {
  padding: 0 20px;
  flex: 1; /* 남은 공간을 차지 */
}

.title {
  font-size: 1.15rem;
  font-weight: 700;
  margin-bottom: 8px;
  color: #222;
  /* 제목이 너무 길면 말줄임(...) 처리 */
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.preview {
  color: #666;
  font-size: 0.95rem;
  line-height: 1.5;
  /* 3줄 이상 넘어가면 말줄임 처리 (WebKit 기반 브라우저용) */
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* 카드 푸터 (날짜, 통계) */
.card-footer {
  padding: 15px 20px;
  border-top: 1px solid #f9f9f9;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: auto; /* 맨 아래로 밀어내기 */
}

.date {
  font-size: 0.85rem;
  color: #999;
}

.stats {
  display: flex;
  gap: 12px;
  font-size: 0.85rem;
  color: #666;
  font-weight: 600;
}

/* 로딩 및 빈 상태 스타일 */
.state-msg {
  text-align: center;
  padding: 60px 0;
  color: #888;
}
.error { color: #e74c3c; }

.empty-state {
  text-align: center;
  padding: 80px 0;
  color: #999;
  background: #fdfdfd;
  border-radius: 16px;
  border: 1px dashed #eee;
}
.icon { font-size: 3rem; margin-bottom: 16px; }

/* 글쓰기 버튼 (Empty State용) */
.btn-write {
  margin-top: 20px;
  background-color: #2cb398;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 30px;
  font-weight: 700;
  cursor: pointer;
  transition: background-color 0.2s;
}
.btn-write:hover {
  background-color: #249e85;
}

/* 로딩 스피너 애니메이션 */
.spinner {
  display: inline-block;
  width: 20px; height: 20px;
  border: 3px solid #ddd;
  border-top-color: #2cb398;
  border-radius: 50%;
  animation: spin 1s infinite linear;
  margin-right: 8px;
  vertical-align: middle;
}
@keyframes spin { to { transform: rotate(360deg); } }
</style>