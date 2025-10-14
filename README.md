# 목차

1. [과제 목표 및 문제 정의](#과제-목표-및-문제-정의)
2. [접근 방식 및 시스템 구성도](#접근-방식-및-시스템-구성도)
2. [기술적 선택 이유](#기술적-선택-이유)
3. [주요 기능](#주요-기능)
4. [디렉토리 구조](#디렉토리-구조)
5. [실행 방법](#실행-방법)
6. [결과 예시](#결과-예시)
7. [개선 아이디어](#개선-아이디어)


## 과제 목표 및 문제 정의

프로젝트의 목표는 **각각의 PDF에 포함된 여러 블로그 포스트를 자동으로 분리·정제하고, 요약 및 메타데이터를 구조화하여 적재한 뒤 이를 활용해 블로그 콘텐츠 생성 과정을 자동화하는 시스템**을 구축하는 것입니다.

기존에는 하나의 PDF 안에 여러 포스트가 섞여 있어  
- 수작업으로 텍스트를 추출해야 하고,  
- 요약, 리라이팅, 썸네일 제작 등의 과정을 개별적으로 수행해야 하는 비효율이 있었습니다.




## 접근 방식 및 시스템 구성도

### 접근 방식 (Approach)

이를 해결하기 위해,  
> **“PDF 업로드 → 포스트 단위 분리 → 텍스트 정제 → 요약 → 데이터 적재”**  
까지의 과정을 자동화한 **로컬 기반 ETL 파이프라인**을 구현했습니다.

파이프라인은 FastAPI 환경에서 실행되며  
- **PDF 업로드 시 자동으로 포스트 단위 분리 및 정제**,  
- **추후 콘텐츠 생성을 위한 요약(마크다운/간략 요약)**,  
- **결과 데이터를 PostgreSQL(DB 컨테이너) 및 로컬 스토리지(`uploads/`)에 적재**하도록 구성되어 있습니다.

---

### 데이터 적재 구조

모든 처리 결과는 **PostgreSQL 컨테이너**에 메타데이터로 저장되고,  
본문·이미지·요약 파일은 **로컬 컨테이너 내 `uploads/` 디렉토리**에 보존됩니다.

| 테이블 | 역할 |
|--------|------|
| **RawPdf** | 업로드된 원본 PDF 정보 |
| **SplitPost** | PDF에서 분리된 개별 포스트 단위 |
| **RefinedPost** | 정제 및 요약된 포스트 데이터 |

<p>
  <img src="./images/스크린샷 2025-10-14 오후 9.39.40.png" alt="ERD 스크린샷" width="600"/>
</p>

데이터베이스에는 위 3단계 구조로 각 처리 결과가 기록되며,  
로컬 저장소(`uploads/raw_pdf`, `uploads/split_posts`, `uploads/refined_posts`)에는 실제 파일이 계층적으로 저장됩니다.

특히 `uploads/refined_posts` 디렉터리에는 각 블로그 포스트가  
아래와 같이 **JSON 형식으로 구조화**되어 저장됩니다.  
이 파일에는 제목(`title`), 작성자(`author`), 작성일(`date`), 원문 URL(`url`), 본문 내용(`body`) 등이 포함되며,  
추가적으로 추출된 이미지 파일들도 함께 저장됩니다.

<p>
  <img src="./images/스크린샷 2025-10-14 오후 9.48.10.png" alt="포스팅 파싱 스크린샷" width="600"/>
</p>


### ETL 파이프라인 개요

#### 데이터 수집 (Extract)
- 업로드된 PDF를 `pdfminer`로 HTML로 변환  
- `<a name="n">Page n</a>` 패턴을 기준으로 페이지 맵(`page_map`) 구성  
- 정규표현식을 활용해 포스트 시작 페이지를 탐지하고,  
  각 포스트의 페이지 범위(`post_ranges`)를 자동 산출

#### 데이터 변환 (Transform)
- 감지된 범위별로 PDF를 분리한 뒤 `BeautifulSoup`으로 텍스트 추출 및 병합  
- 작성자, 날짜, URL 등의 메타데이터를 파싱  
- `fitz(PyMuPDF)`로 링크와 겹치지 않는 이미지만 추출하여 저장  
- 반복 문구나 지저분한 텍스트를 제거하여 정제(Clean) 단계 수행함 
- 결과를 **포스트 단위 JSON** 형태로 저장

#### 데이터 적재 및 응용(Load)
- 정제된 JSON 및 이미지 경로를 DB와 파일 시스템에 적재  
- 이후 **OpenAI API**를 이용하여 다음을 수행:
  - 마크다운 형식을 변환한 pdf 요약문 자동 생성  
  - 제목·본문 기반 썸네일 이미지 생성  
  - 지정 기간(`start_date ~ end_date`)별 인사이트 리포트(pdf) 생성  


## 기술적 선택 이유

#### FastAPI
- **확장성**: API 기반 구조로, 웹 대시보드·자동 배치·외부 연동 등으로 확장 용이
- **비동기 I/O**: PDF 파싱·AI 요청을 병렬화하여 응답 속도 향상  
- **유지보수성**: `Service / Repository / Schema` 계층으로 모듈화된 구조

#### OpenAI API
- **품질 및 안정성**: Groq, Stable Diffusion 등 오픈 api 및 모델을 사용하려고 했으나 품질 및 속도가 느림
- **로컬 모델 한계 보완**: 오픈 소스 생성형 모델을 서빙하기에 리소스가 부족했음

---

### 사전 요약(Markdown) 저장 설계 배경

OpenAI API로 생성된 요약문은  
Markdown 형태로 db 저장되며,  
핵심 키워드 기반 요약 컬럼을 함께 DB에 미리 적재합니다.

이 설계에는 명확한 트레이드오프가 존재합니다.

| 항목 | 선택 이유 | 단점 |
|------|------------|------|
| **사전 생성(Precompute)** | 업로드 시 한 번에 요약 및 저장 → 이후 조회 시 즉시 응답 | 초기 업로드 시간이 다소 길어짐 |
| **요청 시 생성(On-demand)** | 저장 공간 절약, 최신 모델 반영 가능 | 호출 시마다 OpenAI 응답 대기(지연) 발생 |

따라서 본 프로젝트에서 **더 빠른 응답형 콘텐츠 생성 흐름**(사용자에게 요약·리라이팅·리포트·이미지 자동화)을 지원하기 위해  
**사전 생성(Precompute) 방식**을 채택했습니다.

## 주요 기능

### Files
- `POST /files/upload/pdf` — 단일 PDF 업로드 및 자동 분리
- `POST /files/upload/pdf/multi` — 다중 PDF 업로드 처리
- `GET /files/` — 업로드된 파일 및 정제 결과 목록 조회(id = post_id 조회)
- `DELETE /files/truncate/all` — 업로드 및 처리된 모든 데이터 초기화


### Thumbnails
- `GET /thumbnails/download/{post_id}` — 포스트별 자동 생성 썸네일 이미지 다운로드


### Summaries
- `GET /summaries/download/{post_id}` — 포스트 요약문을 PDF로 다운로드


### Period Report
- `GET /period-report/` — 지정된 기간(start_date~end_date)의 인사이트 리포트 PDF 다운로드



## 디렉토리 구조

<p>
  <img src="./images/스크린샷 2025-10-14 오후 10.05.17.png" alt="디렉토리 스크린샷" width="600"/>
</p>


## 실행 방법

### 1. 프로젝트 클론

```bash
git clone https://github.com/your-username/blog-content-automation.git
cd blog-content-automation
```

### 2. 환경 변수 설정 (.env)
프로젝트 루트에 .env 파일을 반드시 생성해야 함.

```bash
# .env 예시
DB_USER=
DB_PASSWORD=
DB_DATABASE=
DB_HOST=
DB_PORT=

DB_POOL_SIZE=
DB_MAX_OVERFLOW=
DB_POOL_TIMEOUT=
DB_POOL_RECYCLE=

ENVIRONMENT=
PROJECT_NAME=
CORS_ORIGINS_RAW=

OPENAI_API_KEY=
```

### 3. Docker Compose 실행
아래 명령어로 FastAPI, PostgreSQL, pgAdmin 서비스를 한 번에 실행합니다.

```bash
# 이미지 빌드 및 컨테이너 실행
docker compose up -d --build
```


### 4. 서비스 접속 경로
| 서비스 | 설명 | 주소 |
|:--------|:-------------------------------|:-----------------------------|
| **FastAPI** | 블로그 자동화 API 서버 | [http://localhost:8000/docs](http://localhost:8000/docs) |
| **pgAdmin4** | 데이터베이스 관리 대시보드 | [http://localhost:5050](http://localhost:5050) |

---

### pgAdmin 기본 계정

| 항목 | 값 |
|:------|:----------------|
| **ID** | `admin@local.com` |
| **PW** | `admin1234` |

> 💡 **참고:**  
> pgAdmin에서 PostgreSQL 접속 시 필요한 **Host**, **Port**, **Database**, **User**, **Password** 정보는  
> 프로젝트 루트의 `.env` 파일을 참고하세요.


## 결과 예시

### 1. PDF 업로드 및 리스트 확인
<p>
  <img src="./images/스크린샷 2025-10-14 오후 11.01.54.png" alt="업로드 스크린샷 1" height="300">
  <img src="./images/스크린샷 2025-10-14 오후 11.03.50.png" alt="업로드 스크린샷 2" height="300">
</p>

### 2. 포스팅 정제 결과
<p>
  <img src="./images/스크린샷 2025-10-14 오후 11.08.43.png" alt="DB 스크린샷 1" height="300">
</p>
> 분리된 각 포스트를 자동으로 텍스트 정제 및 요약

### 3. 요약 / 리라이팅
<p>
  <img src="./images/스크린샷 2025-10-14 오후 11.19.59.png" alt="요약 리라이팅 스크린샷 1" height="300">
</p>
> 기존 포스트를 짧게 요약하거나 최신 문체로 재작성

### 4. 썸네일 이미지 자동 생성
<p>
  <img src="./images/thumbnail_2025_10_14_23_13.png" alt="썸네일 스크린샷 1" height="300">
</p>
> 제목 및 본문을 기반으로 AI를 활용해 자동으로 생성된 썸네일입니다.


### 5. 기간별 리포트 PDF
<p>
  <img src="./images/스크린샷 2025-10-14 오후 11.28.10.png" alt="콘텐츠 기간별 스크린샷 1" height="300">
</p>
> 지정한 기간 내의 포스트 요약을 기반으로 자동 생성된 콘텐츠 큐레이션 리포트 입니다.


## 개선 아이디어
# 추후 작성 예정