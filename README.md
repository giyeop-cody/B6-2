# B6-2: 내가 고친 코드 설명을 AI가 대신 써주는 도우미

> Git 변경 사항을 분석해서 AI가 커밋 메시지와 PR 초안을 자동 생성하는 CLI 도구
> AI API: NVIDIA NIM (, NVIDIA NIM API Key 인증)

## 📌 과제 정보

| 항목 | 내용 |
|------|------|
| **과목** | 클라우드와 AI API |
| **난이도** | ★☆☆ (Lv.1) |
| **학습 시간** | 40분 |
| **필수 여부** | ✅ 필수 |
| **과제 번호** | 185016 |
| **언어** | Python 3.10+ |

## 🎯 프로젝트 개요

AI API를 활용해서 Git 변경 사항을 분석하고, 커밋 메시지와 PR 초안을 자동으로 생성하는 CLI 도구를 만듭니다. 민감정보 마스킹 보안 기능도 함께 구현합니다.

## 🎓 학습 목표

이 과제를 완료한 뒤, 다음을 설명할 수 있어야 한다:

1. AI API 연동 — 환경변수 기반 API Key 관리, 로컬 LLM 연결 방법
2. Git 데이터 수집 — git status, git diff로 변경 사항을 프로그램에서 읽는 방법
3. 프롬프트 설계 — diff를 AI가 이해할 수 있는 컨텍스트로 변환
4. 보안 처리 — diff에 포함된 민감정보를 마스킹하여 프롬프트에 포함하지 않는 방법
5. CLI 설계 — argparse로 명령/옵션을 처리하고 단일 실행 흐름을 설계

## ⚠️ 제약 사항

- AI API Key는 환경변수로만 관리, 하드코딩 금지
- 1회 실행 시 요청 횟수 1~2회 이내 제한 권장
- Git 변경 사항 수집은 git status, git diff 범위로 제한
- git push, GitHub PR 생성 등 원격 저장소 자동 반영 기능은 구현하지 않음
- 민감정보 마스킹 또는 diff 일부만 전송 (--safe-mode 옵션)

| **실행 환경** | 터미널 (웹 화면 없음) |

---

## 🚀 사용 방법

### NVIDIA NIM 설정 (.env 파일 사용)

1. **API Key 발급**: https://build.nvidia.com → Settings → API Keys
2. **.env 파일 생성**:
```bash
cp .env.example .env
# .env 파일을 열어서 AI_API_KEY 값을 실제 NVIDIA NIM API Key(nvapi-...)로 수정
```
3. **실행**:
```bash
python main.py commit          # 커밋 메시지 자동 생성
python main.py pr              # PR 제목/본문 자동 생성
```

> `.env` 파일은 `.gitignore`에 포함되어 GitHub에 푸시되지 않습니다.
> `python-dotenv`가 `.env` 파일을 자동으로 로딩하므로 `export` 불필요.

**또는 환경변수 직접 설정**:
```bash
export AI_API_KEY="nvapi-your_key"
python main.py commit
```

### Mock 모드 (개발/테스트용, API Key 불필요)
```bash
python main.py commit --mock   # 템플릿 기반 생성 (AI API 호출 없음)
```

### 옵션
```bash
python main.py commit --safe-mode              # 민감정보 마스킹 + diff 제한
python main.py commit --temperature 0.1        # 더 결정론적인 출력
python main.py pr --max-tokens 1000            # 더 긴 출력 허용
```

---

## 🏗️ 프로젝트 구조

```
b6-2-app/
├── main.py              # CLI 진입점 (commit/pr 명령, argparse)
├── git_collector.py     # git status/diff 수집 (GitCollector 클래스)
├── ai_client.py         # AI 클라이언트 (NVIDIA NIM API, mock 지원)
├── prompt_builder.py    # 프롬프트 템플릿 (커밋/PR용)
├── sanitizer.py         # 민감정보 마스킹 + --safe-mode
├── validator.py         # 출력 형식 자동 검증
├── .env.example         # 환경변수 예시
├── .gitignore
├── requirements.txt
└── docs/                # 추론 문서 (4개)
```

---

## ✅ 제약사항 준수

| 제약 | 준수 | 구현 |
|------|------|------|
| API Key 환경변수만 관리 | ✅ | `AI_API_KEY` env, 하드코딩 금지 |
| 1회 실행 1~2회 요청 제한 | ✅ | commit=1회, pr=1회 API 호출 |
| git status/diff 범위만 | ✅ | push/PR API 구현 안 함 |
| 초안 텍스트 출력까지 | ✅ | 터미널 출력만, 자동 반영 안 함 |
| 민감정보 마스킹 | ✅ | `sanitizer.py` (8가지 패턴) |
| --safe-mode 옵션 | ✅ | 마스킹 + 최대 10파일/200줄 |
| .env → .gitignore | ✅ | GitHub에 Key 푸시하지 않음 |

---

## 🔒 보안: 민감정보 마스킹

| 패턴 | 마스킹 예시 |
|------|------------|
| `nvapi-xxx` (NVIDIA NIM API Key) | `nvapi-***MASKED***` |
| `sk-xxx` (OpenAI API Key) | `sk-***MASKED***` |
| `ghp_xxx` (GitHub PAT) | `ghp_***MASKED***` |
| 이메일 | `***@***.***` |
| `password=xxx` | `password=***MASKED***` |
| JWT (`eyJ...`) | `***JWT_MASKED***` |

---

## 🤖 NVIDIA NIM

| 항목 | 내용 |
|------|------|
| 인증 | NVIDIA NIM API Key (nvapi-...) |
| 엔드포인트 | https://integrate.api.nvidia.com/v1/chat/completions |
| 기본 모델 | meta/llama-3.1-8b-instruct (3초 응답) |
| 무료 한도 | 1,000 credits, 40 RPM |
| 신용카드 | 불필요 |
| 모델 변경 이력 | 70b(176초 타임아웃) → 8b(3초, 65배 개선) |

### 다른 모델 사용
```bash
export AI_MODEL="Llama-3.3-70B-Instruct"   # Llama 3.3 70B
export AI_MODEL="Phi-3-medium-128k-instruct" # Phi-3
```

---

## 📋 출력 예시

### 커밋 메시지
```
[INFO] Git status 수집 완료: 3개 파일 변경 감지
[INFO] Git diff 수집 완료: 128줄
[INFO] AI API 요청 중... (model=meta/llama-3.1-8b-instruct, temperature=0.3, max_tokens=500)
[DONE] 커밋 메시지 생성 완료
[INFO] AI API 호출 횟수: 1

--- Commit Message ---
feat: Git 변경 사항 기반 커밋 메시지 자동 생성 기능 추가
----------------------
[VALIDATION] 커밋 메시지 형식 검증 통과 ✅
[INFO] 생성된 메시지는 초안입니다. 검토 후 적용하세요.
```

### API Key 미설정
```
[ERROR] AI_API_KEY 환경변수가 설정되지 않았습니다.
  예) export AI_API_KEY="nvapi-your_nvidia_nim_api_key"
  API Key 발급: https://build.nvidia.com → Settings → API Keys
```

### 변경사항 없음
```
[INFO] 변경 사항이 없습니다. 커밋 메시지를 생성하지 않고 종료합니다.
```
