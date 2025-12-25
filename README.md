<img width="2752" height="1536" alt="Gemini_Generated_Image_p3larap3larap3la" src="https://github.com/user-attachments/assets/cef62d7a-e977-42db-a74d-40a032dbdefc" />


### 📓 프로젝트 개요

- 설명 : AI 기반 제주도 여행 경로추천 서비스
- 기간 : 2025.12.08(월) ~ 2025.12.25(목)

### 🦝 서비스 특징

- 회원 정보와, 원하는 여행 스타일에 기반하여 군집화를 통한 맞춤 여행 경로를 추천함

### ⚙ 주요 기능

- 사용자 맞춤 여행 경로 생성
- AI가 추천해준 경로를 편집하여 더욱 개인화된 여행 경로 생성 가능
- 커뮤니티 기능을 통해 다른 사람의 경로를 참고하거나 자신의 루트를 공유 가능
- 추천 경로, 저장한 경로의 장소 사진 및 카카오맵 링크를 통해 상세 정보 확인 가능
- 대중적으로 참고하면 좋을만한 여행 경로를 메인 페이지에서 제공

### 🦾 팀 소개

- 강태인 [AI/Data/Deployment]
  
- 김종민 [Backend/Frontend]
  
---

## 🛒 기술 스택

### Backend
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)  ![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white)  ![DjangoREST](https://img.shields.io/badge/DJANGO-REST-ff1709?style=for-the-badge&logo=django&logoColor=white&color=ff1709&labelColor=gray)  ![SQLite](https://img.shields.io/badge/sqlite-%2307405e.svg?style=for-the-badge&logo=sqlite&logoColor=white)  ![JWT](https://img.shields.io/badge/JWT-black?style=for-the-badge&logo=JSON%20web%20tokens)
### Frontend
![JavaScript](https://img.shields.io/badge/javascript-%23323330.svg?style=for-the-badge&logo=javascript&logoColor=%23F7DF1E)  ![Vue.js](https://img.shields.io/badge/vuejs-%2335495e.svg?style=for-the-badge&logo=vuedotjs&logoColor=%234FC08D)  ![Vite](https://img.shields.io/badge/vite-%23646CFF.svg?style=for-the-badge&logo=vite&logoColor=white) 
### AI
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi) ![scikit-learn](https://img.shields.io/badge/scikit--learn-%23F7931E.svg?style=for-the-badge&logo=scikit-learn&logoColor=white) ![Pandas](https://img.shields.io/badge/pandas-%23150458.svg?style=for-the-badge&logo=pandas&logoColor=white)

### DevOps
![Git](https://img.shields.io/badge/git-%23F05033.svg?style=for-the-badge&logo=git&logoColor=white)  ![GitHub](https://img.shields.io/badge/github-%23121011.svg?style=for-the-badge&logo=github&logoColor=white)
### Tools
![Notion](https://img.shields.io/badge/Notion-%23000000.svg?style=for-the-badge&logo=notion&logoColor=white)  ![Visual Studio Code](https://img.shields.io/badge/Visual%20Studio%20Code-0078d7.svg?style=for-the-badge&logo=visual-studio-code&logoColor=white)  ![Postman](https://img.shields.io/badge/Postman-FF6C37?style=for-the-badge&logo=postman&logoColor=white)  ![Figma](https://img.shields.io/badge/figma-%23F24E1E.svg?style=for-the-badge&logo=figma&logoColor=white)

### Deployment
![AWS](https://img.shields.io/badge/AWS-%23FF9900.svg?style=for-the-badge&logo=amazon-aws&logoColor=white) ![Nginx](https://img.shields.io/badge/nginx-%23009639.svg?style=for-the-badge&logo=nginx&logoColor=white) ![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)

---

## 🔧 개발 환경

### Backend

- Django 5.2.8
- DRF 3.16.1

### Frontend

- Vue.js 3.5.26

### AI
- python 3.11 for route recommend system
- python 3.9 for place recommend system

---

## 📂 프로젝트 구조 (Project Structure)
### 🤖 AI: Recommendation Engines (FastAPI)
사용자의 성향을 분석하여 최적의 장소와 경로를 제안하는 독립 서버입니다.

place_recommend/: 기존 여행자들의 여행 장소 평가 데이터를 학습하여 서비스 사용자의 인구통계학적 특성을 바탕으로 한 장소 추천 AI 서버입니다.

route_recommend/: 서비스 사용자의 성향을 파악하고 이와 유사한 여행자의 GPS 이동 데이터를 분석하여 여행 경로를 생성하는 추천 AI 서버입니다.

### ⚙️ BE: Backend (Django REST Framework)
서비스 데이터 관리 및 AI 서버와의 통신을 담당하는 핵심 API 서버입니다.

accounts/: JWT, OAuth 기반의 회원 인증 및 프로필 정보를 관리합니다.

routes/: 추천 요청 처리, 경로 편집 및 Route > Day > Place 구조의 데이터를 일괄 저장합니다.

posts/: 사용자 간 여행 루트를 공유하고 소통할 수 있는 커뮤니티 기능을 담당합니다.

### 💻 FE: Frontend (Vue.js 3)
사용자에게 추천 프로세스와 경로 편집 기능을 제공하는 인터페이스입니다.

src/api/: Axios 인터셉터를 통해 JWT 토큰 만료 시 자동으로 Refresh를 요청하는 클라이언트를 포함합니다.

src/stores/: Pinia를 사용하여 로그인 상태 및 현재 편집 중인 여행 경로 데이터를 관리합니다.

### 🔌핵심 API 명세
1. 로그인 (JWT 발급)
사용자 인증을 통해 토큰을 발급받습니다.

`Endpoint: POST /api/v1/auth/jwt/login/`

Request Body Example:

```JSON

{
  "username": "user123",
  "password": "password123"
}
```
Response Example:
```JSON

{
  "refresh": "eyJ0eXAi...",
  "access": "eyJ0eXAi..."
}
```
2. 여행 경로 추천 (AI 연동)
사용자 조건에 맞는 3개의 추천 루트 리스트를 반환합니다.

`Endpoint: POST /api/v1/routes/recommend/`

Request Body Example:

```JSON

{
  "HOW_LONG": 3,
  "SEASON": "summer",
  "TRAVEL_STYL_1": 2,
  "TRAVEL_MOTIVE_1": 7
}
```
Response Example:
```JSON

[
  {
    "id": 1,
    "title": "동부 힐링 루트 (3일)",
    "description": "성산일출봉 중심 힐링 코스",
    "days": 3,
    "places": [
      { "day": 1, "order": 1, "name": "성산일출봉", "photo_url": "..." },
      { "day": 1, "order": 2, "name": "섭지코지", "photo_url": "..." }
    ]
  }
]
```
3. 추천 결과 확정 (DB 저장)
추천받거나 편집한 경로를 데이터베이스에 영구 저장합니다.

`Endpoint: POST /api/v1/routes/confirm/`

Request Body Example:

```JSON

{
  "title": "나의 제주 힐링 여행",
  "description": "조용한 카페 위주의 여행",
  "days": [
    {
      "day": 1,
      "places": [
        { "order": 1, "name": "함덕해수욕장", "address": "...", "latitude": 33.54, "longitude": 126.66 }
      ]
    }
  ]
}
```
`Response Status: 201 Created (저장된 Route 상세 객체 반환)`

4. 카카오 로그인 (Social Login)
카카오 OAuth 2.0을 통해 인증을 진행하고, 서비스 전용 JWT 토큰을 발급받습니다.

`Endpoint: POST /api/v1/auth/kakao/login/`

Request Body Example:

```JSON

{
  "code": "KAKAO_AUTHORIZATION_CODE_FROM_CALLBACK"
}
```
Response Example:

```JSON

{
  "access": "eyJ0eXAi...",
  "refresh": "eyJ0eXAi...",
  "is_setting": true
}
```
`is_setting`: 해당 유저의 추가 정보(성별, 연령대 등 AI 추천에 필요한 필수 데이터)가 이미 등록되어 있는지 여부를 나타냅니다. false일 경우 프로필 설정 페이지로 리다이렉트가 필요합니다.

---

## 🖨 ERD

<img width="2752" height="1536" alt="Gemini_Generated_Image_9zrzli9zrzli9zrz" src="https://github.com/user-attachments/assets/69fbeaaa-921f-4370-972e-4a221464a775" />

---

## 프로젝트 실행 순서

### 사전 준비 사항
- Python 3.11 설치
- Python 3.9 설치
- Window 11

### .env 준비
- `JejuDoldam/AI/`, `JejuDoldam/BE/`, `JejuDoldam/FE/` 경로의 .env.example 대신 .env 준비

### 터미널 4개 준비 (루트: 프로젝트 폴더)
- ai_route_recommend server
- ai_place_recommend server
- backend server
- frontend server

#### ai_route_recommend server 터미널
- `JejuDoldam/AI/route_recommend/` 경로에서 가상환경 생성 `py -3.11 -m venv venv`
- 가상환경 활성화 `source venv/Scripts/activate`
- requirements.txt 설치 `pip install -r cluster_requirements.txt`
- 서버 켜기 `uvicorn fastapi_route:app --port 8001 --reload`

#### ai_place_recommend server 터미널
- `JejuDoldam/AI/place_recommend/` 경로에서 가상환경 생성 `py -3.9 -m venv venv`
- 가상환경 활성화 `source venv/Scripts/activate`
- requirements.txt 설치 `pip install -r lightfm_requirements.txt`
- 서버 켜기 `uvicorn fastapi_place:app --port 8002 --reload`

#### backend server 터미널
- `JejuDoldam/BE/` 경로에서 가상환경 생성 `py -3.11 -m venv venv`
- 가상환경 활성화 `source venv/Scripts/activate`
- requirements.txt 설치 `pip install -r requirements.txt`
- migrate `python manage.py migrate`
- load fixture data `python manage.py loaddata accounts.json posts.json routes.json`
- 서버 켜기 `python manage.py runserver`

#### frontend server 터미널
- `JejuDoldam/FE/` 경로에서 가상환경 생성 `py -3.11 -m venv venv`
- 가상환경 활성화 `source venv/Scripts/activate`
- `npm install`
- 서버 켜기 `npm run dev`

### 접속
- frontend server 터미널의 접속 경로 접속
 - default -> `http://localhost:5173/` 

---

## 🔈 기능 시연 상세
- 로그인 하지 않은 초기 랜딩 페이지
<img width="2559" height="1274" alt="image" src="https://github.com/user-attachments/assets/b2055de9-4f32-4335-bc29-a789c971370e" />

- 로그인 후 메인페이지
<img width="2559" height="1282" alt="image" src="https://github.com/user-attachments/assets/a87ce54a-85ce-4e97-b912-a435ba94d344" />

-> 대중적으로 만족도가 높을만한 경로를 메인페이지에 접속 할 때마다 3개씩 랜덤으로 추천
- 여행 스타일 입력 페이지
<img width="2557" height="1288" alt="image" src="https://github.com/user-attachments/assets/42f20941-0b80-4f4e-9af6-288ecdc627c1" />

- 여행 경로 추천 페이지
<img width="2559" height="1276" alt="image" src="https://github.com/user-attachments/assets/1facc43c-1dfb-47d3-a170-45a4ae3efdd2" />

- 저장한 경로 상세조회 페이지
차후 수정
- 커뮤니티(게시글 목록 조회)
<img width="2559" height="1277" alt="image" src="https://github.com/user-attachments/assets/28bcd03c-9776-46b2-b1c3-2f3805f28db9" />

- 커뮤니티(게시글 상세 조회)
<img width="2559" height="1283" alt="image" src="https://github.com/user-attachments/assets/6995e51e-d95f-4095-8fab-7875e95a287e" />

---

## 🖱 협업 준수 사항

- [Code Convention](https://github.com/ae-tin/JejuDoldam/wiki/Code-Convention)
- [Git branch/commit Convention](https://github.com/ae-tin/JejuDoldam/wiki/Git-Convention)

<img width="1293" height="526" alt="image" src="https://github.com/user-attachments/assets/b743eddf-767e-4693-99b5-caf1c2a5a209" />


---
