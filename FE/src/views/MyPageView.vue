<template>
  <div class="mypage-layout">
    
    <section class="profile-header">
      <div class="cover-image"></div>
      
      <div class="profile-inner">
        <div class="profile-card">
          <div class="card-top">
            <div class="avatar-box">
              {{ initial }}
            </div>
            <div class="user-text">
              <h2 class="name">{{ me?.username || '여행자' }}님</h2>
              <p class="bio">여유로운 힐링 여행을 좋아하는 제주 러버 🏝️</p>
            </div>
          </div>

          <div class="card-bottom">
            <div class="stats-group">
              <div class="stat-box">
                <strong class="count">0</strong>
                <span class="label">팔로워</span>
              </div>
              <div class="divider"></div>
              <div class="stat-box">
                <strong class="count">0</strong>
                <span class="label">팔로잉</span>
              </div>
            </div>
            
            <div class="btn-group">
              <button class="btn-edit" @click="changeTab('settings')">프로필 편집</button>
              <!-- <button class="btn-settings" @click="changeTab('settings')">⚙️</button> -->
            </div>
          </div>
        </div>
      </div>
    </section>

    <div class="tab-sticky-wrapper">
      <nav class="tab-nav">
        <button 
          v-for="t in tabs" 
          :key="t.key" 
          class="tab-link"
          :class="{ active: currentTab === t.key }"
          @click="changeTab(t.key)"
        >
          {{ t.label }}
        </button>
      </nav>
    </div>

    <main class="content-area fade-in">
      <KeepAlive>
        <component :is="currentTabComponent" />
      </KeepAlive>
    </main>

  </div>
</template>

<script setup>
// Vue의 반응형 시스템(ref, computed)과 생명주기 훅(onMounted)을 가져옵니다.
import { ref, computed, onMounted } from 'vue'
// 라우터 기능(현재 주소 확인, 페이지 이동)을 가져옵니다.
import { useRoute, useRouter } from 'vue-router'
// Axios API 클라이언트
import api from '@/api/client'

// --- [중요] 컴포넌트 일반 임포트 (Static Import) ---
// 1. defineAsyncComponent를 사용하지 않고 바로 import 합니다.
// 2. 이렇게 하면 페이지가 열릴 때 컴포넌트를 미리 준비해두므로, 
//    탭을 눌렀을 때 로딩 대기 시간이나 멈춤 현상(Freezing)이 발생하지 않습니다.
import MyPageRoutes from '@/components/mypage/MyPageRoutes.vue'
import MyPagePosts from '@/components/mypage/MyPagePosts.vue'
import MyLikeList from '@/components/mypage/MyLikeList.vue' // (파일명을 MyLikeList로 변경했다면 이걸로 쓰세요)
import MyPageSettings from '@/components/mypage/MyPageSettings.vue'

// --- [라우터 객체 생성] ---
const route = useRoute()    // 현재 URL 정보 (?tab=likes 같은 쿼리 파라미터 확인용)
const router = useRouter()  // 페이지 이동 명령용 (router.push, replace)

// --- [상태 변수] ---
const me = ref(null) // 내 정보를 담을 변수 (초기값은 비어있음)

// --- [탭 설정] ---
// key: URL 쿼리에 사용될 식별자
// label: 화면에 표시될 탭 이름
// comp: 해당 탭이 활성화됐을 때 보여줄 '컴포넌트 객체' (위에서 import 한 것)
const tabs = [
  { key: 'routes', label: '저장한 경로', comp: MyPageRoutes },
  { key: 'posts', label: '내 게시글', comp: MyPagePosts },
  { key: 'likes', label: '좋아요', comp: MyLikeList }, // ✅ 여기에 좋아요 컴포넌트 연결
  { key: 'followers', label: '팔로워', comp: null },   // 아직 기능 구현 전
  { key: 'following', label: '팔로잉', comp: null },
  { key: 'settings', label: '프로필', comp: MyPageSettings },
]

// --- [Computed: 계산된 속성] ---

// 1. 현재 활성화된 탭 파악하기
// URL이 '/mypage?tab=likes'라면 'likes'를 반환, 없으면 기본값 'routes'
const currentTab = computed(() => route.query.tab || 'routes')

// 2. 현재 보여줄 컴포넌트 결정하기
// tabs 배열에서 currentTab과 키가 같은 항목을 찾아, 그 안의 comp를 반환합니다.
// 만약 못 찾거나 comp가 비어있으면(null) 기본값으로 MyPageRoutes를 보여줍니다.
const currentTabComponent = computed(() => {
  const target = tabs.find(t => t.key === currentTab.value)
  return target?.comp || MyPageRoutes
})

// 3. 아바타용 이니셜 추출
// 내 정보(me)가 있으면 이름 첫 글자를 대문자로, 없으면 스마일 아이콘 표시
const initial = computed(() => {
  const u = me.value?.username
  return u ? u[0].toUpperCase() : '😊'
})

// --- [메서드: 기능 구현] ---

// 탭 변경 함수
// 단순히 변수를 바꾸는 게 아니라, URL의 쿼리 파라미터(?tab=...)를 변경합니다.
// 이렇게 해야 새로고침해도 탭이 유지되고, 뒤로가기도 자연스럽습니다.
const changeTab = (key) => {
  router.replace({ query: { ...route.query, tab: key } })
}

// 내 정보 가져오기 (비동기 통신)
const fetchMe = async () => {
  try {
    // 백엔드 API 호출
    const { data } = await api.get('/auth/me/')
    me.value = data
  } catch (e) {
    console.error('내 정보 로드 실패:', e)
  }
}

// --- [생명주기 훅] ---
// onMounted: 컴포넌트가 화면에 다 그려진 직후 실행됩니다.
onMounted(() => {
  fetchMe() // 들어오자마자 내 정보 로딩 시작
})
</script>

<style scoped>
/* scoped: 이 스타일은 오직 이 컴포넌트 내부에서만 적용됩니다. */

/* 전체 레이아웃 */
.mypage-layout {
  background-color: #f5f7fa; /* 부드러운 회색 배경 */
  min-height: 100vh;
  /* 상단 네비게이션 바(Navbar)가 fixed로 떠있어서 내용이 가려지는 것을 방지하기 위해 패딩 추가 */
  padding-top: 60px; 
  font-family: -apple-system, BlinkMacSystemFont, "Pretendard", Roboto, sans-serif;
}

/* 1. 프로필 영역 스타일 */
.profile-header {
  position: relative;
  background-color: #fff;
  padding-bottom: 20px;
  border-bottom: 1px solid #eee;
}

.cover-image {
  height: 200px;
  /* 시원한 느낌의 그라데이션 배경 */
  background: linear-gradient(120deg, #a1c4fd 0%, #c2e9fb 100%);
  width: 100%;
}

.profile-inner {
  max-width: 1000px;
  margin: 0 auto;
  padding: 0 20px;
  /* 커버 이미지 위로 프로필 카드가 겹쳐 보이도록 음수 마진 사용 */
  margin-top: -60px; 
  position: relative;
  z-index: 2;
}

.profile-card {
  background: white;
  border-radius: 20px;
  padding: 30px;
  /* 카드가 떠있는 듯한 입체감을 주는 그림자 */
  box-shadow: 0 10px 25px rgba(0,0,0,0.08);
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  flex-wrap: wrap; /* 화면이 좁아지면 줄바꿈 허용 */
  gap: 20px;
}

.card-top { display: flex; align-items: center; gap: 20px; }

.avatar-box {
  width: 90px; height: 90px;
  border-radius: 50%;
  background-color: #2cb398; /* 브랜드 메인 컬러 (민트) */
  color: white;
  font-size: 2.2rem;
  font-weight: 800;
  display: flex; align-items: center; justify-content: center;
  border: 5px solid #fff; /* 흰색 테두리로 배경과 분리 */
  box-shadow: 0 4px 10px rgba(0,0,0,0.1);
}

.user-text .name { font-size: 1.6rem; font-weight: 800; color: #333; margin-bottom: 6px; }
.user-text .bio { color: #666; font-size: 1rem; }

.card-bottom { display: flex; align-items: center; gap: 30px; }

.stats-group { display: flex; align-items: center; gap: 20px; }
.stat-box { text-align: center; }
.stat-box .count { display: block; font-size: 1.2rem; color: #333; }
.stat-box .label { font-size: 0.85rem; color: #888; }
.divider { width: 1px; height: 30px; background: #eee; }

.btn-group { display: flex; gap: 10px; }
.btn-edit { background: #2cb398; color: white; padding: 10px 20px; border-radius: 12px; border:none; font-weight:bold; cursor: pointer; }
.btn-settings { background: #fff; border: 1px solid #ddd; padding: 10px 14px; border-radius: 12px; font-size: 1.1rem; cursor: pointer; }

/* 2. 탭 메뉴 스타일 (Sticky) */
.tab-sticky-wrapper {
  background: #fff;
  position: sticky; /* 스크롤 시 상단에 고정됨 */
  top: 60px;        /* Navbar 바로 아래 위치 */
  z-index: 10;
  border-bottom: 1px solid #e0e0e0;
}
.tab-nav {
  max-width: 1000px;
  margin: 0 auto;
  padding: 0 20px;
  display: flex;
  gap: 30px;
  overflow-x: auto; /* 탭이 많아지면 가로 스크롤 생성 */
}
.tab-link {
  background: none; border: none;
  padding: 16px 0;
  font-size: 1rem;
  font-weight: 600;
  color: #888;
  cursor: pointer;
  white-space: nowrap;
  position: relative;
}
.tab-link.active { color: #333; font-weight: 800; }
/* 활성화된 탭 아래에 민트색 밑줄 표시 (가상 요소 사용) */
.tab-link.active::after {
  content: ''; position: absolute; bottom: 0; left: 0; right: 0;
  height: 3px; background: #2cb398;
}

/* 3. 컨텐츠 영역 스타일 */
.content-area {
  max-width: 1000px;
  margin: 0 auto;
  padding: 40px 20px;
  min-height: 500px;
}

/* 탭 전환 시 부드럽게 나타나는 애니메이션 */
.fade-in { animation: fadeIn 0.5s ease; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

/* 모바일 화면 대응 (768px 이하) */
@media (max-width: 768px) {
  .profile-card { flex-direction: column; align-items: flex-start; }
  .card-bottom { width: 100%; justify-content: space-between; margin-top: 20px; }
}
</style>