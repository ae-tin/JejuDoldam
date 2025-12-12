<template>
  <div class="page">
    <header class="header">
      <button class="btn btn-ghost" type="button" @click="goBack">
        ← 뒤로
      </button>

      <div class="header-text">
        <h2 class="title">{{ detail?.title || '루트 상세' }}</h2>
        <p class="desc">{{ detail?.description || '설명이 없습니다.' }}</p>
      </div>
    </header>

    <section class="card">
      <div v-if="loading" class="state">불러오는 중...</div>
      <div v-else-if="error" class="state error">{{ error }}</div>

      <template v-else-if="detail">
        <div class="meta">
          <span class="pill">Route #{{ detail.id }}</span>
          <span v-if="detail.created_at" class="muted">
            {{ detail.created_at.slice(0, 10) }}
          </span>
        </div>

        <div v-if="!detail.days?.length" class="state">
          아직 일차/장소가 없습니다.
        </div>

        <div v-else class="days">
          <div v-for="day in detail.days" :key="day.id" class="day">
            <div class="day-head">
              <div class="day-title">Day {{ day.day }}</div>
              <div class="muted">{{ day.places?.length || 0 }} places</div>
            </div>

            <ul class="places">
              <li v-for="p in day.places" :key="p.id" class="place">
                <div class="left">
                  <span class="order">{{ p.order }}</span>
                  <span class="name">{{ p.name }}</span>
                </div>

                <div class="right">
                  <div v-if="p.address" class="addr">{{ p.address }}</div>
                  <div v-if="p.memo" class="memo">{{ p.memo }}</div>
                </div>
              </li>
            </ul>
          </div>
        </div>
      </template>

      <div v-else class="state">데이터가 없습니다.</div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/api/client'

const route = useRoute()
const router = useRouter()

const detail = ref(null)
const loading = ref(false)
const error = ref('')

const goBack = () => router.back()

onMounted(async () => {
  loading.value = true
  error.value = ''

  try {
    const routeId = route.params.routeId
    const { data } = await api.get(`/routes/${routeId}/`)
    detail.value = data
  } catch (e) {
    console.error(e)
    error.value = '루트 상세를 불러오지 못했습니다.'
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.page {
  max-width: 980px;
  margin: 0 auto;
  padding: 24px 0;
}

.header {
  display: flex;
  gap: 16px;
  align-items: flex-start;
  margin-bottom: 14px;
}

.header-text {
  flex: 1;
}

.title {
  margin: 0;
  font-size: 22px;
  font-weight: 800;
}

.desc {
  margin: 6px 0 0;
  color: #6b7280;
  line-height: 1.5;
}

.card {
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  background: #fff;
  padding: 14px;
}

.state {
  padding: 12px 6px;
  color: #6b7280;
}

.state.error {
  color: #dc2626;
}

.meta {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
}

.pill {
  font-size: 12px;
  padding: 6px 10px;
  border-radius: 999px;
  border: 1px solid #e5e7eb;
  background: #f9fafb;
}

.muted {
  color: #6b7280;
  font-size: 13px;
}

.days {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.day {
  border: 1px solid #f1f5f9;
  border-radius: 12px;
  padding: 12px;
  background: #fafafa;
}

.day-head {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 10px;
}

.day-title {
  font-weight: 800;
}

.places {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.place {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  padding: 10px;
  border: 1px solid #e5e7eb;
  background: #fff;
  border-radius: 10px;
}

.left {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 220px;
}

.order {
  width: 26px;
  height: 26px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  background: #f3f4f6;
  font-weight: 800;
  font-size: 13px;
}

.name {
  font-weight: 700;
}

.right {
  text-align: right;
  font-size: 13px;
  color: #6b7280;
}

.addr {
  margin-bottom: 2px;
}

.memo {
  color: #9ca3af;
}

.btn {
  border-radius: 10px;
  padding: 8px 12px;
  cursor: pointer;
  font-weight: 600;
}

.btn-ghost {
  border: 1px solid #e5e7eb;
  background: #fff;
}
</style>
