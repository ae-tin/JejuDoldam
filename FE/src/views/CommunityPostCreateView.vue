<template>
  <div class="write-container">
    <header class="page-header fade-element">
      <RouterLink to="/community" class="back-link">
        <span class="icon">←</span> 목록으로 돌아가기
      </RouterLink>
      <div class="header-text">
        <h1>여행기 작성 ✍️</h1>
        <p class="sub-text">당신의 특별한 여행 경험을 공유해주세요.</p>
      </div>
    </header>

    <div class="write-card fade-element delay-100">
      <form @submit.prevent="handleSubmit">
        
        <div class="input-group">
          <label for="title">제목</label>
          <input 
            id="title" 
            v-model="form.title" 
            type="text" 
            required 
            placeholder="제목을 입력해주세요 (예: 3박 4일 제주 힐링 여행)" 
            class="custom-input"
          />
        </div>

        <div class="input-group">
          <label for="route">
            연결할 여행 루트 <span class="optional">(선택)</span>
          </label>
          <div class="select-wrapper">
            <select id="route" v-model="form.route" class="custom-select">
              <option :value="null">여행 루트를 선택하지 않음</option>
              <option v-for="r in routes" :key="r.id" :value="r.id">
                [Route #{{ r.id }}] {{ r.title }}
              </option>
            </select>
            <span class="select-arrow">▼</span>
          </div>
          <p class="help-text">💡 저장해둔 나의 여행 경로를 글과 함께 보여줄 수 있어요.</p>
        </div>

        <div class="input-group">
          <label for="content">내용</label>
          <textarea
            id="content"
            v-model="form.content"
            rows="12"
            required
            placeholder="여행의 추억, 꿀팁, 맛집 정보 등을 자유롭게 적어주세요."
            class="custom-textarea"
          ></textarea>
        </div>

        <div class="action-area">
          <button type="submit" class="submit-btn" :disabled="loading">
            <span v-if="loading" class="spinner"></span>
            {{ loading ? '등록 중...' : '게시글 등록하기' }}
          </button>
        </div>

        <p v-if="error" class="error-msg">⚠️ {{ error }}</p>

      </form>
    </div>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/api/client'

const router = useRouter()

const form = ref({
  title: '',
  content: '',
  route: null,
})

const routes = ref([])
const loading = ref(false)
const error = ref('')

const loadRoutes = async () => {
  try {
    const { data } = await api.get('/routes/')
    routes.value = data
  } catch (e) {
    console.error(e)
  }
}

const handleSubmit = async () => {
  if (!form.value.title.trim() || !form.value.content.trim()) return
  loading.value = true
  error.value = ''
  try {
    const payload = {
      title: form.value.title,
      content: form.value.content,
      route: form.value.route,
    }
    await api.post('/posts/', payload)
    // alert('게시글이 등록되었습니다.') // UX상 부드러운 이동을 위해 alert 제거 가능
    router.push({ name: 'community-list' })
  } catch (e) {
    console.error(e)
    error.value = '게시글 등록에 실패했습니다. 다시 시도해주세요.'
  } finally {
    loading.value = false
  }
}

// 애니메이션 옵저버
let observer = null
onMounted(() => {
  loadRoutes()
  
  observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
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
/* 컨테이너 */
.write-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 100px 20px 60px;
  font-family: -apple-system, BlinkMacSystemFont, "Pretendard", Roboto, sans-serif;
  color: #333;
}

/* 헤더 */
.page-header { margin-bottom: 30px; }
.back-link {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: #888;
  text-decoration: none;
  font-size: 0.95rem;
  margin-bottom: 20px;
  transition: color 0.2s;
}
.back-link:hover { color: #2cb398; }

.header-text h1 {
  font-size: 2rem;
  font-weight: 800;
  margin-bottom: 8px;
  color: #111;
}
.sub-text { color: #666; }

/* 폼 카드 */
.write-card {
  background: white;
  border-radius: 20px;
  padding: 40px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.05);
  border: 1px solid #f0f0f0;
}

/* 입력 그룹 공통 */
.input-group { margin-bottom: 28px; }
.input-group label {
  display: block;
  font-weight: 700;
  margin-bottom: 10px;
  color: #333;
  font-size: 1rem;
}
.optional {
  font-weight: normal;
  color: #999;
  font-size: 0.85rem;
  margin-left: 4px;
}

/* Input & Textarea 스타일 */
.custom-input, .custom-textarea, .custom-select {
  width: 100%;
  padding: 14px 16px;
  border: 1px solid #ddd;
  border-radius: 12px;
  font-size: 1rem;
  color: #333;
  background-color: #fafafa;
  transition: all 0.2s ease;
  font-family: inherit;
  outline: none;
}

.custom-input:focus, .custom-textarea:focus, .custom-select:focus {
  background-color: #fff;
  border-color: #2cb398;
  box-shadow: 0 0 0 4px rgba(44, 179, 152, 0.1);
}

.custom-textarea { resize: vertical; min-height: 150px; line-height: 1.6; }

/* 셀렉트 박스 커스텀 */
.select-wrapper { position: relative; }
.custom-select { appearance: none; cursor: pointer; padding-right: 40px; }
.select-arrow {
  position: absolute;
  right: 16px; top: 50%;
  transform: translateY(-50%);
  color: #999;
  pointer-events: none;
  font-size: 0.8rem;
}
.help-text { font-size: 0.85rem; color: #888; margin-top: 8px; }

/* 버튼 영역 */
.action-area { margin-top: 40px; }
.submit-btn {
  width: 100%;
  padding: 16px;
  background-color: #2cb398;
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 1.1rem;
  font-weight: 800;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 10px;
}
.submit-btn:hover { background-color: #249e85; transform: translateY(-2px); box-shadow: 0 5px 15px rgba(44, 179, 152, 0.3); }
.submit-btn:disabled { background-color: #ccc; cursor: not-allowed; transform: none; box-shadow: none; }

/* 에러 메시지 */
.error-msg { margin-top: 20px; color: #e74c3c; text-align: center; font-weight: bold; background: #fff5f5; padding: 10px; border-radius: 8px; }

/* 로딩 스피너 */
.spinner {
  width: 18px; height: 18px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s infinite linear;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* 애니메이션 */
.fade-element { opacity: 0; transform: translateY(20px); transition: 0.8s ease; }
.fade-element.visible { opacity: 1; transform: translateY(0); }
.delay-100 { transition-delay: 0.1s; }

/* 반응형 */
@media (max-width: 600px) {
  .write-card { padding: 24px 20px; }
  .header-text h1 { font-size: 1.8rem; }
}
</style>