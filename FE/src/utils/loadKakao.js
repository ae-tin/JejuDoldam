let kakaoPromise = null

export function loadKakao() {
  if (window.kakao?.maps) return Promise.resolve(window.kakao)
  if (kakaoPromise) return kakaoPromise

  const appkey = import.meta.env.VITE_KAKAO_MAP_APP_KEY
  if (!appkey) return Promise.reject(new Error('VITE_KAKAO_JS_KEY가 없습니다. (.env 확인)'))

  kakaoPromise = new Promise((resolve, reject) => {
    const existing = document.getElementById('kakao-map-sdk')
    if (existing) {
      existing.addEventListener('load', () => {
        window.kakao.maps.load(() => resolve(window.kakao))
      })
      existing.addEventListener('error', reject)
      return
    }

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
