<!-- MyPageView.vue -->
<template>
  <div class="mypage">
    <div class="title-area">
      <h2>마이페이지</h2>
      <p class="sub">나의 제주 여행 루트와 활동을 한 곳에서 관리하세요.</p>
    </div>

    <!-- 프로필 카드(와이어프레임 구조 따라감: 아바타/이름/요약/버튼) -->
    <section class="profile-card">
      <div class="avatar">{{ initial }}</div>

      <div class="profile-main">
        <div class="name">{{ me?.username ?? '...' }}</div>
        <div class="desc">여유로운 힐링 여행을 좋아하는 제주 러버입니다.</div>
        <div class="meta">가입일 · -</div>
      </div>

      <div class="stats">
        <div class="stat">
          <div class="num">0</div>
          <div class="label">팔로워</div>
        </div>
        <div class="stat">
          <div class="num">0</div>
          <div class="label">팔로잉</div>
        </div>
      </div>

      <div class="profile-actions">
        <button class="btn primary" type="button" disabled>프로필 편집</button>
        <button class="btn" type="button" @click="setTab('settings')">설정</button>
      </div>
    </section>

    <!-- 탭 바 (SVG 순서: 내 게시글/저장한 경로/좋아요/팔로워/팔로잉/설정) -->
    <nav class="tabs">
      <button
        v-for="t in tabs"
        :key="t.key"
        class="tab"
        :class="{ active: activeTab === t.key }"
        type="button"
        @click="setTab(t.key)"
      >
        {{ t.label }}
      </button>
    </nav>

    <!-- 컨텐츠 영역 -->
    <section class="content">
      <!-- 저장한 경로 탭(= routes)만 일단 “실제 구현” -->
      <div v-if="activeTab === 'routes'">
        <h3>저장한 경로</h3>
        <p class="hint">내가 저장한 제주 여행 루트입니다.</p>

        <p v-if="loading">불러오는 중...</p>
        <p v-else-if="error" class="error">{{ error }}</p>

        <div v-else-if="routes.length" class="route-list">
          <div
            v-for="r in routes"
            :key="r.id"
            class="route-item"
            @click="goDetail(r.id)"
          >
            <div class="rt-title">{{ r.title }}</div>
            <div class="rt-desc">{{ r.description || '설명 없음' }}</div>
            <div class="rt-meta">#{{ r.id }} · {{ formatDate(r.created_at) }}</div>
          </div>
        </div>

        <p v-else>아직 저장된 루트가 없습니다.</p>
      </div>

      <!-- 나머지 탭은 placeholder (UI만 먼저) -->
      <div v-else>
        <h3>{{ currentTabLabel }}</h3>
        <p class="hint">이 탭은 다음 단계에서 연결합니다. (지금은 UI 뼈대만)</p>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/api/client'

const route = useRoute()
const router = useRouter()

const tabs = [
  { key: 'posts', label: '내 게시글' },
  { key: 'routes', label: '저장한 경로' },
  { key: 'likes', label: '좋아요' },
  { key: 'followers', label: '팔로워' },
  { key: 'following', label: '팔로잉' },
  { key: 'settings', label: '설정' },
]

const activeTab = computed(() => {
  const t = route.query.tab
  return typeof t === 'string' ? t : 'routes'
})

const currentTabLabel = computed(() => {
  return tabs.find(t => t.key === activeTab.value)?.label ?? '마이페이지'
})

const me = ref(null)
const routes = ref([])
const loading = ref(false)
const error = ref('')

const initial = computed(() => {
  const u = me.value?.username
  return u ? u[0].toUpperCase() : 'J'
})

function setTab(tabKey) {
  router.replace({ query: { ...route.query, tab: tabKey } })
}

function goDetail(routeId) {
  router.push({ name: 'route-detail', params: { routeId } })
}

function formatDate(iso) {
  if (!iso) return '-'
  try { return new Date(iso).toLocaleString() } catch { return iso }
}

async function loadMe() {
  const { data } = await api.get('/auth/me/')
  me.value = data
}

async function loadRoutes() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await api.get('/routes/')
    routes.value = data
  } catch (e) {
    console.error(e)
    error.value = '저장한 경로를 불러오지 못했습니다.'
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await loadMe()
  if (activeTab.value === 'routes') {
    await loadRoutes()
  }
})

watch(activeTab, async (newTab) => {
  if (newTab === 'routes') {
    await loadRoutes()
  }
})
</script>

<style scoped>
.mypage { max-width: 1040px; margin: 0 auto; }
.title-area { margin: 18px 0 14px; }
.sub { color: #6b7280; margin-top: 6px; }

.profile-card {
  display: grid;
  grid-template-columns: 64px 1fr auto auto;
  gap: 16px;
  align-items: center;
  padding: 18px;
  border: 1px solid #e5e7eb;
  border-radius: 16px;
  background: #fff;
}

.avatar {
  width: 56px; height: 56px;
  border-radius: 999px;
  display: grid; place-items: center;
  background: #dbeafe;
  color: #1e40af;
  font-weight: 800;
}

.name { font-weight: 800; }
.desc { color: #6b7280; margin-top: 4px; font-size: 14px; }
.meta { color: #9ca3af; margin-top: 6px; font-size: 12px; }

.stats { display: flex; gap: 16px; margin-right: 10px; }
.stat { text-align: right; }
.num { font-weight: 800; }
.label { color: #6b7280; font-size: 12px; margin-top: 2px; }

.profile-actions { display: flex; gap: 10px; }
.btn {
  border: 1px solid #dbeafe;
  padding: 10px 14px;
  border-radius: 999px;
  background: #fff;
  cursor: pointer;
}
.btn.primary {
  background: #2563eb;
  border-color: #2563eb;
  color: #fff;
}

.tabs {
  display: flex;
  gap: 22px;
  padding: 14px 6px 10px;
  border-bottom: 1px solid #e5e7eb;
  margin-top: 10px;
}
.tab {
  border: none;
  background: transparent;
  padding: 10px 4px;
  cursor: pointer;
  color: #6b7280;
  position: relative;
}
.tab.active {
  color: #2563eb;
  font-weight: 700;
}
.tab.active::after {
  content: "";
  position: absolute;
  left: 0; right: 0; bottom: -10px;
  height: 2px;
  background: #2563eb;
}

.content { padding: 18px 0; }
.hint { color: #6b7280; margin-top: 6px; font-size: 14px; }
.error { color: #dc2626; margin-top: 10px; }

.route-list { display: grid; gap: 12px; margin-top: 14px; }
.route-item {
  border: 1px solid #eef2ff;
  border-radius: 14px;
  padding: 14px 16px;
  cursor: pointer;
  background: #fff;
}
.rt-title { font-weight: 800; }
.rt-desc { color: #6b7280; margin-top: 6px; }
.rt-meta { color: #9ca3af; margin-top: 8px; font-size: 12px; }
</style>
