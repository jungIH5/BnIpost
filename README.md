# BnIpost

키워드나 사진 하나로 네이버 블로그·인스타그램 게시물을 AI가 자동 생성·게시하는 웹 서비스입니다.

---

## 아키텍처

```
┌─────────────────────────────────────────────┐
│              Docker Compose                  │
│                                             │
│  [Frontend]     [Java]      [Python]        │
│  Next.js    →  Spring   →  FastAPI          │
│  :3000      ←  Boot     ←  + LangGraph      │
│                :8080        :8000            │
│                  ↕              ↕            │
│           [PostgreSQL]     [Redis]           │
│              :5432          :6379            │
└─────────────────────────────────────────────┘
```

| 서비스 | 역할 | 기술 |
|--------|------|------|
| **Frontend** | UI 렌더링 | Next.js 14, TypeScript, Tailwind CSS |
| **Java Server** | 회원관리, OAuth | Spring Boot 3, Spring Security, JWT |
| **Python Server** | AI 워크플로우 | FastAPI, LangGraph, Claude API |
| **PostgreSQL** | 데이터 저장 | PostgreSQL 16 |
| **Redis** | 캐싱 | Redis 7 |

---

## LangGraph 워크플로우

```
START
  ↓
[parse_input]      → 입력 타입 판별 (키워드/이미지) + 소셜 토큰 조회
  ↓ (이미지인 경우)
[analyze_image]    → Claude Vision으로 이미지 분석
  ↓
[generate_content] → Claude로 플랫폼 최적화 콘텐츠 생성
  ↓
[quality_checker]  → 품질 검증 (규칙 기반 + AI 평가) / 최대 3회 재시도
  ↓ (통과 시)
[post_publisher]   → 네이버 블로그 / 인스타그램 API 게시
  ↓
[history_saver]    → DB에 결과 저장
  ↓
END
```

---

## 시작하기

### 사전 준비

다음 API 키가 필요합니다:

| API | 획득 방법 |
|-----|-----------|
| **Naver Client ID/Secret** | [네이버 개발자 센터](https://developers.naver.com) → 앱 등록 → 네이버 로그인, 블로그 API 추가 |
| **Meta App ID/Secret** | [Meta 개발자 콘솔](https://developers.facebook.com) → 앱 생성 → Instagram Graph API 추가 (비즈니스 계정 필수) |
| **Anthropic API Key** | [Anthropic Console](https://console.anthropic.com) |

### 설치 및 실행

```bash
# 1. 저장소 클론
git clone https://github.com/YOUR_GITHUB_USERNAME/BnIpost.git
cd BnIpost

# 2. 환경 변수 설정
cp .env.example .env
# .env 파일을 열어 실제 API 키 입력

# 3. Docker로 전체 서비스 실행
docker compose up --build

# 4. 브라우저에서 접속
# http://localhost:3000
```

### 개별 서비스 개발 시

```bash
# Java 서버만
cd java-server && mvn spring-boot:run

# Python 서버만
cd python-server && uvicorn app.main:app --reload --port 8000

# Frontend만
cd frontend && npm install && npm run dev
```

---

## API 엔드포인트

### Java Server (`:8080`)

| Method | Path | 설명 |
|--------|------|------|
| GET | `/health` | 헬스체크 |
| GET | `/auth/naver` | 네이버 OAuth 시작 |
| GET | `/auth/naver/callback` | 네이버 OAuth 콜백 |
| GET | `/auth/instagram` | 인스타그램 OAuth 시작 |
| GET | `/auth/instagram/callback` | 인스타그램 OAuth 콜백 |
| GET | `/api/users/me` | 내 프로필 조회 (JWT 필요) |
| GET | `/api/users/internal/token` | 소셜 토큰 조회 (내부 통신용) |

### Python Server (`:8000`)

| Method | Path | 설명 |
|--------|------|------|
| GET | `/health` | 헬스체크 |
| POST | `/api/posts/generate` | 게시물 생성 + 게시 (JWT 필요) |
| POST | `/api/posts/preview` | 게시물 미리보기 (게시 안 함) |
| GET | `/api/history/` | 게시 이력 조회 (JWT 필요) |

---

## 환경 변수

`.env.example` 파일을 참고하세요. 필수 항목:

```
DB_PASSWORD         # DB 비밀번호
JWT_SECRET          # JWT 서명 키 (32자 이상)
NAVER_CLIENT_ID     # 네이버 앱 클라이언트 ID
NAVER_CLIENT_SECRET # 네이버 앱 시크릿
META_APP_ID         # Meta 앱 ID
META_APP_SECRET     # Meta 앱 시크릿
ANTHROPIC_API_KEY   # Claude API 키
```

---

## 주의사항

- **인스타그램**: 일반 개인 계정으로는 게시 API 사용 불가. **비즈니스 또는 크리에이터 계정** 전환 후 Facebook 페이지 연동 필요.
- **네이버 블로그 API**: 네이버 개발자 센터에서 앱 등록 후 `블로그` API 권한 추가 필요.
- **Claude API**: `claude-sonnet-4-6` (콘텐츠 생성), `claude-haiku-4-5-20251001` (품질 검증)을 사용합니다.

---

## 프로젝트 구조

```
BnIpost/
├── docker-compose.yml
├── .env.example
├── .gitignore
├── db/
│   └── init.sql
├── java-server/          # Spring Boot (Auth)
│   ├── Dockerfile
│   ├── pom.xml
│   └── src/main/java/com/bnipost/
│       ├── config/       # Security, CORS, Bean 설정
│       ├── controller/   # Auth, User, Health API
│       ├── entity/       # User 엔티티
│       ├── filter/       # JWT 인증 필터
│       ├── repository/   # JPA Repository
│       ├── service/      # OAuth, User 서비스
│       └── util/         # JWT 유틸리티
├── python-server/        # FastAPI + LangGraph (AI)
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── auth/         # JWT 검증
│       ├── graph/        # LangGraph 워크플로우
│       │   ├── state.py  # 상태 타입 정의
│       │   ├── workflow.py # 그래프 구성
│       │   └── nodes/    # 각 노드 구현
│       ├── models/       # SQLAlchemy 모델
│       ├── routers/      # FastAPI 라우터
│       └── services/     # Naver, Instagram API
└── frontend/             # Next.js (UI)
    ├── Dockerfile
    └── src/
        ├── app/          # Next.js App Router 페이지
        ├── components/   # 재사용 컴포넌트
        ├── lib/          # API 클라이언트, 인증 유틸
        └── types/        # TypeScript 타입 정의
```
