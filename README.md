<img width="2752" height="1536" alt="Gemini_Generated_Image_p3larap3larap3la" src="https://github.com/user-attachments/assets/cef62d7a-e977-42db-a74d-40a032dbdefc" />


### 📓 프로젝트 개요

- 설명 : AI 기반 제주도 여행 경로추천 서비스
- 기간 : 2025.12.08(월) ~ 2025.12.24(수)

### 🦝 서비스 특징

- 회원 정보와, 원하는 여행 스타일에 기반하여 군집화를 통한 맞춤 여행 경로를 추천함

### ⚙ 주요 기능

- 사용자 맞춤 여행 경로 생성
- AI가 추천해준 경로를 편집하여 더욱 개인화된 여행 경로 생성 가능
- 커뮤니티 기능을 통해 다른 사람의 경로를 참고하거나 자신의 루트를 공유 가능
- 추천 경로, 저장한 경로의 장소 사진 및 카카오맵 링크를 통해 상세 정보 확인 가능
- 대중적으로 참고하면 좋을만한 여행 경로를 메인 페이지에서 제공

### 🦾 팀 소개

- 강태인 [AI/Data/AI_server]
  
- 김종민 [Backend/Frontend]
  

## 🛒 기술 스택

---
### Backend
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)  ![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white)  ![DjangoREST](https://img.shields.io/badge/DJANGO-REST-ff1709?style=for-the-badge&logo=django&logoColor=white&color=ff1709&labelColor=gray)  ![SQLite](https://img.shields.io/badge/sqlite-%2307405e.svg?style=for-the-badge&logo=sqlite&logoColor=white)  ![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)  ![JWT](https://img.shields.io/badge/JWT-black?style=for-the-badge&logo=JSON%20web%20tokens)
### Frontend
![JavaScript](https://img.shields.io/badge/javascript-%23323330.svg?style=for-the-badge&logo=javascript&logoColor=%23F7DF1E)  ![Vue.js](https://img.shields.io/badge/vuejs-%2335495e.svg?style=for-the-badge&logo=vuedotjs&logoColor=%234FC08D)  ![Vite](https://img.shields.io/badge/vite-%23646CFF.svg?style=for-the-badge&logo=vite&logoColor=white) 
### AI
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
나머지는 추가 예정
### DevOps
![Git](https://img.shields.io/badge/git-%23F05033.svg?style=for-the-badge&logo=git&logoColor=white)  ![GitHub](https://img.shields.io/badge/github-%23121011.svg?style=for-the-badge&logo=github&logoColor=white)
### Tools
![Notion](https://img.shields.io/badge/Notion-%23000000.svg?style=for-the-badge&logo=notion&logoColor=white)  ![Visual Studio Code](https://img.shields.io/badge/Visual%20Studio%20Code-0078d7.svg?style=for-the-badge&logo=visual-studio-code&logoColor=white)  ![Postman](https://img.shields.io/badge/Postman-FF6C37?style=for-the-badge&logo=postman&logoColor=white)  ![Figma](https://img.shields.io/badge/figma-%23F24E1E.svg?style=for-the-badge&logo=figma&logoColor=white)

## 🔧 개발 환경

---

Backend

- Django 5.2.8
- DRF 3.16.1

Frontend

- Vue.js 3.5.26

## 💿 프로젝트 폴더 구조

---
```swift
JejuDoldam/
│
├── AI/ # AI 관련 서버 및 모델 디렉토리
│ ├── place_recommend/ # 장소 추천 AI 서버 (FastAPI)
│ │ ├── __pycache__/
│ │ ├── dataset/ # 장소 추천 모델용 데이터셋
│ │ │ ├── test/
│ │ │ ├── test_data.csv
│ │ │ ├── train_data.csv
│ │ │ └── user_interactions.csv
│ │ ├── models/ # 학습된 LightFM 모델 파일
│ │ │ └── place_recommender.pkl
│ │ ├── fastapi_place.py # 장소 추천 FastAPI 서버 실행 파일
│ │ ├── place_recommender_train.py # 장소 추천 모델 학습 스크립트
│ │ ├── requirements.txt # AI 서버 의존성 목록
│ │ └── test.py # 모델 테스트 스크립트
│ │
│ └── route_recommend/ # 경로 추천 AI 서버 (FastAPI)
│ ├── __pycache__/
│ ├── data/ # 경로 추천 모델용 데이터셋
│ │ ├── Jeju_Doldam_Data.csv
│ │ ├── Jeju_Doldam_Log_Data.csv
│ │ └── Jeju_Doldam_Place_Data.csv
│ ├── models/ # 학습된 클러스터링 모델 파일
│ │ ├── kmeans_model.pkl
│ │ └── kproto_model.pkl
│ ├── fastapi_route.py # 경로 추천 FastAPI 서버 실행 파일
│ ├── requirements.txt # AI 서버 의존성 목록
│ ├── route_recommender.py # 경로 추천 로직 구현 파일
│ └── route_recommender_train.py # 경로 추천 모델 학습 스크립트
│
├── BE/ # 백엔드 서버 디렉토리 (Django)
│ ├── accounts/ # 사용자 인증 및 관리 앱
│ │ ├── __pycache__/
│ │ ├── migrations/
│ │ ├── admin.py
│ │ ├── apps.py
│ │ ├── models.py
│ │ ├── serializers.py
│ │ ├── tests.py
│ │ ├── urls.py
│ │ └── views.py
│ ├── config/ # Django 프로젝트 설정 디렉토리
│ │ ├── __pycache__/
│ │ ├── __init__.py
│ │ ├── asgi.py
│ │ ├── settings.py
│ │ ├── urls.py
│ │ └── wsgi.py
│ ├── posts/ # 게시글 커뮤니티 앱
│ │ ├── __pycache__/
│ │ ├── migrations/
│ │ ├── admin.py
│ │ ├── apps.py
│ │ ├── models.py
│ │ ├── serializers.py
│ │ ├── tests.py
│ │ ├── urls.py
│ │ └── views.py
│ ├── routes/ # 경로 생성 및 관리 앱 (AI 연동 포함)
│ │ ├── __pycache__/
│ │ ├── migrations/
│ │ ├── admin.py
│ │ ├── apps.py
│ │ ├── models.py
│ │ ├── serializers.py
│ │ ├── tests.py
│ │ ├── urls.py
│ │ └── views.py
│ ├── .env.example # 백엔드 환경변수 예시 파일
│ ├── .gitignore
│ ├── db.sqlite3 # 로컬 개발용 SQLite DB 파일
│ ├── manage.py # Django 관리 커맨드 스크립트
│ └── requirements.txt # 백엔드 의존성 목록
│
└── FE/ # 프론트엔드 디렉토리 (Vue.js)
 ├── node_modules/
 ├── public/
 │ └── favicon.ico
 ├── src/
 │ ├── api/ # Axios 인스턴스 및 API 호출 함수
 │ │ └── client.js
 │ ├── assets/ # 정적 리소스 (이미지, CSS 등)
 │ │ ├── base.css
 │ │ ├── logo.svg
 │ │ └── main.css
 │ ├── components/ # 재사용 가능한 Vue 컴포넌트
 │ │ ├── common/
 │ │ ├── posts/
 │ │ └── routes/
 │ ├── router/ # Vue Router 설정
 │ │ └── index.js
 │ ├── stores/ # Pinia 상태 관리 스토어
 │ │ ├── auth.js
 │ │ └── route.js
 │ ├── views/ # 페이지 단위 Vue 컴포넌트
 │ │ ├── HomeView.vue
 │ │ ├── LoginView.vue
 │ │ ├── MyPageView.vue
 │ │ ├── PostCreateView.vue
 │ │ ├── PostDetailView.vue
 │ │ ├── PostListView.vue
 │ │ ├── RouteConfirmView.vue
 │ │ ├── RouteCreateView.vue
 │ │ ├── RouteEditView.vue
 │ │ └── SignupView.vue
 │ ├── App.vue # 루트 Vue 컴포넌트
 │ └── main.js # Vue 앱 진입점
 ├── .env.example # 프론트엔드 환경변수 예시 파일
 ├── .gitignore
 ├── index.html # 프론트엔드 진입 HTML 파일
 ├── jsconfig.json
 ├── package-lock.json
 ├── package.json # 프론트엔드 의존성 목록 및 스크립트
 ├── README.md
 └── vite.config.js # Vite 빌드 도구 설정
```

## 🖨 ERD

---

깃허브 웹에서 수정

### 🖱 코드 컨벤션
---
https://github.com/ae-tin/JejuDoldam/wiki/Code-Convention

## 🔈 기능 시연 상세

---
