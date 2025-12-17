<template>
  <div ref="el" class="map"></div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { loadKakao } from '@/utils/loadKakao'

const props = defineProps({
  // [{ name, latitude, longitude, order }]
  places: { type: Array, default: () => [] },
})

const el = ref(null)

let map = null
let markers = []
let polyline = null

function clearOverlays() {
  for (const m of markers) m.setMap(null)
  markers = []
  if (polyline) {
    polyline.setMap(null)
    polyline = null
  }
}

function draw(places) {
  if (!map) return

  clearOverlays()

  // 좌표 있는 애들만
  const valid = (places || []).filter(p => p.latitude != null && p.longitude != null)

  if (!valid.length) return

  const bounds = new window.kakao.maps.LatLngBounds()
  const path = []

  for (const p of valid) {
    const lat = Number(p.latitude)
    const lng = Number(p.longitude)
    const pos = new window.kakao.maps.LatLng(lat, lng)

    bounds.extend(pos)
    path.push(pos)

    const marker = new window.kakao.maps.Marker({ position: pos })
    marker.setMap(map)
    markers.push(marker)
  }

  // 동선(폴리라인)
  polyline = new window.kakao.maps.Polyline({
    path,
    strokeWeight: 4,
    strokeOpacity: 0.8,
    strokeStyle: 'solid',
  })
  polyline.setMap(map)

  map.setBounds(bounds)
}

onMounted(async () => {
  await loadKakao()

  map = new window.kakao.maps.Map(el.value, {
    center: new window.kakao.maps.LatLng(33.3617, 126.5292), // 제주 대충 중앙
    level: 9,
  })

  draw(props.places)
})

watch(
  () => props.places,
  (v) => draw(v),
  { deep: true }
)
</script>

<style scoped>
.map {
  width: 100%;
  height: 420px;
  border: 1px solid #eee;
  border-radius: 12px;
}
</style>
