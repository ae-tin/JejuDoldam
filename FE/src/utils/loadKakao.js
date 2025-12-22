// 카카오맵 SDK 로딩중일 때 상태를 추적하기 위한 객체
let kakaoPromise = null

// 카카오맵 API를 로드하고 반환하는 비동기 함수(외부에서만 호출)
export function loadKakao() {
  // 이미 로드된 카카오맵 SDK가 있는지 확인, 로드되어있다면 바로 반환
  if (window.kakao?.maps) return Promise.resolve(window.kakao)
  if (kakaoPromise) return kakaoPromise

  // 앱 키 확인
  const appkey = import.meta.env.VITE_KAKAO_MAP_APP_KEY
  if (!appkey) return Promise.reject(new Error('VITE_KAKAO_JS_KEY가 없습니다. (.env 확인)'))
  
  // 카카오맵 SDK 로드
  kakaoPromise = new Promise((resolve, reject) => {
    const existing = document.getElementById('kakao-map-sdk')
    if (existing) {
      existing.addEventListener('load', () => {
        window.kakao.maps.load(() => resolve(window.kakao))
      })
      existing.addEventListener('error', reject)
      return
    }

    // 스크립트 태그를 동적으로 삽입
    const script = document.createElement('script')
    script.id = 'kakao-map-sdk'
    script.async = true
    script.src =
  `https://dapi.kakao.com/v2/maps/sdk.js?appkey=${appkey}&autoload=false&libraries=services`

    script.onload = () => window.kakao.maps.load(() => resolve(window.kakao))
    script.onerror = reject
    document.head.appendChild(script)
  })

  return kakaoPromise
}
