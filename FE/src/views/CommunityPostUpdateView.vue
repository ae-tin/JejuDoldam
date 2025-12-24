<template>
  <div class="write-container">
    
    <header class="page-header fade-element">
      <button @click="$router.back()" class="back-link">
        <span class="icon">←</span> 뒤로 가기
      </button>
      <div class="header-text">
        <h1>게시글 수정 ✍️</h1>
        <p class="sub-text">작성했던 내용을 수정할 수 있어요.</p>
      </div>
    </header>

    <div class="write-card fade-element delay-100">
      
      <div v-if="initialLoading" class="loading-box">
        <div class="spinner"></div>
        <p>기존 내용을 불러오는 중...</p>
      </div>

      <form v-else @submit.prevent="handleSubmit">
        
        <div class="input-group">
          <label for="title">제목</label>
          <input 
            id="title" 
            v-model="form.title" 
            type="text" 
            required 
            placeholder="제목을 입력해주세요" 
            class="custom-input"
          />
        </div>

        <div class="input-group">
          <label for="content">내용</label>
          <textarea
            id="content"
            v-model="form.content"
            rows="12"
            required
            placeholder="수정할 내용을 입력해주세요."
            class="custom-textarea"
          ></textarea>
        </div>

        <div class="action-area">
          <button type="submit" class="submit-btn" :disabled="saving">
            <span v-if="saving" class="spinner-white"></span>
            {{ saving ? '수정 중...' : '수정 완료' }}
          </button>
        </div>

        <p v-if="error" class="error-msg">⚠️ {{ error }}</p>

      </form>
    </div>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import api from '@/api/client'

const router = useRouter()
const route = useRoute()
const postId = route.params.postId // URL에서 게시글 ID 추출

const form = ref({
  title: '',
  content: '',
})

const initialLoading = ref(true) // 데이터 불러올 때 로딩
const saving = ref(false)        // 저장할 때 로딩
const error = ref('')

// --- [기존 데이터 불러오기] ---
const fetchPostData = async () => {
  initialLoading.value = true
  try {
    // GET /posts/<pk>/
    const { data } = await api.get(`/posts/${postId}/`)
    form.value.title = data.title
    form.value.content = data.content
  } catch (e) {
    console.error(e)
    alert('게시글 정보를 불러오지 못했습니다.')
    router.back()
  } finally {
    initialLoading.value = false
  }
}

// --- [수정 요청 (patch)] ---
const handleSubmit = async () => {
  if (!form.value.title.trim() || !form.value.content.trim()) return
  
  saving.value = true
  error.value = ''
  
  try {
    const payload = {
      title: form.value.title,
      content: form.value.content,
      // route 필드는 수정 불가능하므로 보내지 않음 (백엔드 로직에 따라 필요하다면 기존 값 추가)
    }

    // patch /posts/<pk>/
    await api.patch(`/posts/${postId}/`, payload)
    
    // 수정 완료 후 상세 페이지로 이동
    router.push({ name: 'community-detail', params: { postId } })
    
  } catch (e) {
    console.error(e)
    error.value = '게시글 수정에 실패했습니다. 다시 시도해주세요.'
  } finally {
    saving.value = false
  }
}

// --- [애니메이션 옵저버] ---
let observer = null
onMounted(() => {
  fetchPostData()
  
  observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) entry.target.classList.add('visible')
    })
  }, { threshold: 0.1 })
  
  // DOM 렌더링 후 관찰 시작 (약간의 지연)
  setTimeout(() => {
    document.querySelectorAll('.fade-element').forEach(el => observer.observe(el))
  }, 100)
})

onUnmounted(() => {
  if (observer) observer.disconnect()
})
</script>

<style scoped>
/* 기존 WriteView와 동일한 스타일 유지 */
.write-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 100px 20px 60px;
  font-family: -apple-system, BlinkMacSystemFont, "Pretendard", Roboto, sans-serif;
  color: #333;
}

.page-header { margin-bottom: 30px; }
.back-link {
  background: none; border: none; padding: 0;
  display: inline-flex; align-items: center; gap: 6px;
  color: #888; cursor: pointer; font-size: 0.95rem; margin-bottom: 20px;
  transition: color 0.2s;
}
.back-link:hover { color: #2cb398; }

.header-text h1 { font-size: 2rem; font-weight: 800; margin-bottom: 8px; color: #111; }
.sub-text { color: #666; }

.write-card {
  background: white; border-radius: 20px; padding: 40px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.05); border: 1px solid #f0f0f0;
  min-height: 400px; /* 로딩 시 높이 확보 */
}

.input-group { margin-bottom: 28px; }
.input-group label { display: block; font-weight: 700; margin-bottom: 10px; color: #333; font-size: 1rem; }

.custom-input, .custom-textarea {
  width: 100%; padding: 14px 16px; border: 1px solid #ddd; border-radius: 12px;
  font-size: 1rem; color: #333; background-color: #fafafa;
  transition: all 0.2s ease; font-family: inherit; outline: none;
}
.custom-input:focus, .custom-textarea:focus {
  background-color: #fff; border-color: #2cb398;
  box-shadow: 0 0 0 4px rgba(44, 179, 152, 0.1);
}
.custom-textarea { resize: vertical; min-height: 250px; line-height: 1.6; }

.action-area { margin-top: 40px; }
.submit-btn {
  width: 100%; padding: 16px; background-color: #2cb398; color: white;
  border: none; border-radius: 12px; font-size: 1.1rem; font-weight: 800;
  cursor: pointer; transition: all 0.2s;
  display: flex; justify-content: center; align-items: center; gap: 10px;
}
.submit-btn:hover:not(:disabled) {
  background-color: #249e85; transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(44, 179, 152, 0.3);
}
.submit-btn:disabled { background-color: #ccc; cursor: not-allowed; }

.error-msg { margin-top: 20px; color: #e74c3c; text-align: center; font-weight: bold; background: #fff5f5; padding: 10px; border-radius: 8px; }

/* 로딩 UI */
.loading-box {
  height: 300px; display: flex; flex-direction: column;
  align-items: center; justify-content: center; color: #888;
}
.spinner {
  width: 30px; height: 30px; border: 3px solid #eee; border-top-color: #2cb398;
  border-radius: 50%; animation: spin 0.8s infinite linear; margin-bottom: 16px;
}
.spinner-white {
  width: 18px; height: 18px; border: 2px solid rgba(255,255,255,0.3);
  border-top-color: white; border-radius: 50%; animation: spin 0.8s infinite linear;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* 애니메이션 */
.fade-element { opacity: 0; transform: translateY(20px); transition: 0.8s ease; }
.fade-element.visible { opacity: 1; transform: translateY(0); }
.delay-100 { transition-delay: 0.1s; }

@media (max-width: 600px) {
  .write-card { padding: 24px 20px; }
  .header-text h1 { font-size: 1.8rem; }
}
</style>