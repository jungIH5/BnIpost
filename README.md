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

## 기술 선택 이유

### Frontend — Next.js 14 + TypeScript + Tailwind CSS

| 기술 | 선택 이유 |
|------|----------|
| **Next.js 14** | App Router 기반 SSR/CSR 혼용이 가능해 OAuth 콜백 처리(서버)와 대시보드(클라이언트)를 같은 프레임워크 안에서 자연스럽게 분리할 수 있음. React 생태계에서 사실상 표준이 된 풀스택 프레임워크이며, Docker `output: standalone` 모드로 경량 프로덕션 이미지 생성이 쉬움 |
| **TypeScript** | Java·Python 백엔드의 응답 스키마를 타입으로 정의해두면 API 연동 시 런타임 오류를 컴파일 단계에서 잡을 수 있음. 프로젝트 규모가 커질수록 유지보수 비용 절감 효과가 큼 |
| **Tailwind CSS** | 클래스 기반 유틸리티 스타일링으로 별도 CSS 파일 없이 컴포넌트 안에서 디자인을 완결할 수 있어 개발 속도가 빠름. 미사용 클래스는 빌드 시 자동 제거되므로 번들 크기 최소화에도 유리함 |

### Backend — Java Spring Boot (인증 서버)

Java를 인증 전담 서버로 선택한 핵심 이유는 **보안과 생태계 성숙도**입니다.

- **Spring Security**: OAuth 2.0 Authorization Code Flow, JWT 필터 체인, CORS 정책을 선언적 설정만으로 구성할 수 있는 가장 성숙한 보안 프레임워크. 네이버·Instagram 토큰처럼 외부 인증 흐름이 복잡할수록 검증된 라이브러리가 직접 구현보다 안전함
- **Spring Data JPA + Hibernate**: 유저 엔티티와 소셜 토큰을 암호화 컬럼으로 안전하게 관리하면서도 ORM으로 SQL 작성 부담을 줄임
- **JVM 안정성**: 인증 서버는 요청이 많을수록 스레드 모델이 중요한데, Spring Boot의 내장 Tomcat + JVM은 대용량 동시 인증 요청에 검증된 성능을 보임
- **책임 분리**: 민감한 소셜 토큰(Naver Access Token, Instagram Long-lived Token)을 인증 서버에만 격리하면, Python AI 서버가 침해되어도 토큰은 Java 서버를 통해서만 조회 가능 (`X-Internal-Key` 내부 키 검증)

### Backend — Python FastAPI + LangGraph (AI 서버)

Python을 AI 워크플로우 서버로 선택한 핵심 이유는 **AI/ML 라이브러리 생태계**입니다.

- **LangGraph**: LangGraph의 공식 메인 SDK가 Python이며, 커뮤니티 레퍼런스·문서도 Python 기준으로 작성됨. JS 버전 대비 기능 완성도와 업데이트 속도가 앞서 있어 추후 기능 확장 시 유리함
- **Anthropic SDK (Python)**: Claude API의 공식 Python SDK가 가장 빠르게 최신 기능(Vision, Tool Use, Streaming 등)을 지원함
- **FastAPI**: Python 웹 프레임워크 중 가장 빠른 비동기 처리 성능을 가지며, Pydantic 기반 자동 타입 검증과 OpenAPI 문서 자동 생성을 지원함. LangGraph의 `async` 노드와 자연스럽게 결합됨
- **Pillow / 이미지 처리**: 이미지 업로드 전처리(리사이즈, 포맷 변환, base64 인코딩)에 Python 이미지 라이브러리 생태계가 압도적으로 풍부함

### 왜 Java와 Python을 함께 쓰는가

단일 언어(Python만 또는 Java만)로도 구현 가능하지만, 각 언어의 강점이 완전히 다른 영역에 있어 역할을 분리했습니다.

```
인증·보안·회원관리  →  Java가 더 강함  →  Java Spring Boot
AI 워크플로우·이미지 처리  →  Python이 더 강함  →  Python FastAPI
```

두 서버는 JWT(공유 시크릿)로 사용자 인증을 공유하고, 소셜 토큰은 내부 API 키(`X-Internal-Key`)를 통해 Java→Python 단방향으로만 전달되어 보안 경계를 유지합니다.

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
