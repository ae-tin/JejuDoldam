<template>
  <div ref="el" class="map"></div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { loadKakao } from '@/utils/loadKakao'

const props = defineProps({
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

  const valid = (places || []).filter(p => p.latitude != null && p.longitude != null)

  if (!valid.length) return

  const bounds = new window.kakao.maps.LatLngBounds()
  const path = []

  for (const [index, p] of valid.entries()) {
    const lat = Number(p.latitude)
    const lng = Number(p.longitude)
    const pos = new window.kakao.maps.LatLng(lat, lng)

    bounds.extend(pos)
    path.push(pos)

    let order = p.order || (index + 1)
    if (order > 20) order = 20 

    // public 폴더 사용 권장 (혹은 기존 import.meta.url 방식 유지)
    const imageSrc = new URL(`../marker/marker-${order}.png`, import.meta.url).href
    
    const imageSize = new window.kakao.maps.Size(30, 45)
    const markerImage = new window.kakao.maps.MarkerImage(imageSrc, imageSize)

    const marker = new window.kakao.maps.Marker({
      position: pos,
      image: markerImage, 
      zIndex: 100 - index 
    })

    marker.setMap(map)
    markers.push(marker)
  }

  polyline = new window.kakao.maps.Polyline({
    path,
    strokeWeight: 4,
    strokeOpacity: 0.8,
    strokeStyle: 'solid',
    strokeColor: '#333333' 
  })
  polyline.setMap(map)

  // // [중요] 1번 장소를 중심으로 하고 싶다면:
  // // 방법 A: 모든 마커가 다 보이게 자동 조정 (추천)
  // map.setBounds(bounds)

  // 방법 B: 무조건 1번 장소가 지도의 정중앙 (나머지 마커가 잘릴 수 있음)
  if (valid.length > 0) {
    const firstPos = new window.kakao.maps.LatLng(valid[0].latitude, valid[0].longitude);
    map.setCenter(firstPos);
  }
}

onMounted(async () => {
  await loadKakao()

  // 1. 초기 로딩 시 사용할 "안전한 기본 좌표" (제주도 중간 or 서울 등)
  // props.places가 비어있을 수도 있기 때문에 여기서 props를 참조하는 것은 위험할 수 있습니다.
  const defaultLat = 33.3617
  const defaultLng = 126.5292

  // 2. 일단 기본 좌표로 지도를 생성합니다. (에러 방지)
  map = new window.kakao.maps.Map(el.value, {
    center: new window.kakao.maps.LatLng(defaultLat, defaultLng),
    level: 7, // 초기 레벨
  })

  // 3. 지도가 만들어진 후 draw를 호출하면, 
  // draw 함수 안에서 데이터 좌표를 읽어 map.setBounds()가 실행되므로
  // 자연스럽게 1번 장소(혹은 전체 경로) 쪽으로 시점이 이동합니다.
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
