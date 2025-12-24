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
          
          <div class="btn-actions">
            <button 
              class="btn-icon btn-edit" 
              @click.stop="goEdit(post.id)"
              title="게시글 수정"
            >
              ✏️
            </button>
            <button 
              class="btn-icon btn-delete" 
              @click.stop="deletePost(post.id)"
              title="게시글 삭제"
            >
              🗑️
            </button>
          </div>
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
import api from '@/api/client'

const router = useRouter()

const posts = ref([])
const loading = ref(false)
const error = ref('')

const goDetail = (postId) => {
  router.push({ name: 'community-detail', params: { postId } })
}

// ✅ [추가됨] 수정 페이지 이동 함수
const goEdit = (postId) => {
  router.push({ name: 'community-edit', params: { postId } })
}

const formatDate = (iso) => {
  if (!iso) return '-'
  const d = new Date(iso)
  return `${d.getFullYear()}.${d.getMonth() + 1}.${d.getDate()}`
}

const fetchMyPosts = async () => {
  loading.value = true
  error.value = ''
  try {
    const { data } = await api.get('/posts/my/')
    posts.value = data.sort((a, b) => b.id - a.id)
  } catch (e) {
    console.error('내 게시글 로드 실패:', e)
    error.value = '게시글 목록을 불러오지 못했습니다.'
  } finally {
    loading.value = false
  }
}

const deletePost = async (postId) => {
  if (!confirm('정말 이 게시글을 삭제하시겠습니까?')) return

  try {
    await api.delete(`/posts/${postId}/`)
    posts.value = posts.value.filter(p => p.id !== postId)
    alert('게시글이 삭제되었습니다.')
  } catch (e) {
    console.error('삭제 실패:', e)
    alert('게시글 삭제 중 오류가 발생했습니다.')
  }
}

onMounted(() => {
  fetchMyPosts()
})
</script>

<style scoped>
/* 기존 스타일 유지 */
.header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
.header h3 { font-size: 1.3rem; font-weight: 700; color: #333; }
.count { color: #888; font-weight: 600; }

.post-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 24px; }

.post-card {
  background: white; border-radius: 16px; border: 1px solid #eee; box-shadow: 0 4px 15px rgba(0,0,0,0.05);
  cursor: pointer; transition: transform 0.2s, border-color 0.2s;
  display: flex; flex-direction: column; height: 220px; position: relative; overflow: hidden;
}
.post-card:hover { transform: translateY(-5px); border-color: #2cb398; box-shadow: 0 10px 25px rgba(0,0,0,0.1); }

/* 카드 헤더 (Flexbox) */
.card-header {
  padding: 20px 20px 0; margin-bottom: 10px;
  display: flex; justify-content: space-between; align-items: center;
}

.route-badge { background-color: #e6f7f4; color: #2cb398; padding: 4px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 700; }
.text-badge { background-color: #f5f5f5; color: #666; padding: 4px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; }

/* ✅ [수정됨] 버튼 그룹 스타일 */
.btn-actions {
  display: flex;
  gap: 8px; /* 버튼 사이 간격 */
}

.btn-icon {
  background: none;
  border: none;
  font-size: 1.1rem;
  cursor: pointer;
  padding: 4px;
  border-radius: 50%;
  transition: background-color 0.2s;
  color: #888;
}

/* 수정 버튼 호버 (파란색 계열) */
.btn-edit:hover {
  background-color: #e0f2fe;
  color: #0ea5e9;
}

/* 삭제 버튼 호버 (빨간색 계열) */
.btn-delete:hover {
  background-color: #fee2e2;
  color: #ef4444;
}

/* 나머지 스타일 유지 */
.card-body { padding: 0 20px; flex: 1; }
.title { font-size: 1.15rem; font-weight: 700; margin-bottom: 8px; color: #222; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.preview {
  color: #666;
  font-size: 0.95rem;
  line-height: 1.5;
  /* 2줄까지만 보여주고 나머지는 ... 처리 */
  display: -webkit-box;
  -webkit-line-clamp: 1; /* 3줄 -> 2줄로 축소 */
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  /* 높이 제한 추가 (안전장치) */
  max-height: 3em; /* line-height(1.5) * 2줄 = 3em */
}

.card-footer { padding: 15px 20px; border-top: 1px solid #f9f9f9; display: flex; justify-content: space-between; align-items: center; margin-top: auto; }
.date { font-size: 0.85rem; color: #999; }
.stats { display: flex; gap: 12px; font-size: 0.85rem; color: #666; font-weight: 600; }

.state-msg { text-align: center; padding: 60px 0; color: #888; }
.error { color: #e74c3c; }
.empty-state { text-align: center; padding: 80px 0; color: #999; background: #fdfdfd; border-radius: 16px; border: 1px dashed #eee; }
.icon { font-size: 3rem; margin-bottom: 16px; }
.btn-write { margin-top: 20px; background-color: #2cb398; color: white; border: none; padding: 12px 24px; border-radius: 30px; font-weight: 700; cursor: pointer; transition: background-color 0.2s; }
.btn-write:hover { background-color: #249e85; }
.spinner { display: inline-block; width: 20px; height: 20px; border: 3px solid #ddd; border-top-color: #2cb398; border-radius: 50%; animation: spin 1s infinite linear; margin-right: 8px; vertical-align: middle; }
@keyframes spin { to { transform: rotate(360deg); } }
</style>