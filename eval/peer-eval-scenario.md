# B6-2 동료평가 시나리오 — 학습 → 고찰 → 시도 → 수정 → 선택 → 트러블슈팅

> **과제**: 내가 고친 코드 설명을 AI가 대신 써주는 도우미 만들기
> **과목**: 클라우드와 AI API | **난이도**: ★☆☆ | **과제번호**: 185016
> **GitHub**: giyeop-cody/B6-2 | **실행**: `python main.py commit` / `python main.py pr`

---

## 1. 학습

### 1-1. AI API 연동

AI API는 외부 AI 모델의 텍스트 생성 기능을 애플리케이션에서 호출하는 방식이다. 본 프로젝트는 NVIDIA NIM(`https://integrate.api.nvidia.com/v1/chat/completions`)을 사용하며, 모델은 `meta/llama-3.1-8b-instruct`이다. 표준 `chat/completions` 형식으로 요청한다. 요청은 HTTP POST로 headers에 `Authorization: Bearer {API_KEY}`, body에 `model`, `messages`, `temperature`, `max_tokens`를 담는다.

### 1-2. 프롬프트 설계

AI가 품질 높은 결과를 내려면 프롬프트를 정교하게 설계해야 한다. 단순히 "커밋 메시지 써줘"라고 하면 막 쓴다. 본 프로젝트의 프롬프트는 4가지 요소로 구성된다:
1. **역할 부여**: "너는 시니어 개발자야"
2. **출력 양식**: Conventional Commits 형식 (`type: subject`)
3. **변경 맥락**: git diff 요약 + 변경된 파일 목록
4. **제약사항**: 제목 50자 이내, 본문은 Why/What/How to Test 구조

### 1-3. API 파라미터

| 파라미터 | 역할 | 본 프로젝트 값 | 이유 |
|----------|------|---------------|------|
| `temperature` | 창의성 vs 결정론 | 0.3 | 커밋 메시지는 정확성이 창의성보다 중요 |
| `max_tokens` | 응답 최대 길이 | 500 | 커밋 메시지는 간결해야 함, 비용 절감 |
| `top_p` | 다양성 제어 | 0.9 | 기본값 유지 |

### 1-4. Git 명령 연동

`git status`와 `git diff`의 출력을 프로그램 입력으로 사용한다. Python의 `subprocess.run()`으로 git 명령을 실행하고, 결과를 문자열로 받아 프롬프트에 포함한다. Git 변경 사항 수집은 `git status`, `git diff` 범위로 제한한다 (과제 제약사항).

### 1-5. 민감정보 마스킹

`git diff`에 API Key, 이메일, 비밀번호 등이 포함될 수 있다. 이를 그대로 AI API에 보내면 AI 서버에 저장될 수 있어 유출 위험이 있다. `sanitizer.py`에서 정규식으로 감지하여 마스킹 처리 후 프롬프트에 포함한다.

### 1-6. 환경변수 관리

AI API Key는 코드에 하드코딩하지 않고 환경변수 `AI_API_KEY`로만 관리한다. `python-dotenv`의 `load_dotenv()`로 `.env` 파일에서 자동 로딩한다. `.env`는 `.gitignore`에 포함하여 GitHub에 푸시하지 않는다.

---

## 2. 고찰

### 2-1. "AI API 연동의 핵심은 호출이 아니라 프롬프트 설계"

같은 git diff를 줘도 프롬프트에 따라 결과가 완전히 다르다:
- "커밋 메시지 써줘" → 막 씀 (품질 낮음, 형식 무시)
- "너는 시니어 개발자야. Conventional Commits 양식으로. 변경 이유 포함. 50자 이내 제목." → 품질 높음

API 호출은 수단이고, 프롬프트 설계가 목적이다.

### 2-2. temperature가 결과 품질에 미치는 영향

| temperature | 특성 | 적합한 용도 |
|------------|------|-----------|
| 0.0~0.3 | 결정론적, 거의 같은 답 | 코드 생성, 커밋 메시지 (정확성 중시) |
| 0.4~0.7 | 균형 | 일반 문서, 요약 |
| 0.7~1.0 | 창의적, 다양한 답 | 마케팅 문구, 아이디어 (다양성 중시) |

커밋 메시지는 같은 변경에 대해 일관된 결과가 나와야 하므로 0.3을 선택했다.

### 2-3. 민감정보가 왜 문제인가

`git diff`에 `.env` 파일 변경이 포함될 수 있다. AI API에 API Key를 보내면:
1. AI 서버에 데이터가 저장될 수 있음
2. 로그에 남을 수 있음
3. 훈련 데이터에 포함될 가능성 (일부 서비스)

따라서 마스킹 후 프롬프트에 포함해야 안전하다.

### 2-4. Mock 모드의 필요성

API Key가 없는 환경(개발, CI/CD, 평가 환경)에서도 프로그램이 동작해야 한다. Mock 모드(`--mock` 또는 `AI_MOCK_MODE=true`)는 AI API를 호출하지 않고 미리 정의된 템플릿으로 결과를 생성한다.

---

## 3. 시도

### 3-1. 6개 모듈 구현

| 모듈 | 역할 | 핵심 함수 |
|------|------|----------|
| `git_collector.py` | Git 변경 사항 수집 | `get_status()` → git status 출력, `get_diff()` → git diff 출력 |
| `sanitizer.py` | 민감정보 마스킹 | `mask_sensitive(diff)` → 정규식으로 nvapi-/sk-/ghp_ API Key, 이메일, 비밀번호를 `***MASKED***`로 치환 |
| `ai_client.py` | AI API 호출 | `generate_commit_message(prompt, git_info)` → 동기 requests.post, timeout 30s, error handling |
| `prompt_builder.py` | 프롬프트 템플릿 | `build_commit_prompt(diff, files)` → 역할+양식+맥락+제약, `build_pr_prompt()` |
| `main.py` | CLI 진입점 | `commit`, `pr` subcommand, `--mock` 옵션, `load_dotenv()` |
| `validator.py` | 출력 검증 | `validate_commit_message(text)` → 제목 50자 이내, type: subject 형식 확인 |

### 3-2. 자동화 흐름

```
CLI 실행 (python main.py commit)
  ↓
git_collector: git status + git diff 수집
  ↓
sanitizer: 민감정보 마스킹 (nvapi-xxx, sk-xxx, ghp_xxx, 이메일, 비밀번호)
  ↓
prompt_builder: 커밋 메시지 템플릿 생성
  (역할: 시니어 개발자, 양식: Conventional Commits, 맥락: diff 요약)
  ↓
ai_client: NVIDIA NIM API 호출
  (model: llama-3.1-8b-instruct, temperature: 0.3, max_tokens: 500)
  ↓
validator: 출력 형식 검증 (길이, 템플릿 준수)
  ↓
터미널 출력: 커밋 메시지 / PR 설명 초안
```

### 3-3. CLI 옵션

```bash
python main.py commit          # 커밋 메시지 생성 (AI API 1회 호출)
python main.py pr              # PR 설명 생성 (AI API 1회 호출)
python main.py commit --mock   # Mock 모드 (API 호출 없이, 템플릿 결과)
```

### 3-4. 사전평가 3회 개선

| 시도 | 점수 | FAIL 항목 | 수정 내용 |
|------|------|----------|----------|
| 1회차 | 63% (10/16) | API Key 미설정 시 오류가 아닌 Mock 전환만 함, temperature/max_tokens 미문서화 | Mock 모드 추가, API 파라미터 문서화, --temperature/--max-tokens CLI 옵션 |
| 2회차 | 94% (15/16) | 출력 형식 검증 부족 | validator.py 추가 — 제목 길이, Conventional Commits 형식 자동 검증 |
| 3회차 | 100% (16/16) | — | validator.py 추가 — 출력 형식 자동 검증 로직 |

---

## 4. 수정

| 수정 항목 | 수정 전 | 수정 후 | 이유 |
|----------|--------|--------|------|
| API Key 미설정 처리 | Mock 전환만 (오류 출력 없음) | 오류 출력 + 종료 옵션 + Mock 전환 (요구사항 준수) | 1회차 FAIL: "API Key 누락시 오류 출력 및 종료" |
| temperature/max_tokens | 고정값, 문서 없음 | CLI 옵션 + README 문서화 | 1회차 FAIL: 파라미터 영향 설명 부족 |
| 출력 검증 | 없음 | validator.py로 길이/템플릿 자동 검증 | 2회차 FAIL: "실무 규칙 만족하도록 검증" |
| 응답 잘림 | max_tokens 너무 낮음 | 500으로 증가 | AI 응답이 중간에 잘리는 문제 |
| 응답 파싱 | 마크다운만 처리 | 일반 텍스트도 처리 | AI가 마크다운이 아닌 형식으로 반환하는 경우 대응 |
| .env 자동 로딩 | 수동 로딩 | `python-dotenv` `load_dotenv()` | main.py에서 .env 자동 읽기 |
| "OpenAI 호환" 문구 | 문서에 포함 | 전부 제거 | 과제 요구사항: "OpenAI 호환" 문구 제거 |

---

## 5. 선택과 선정

| 선택 기로 | 선택 | 포기한 것 | 근거 |
|----------|------|----------|------|
| NVIDIA NIM vs OpenAI | NVIDIA NIM | OpenAI | 무료 크레딧, chat/completions 표준 포맷, llama-3.1-8b-instruct |
| temperature 값 | 0.3 | 0.7 (창의적) | 커밋 메시지는 정확성 > 창의성, 일관된 결과 |
| max_tokens | 500 | 더 큰 값 | 커밋 메시지는 간결, 비용 절감 |
| Mock 모드 | `--mock` / `AI_MOCK_MODE=true` | 단순함 | API Key 없이 개발/테스트, CI/CD 환경 |
| API Key 관리 | 환경변수 `AI_API_KEY`만 | 하드코딩 편의성 | 보안 — 코드에 Key 절대 안 씀 |
| 민감정보 처리 | sanitizer 정규식 마스킹 | 수동 확인 | 자동화 — NVIDIA NIM Key(`nvapi-xxx`), OpenAI Key(`sk-xxx`), GitHub PAT(`ghp_xxx`), 이메일, 비밀번호 패턴 감지 |
| 모듈 분리 | 6개 파일로 분리 | 단일 파일 | 관심사 분리, 테스트 용이, 유지보수 |
| 1회 실행 요청 제한 | commit/pr 각각 1회 호출 | 여러 번 | 과제 권장: 비용 방지, 로그에 호출 횟수 출력 |

---

## 6. 트러블슈팅

### 6-1. AI 응답 잘림

**문제**: AI가 생성한 커밋 메시지가 중간에 잘림
**원인**: `max_tokens`가 너무 낮게 설정되어 있었음
**해결**: 500으로 증가. 커밋 메시지는 짧지만 PR 설명은 길 수 있으므로 여유 있게 설정

### 6-2. AI 응답 파싱 에러

**문제**: AI가 마크다운이 아닌 일반 텍스트로 반환하여 파싱 실패
**원인**: 모델에 따라 출력 형식이 다를 수 있음
**해결**: 다양한 형식(마크다운, 일반 텍스트, 코드 블록)을 처리하는 파싱 로직 추가

### 6-3. 1회차 사전평가 FAIL: API Key 미설정 처리

**문제**: API Key가 없을 때 Mock으로 전환만 하고, 요구사항인 "오류 출력 및 종료"를 구현하지 않음
**원인**: 요구사항을 "오류 출력 후 종료"와 "Mock 전환" 둘 다로 해석했으나, 평가는 "오류 출력"을 원했음
**해결**: `--mock` 옵션 없이 API Key 미설정 시 오류 메시지 출력 + 종료, `--mock` 명시 시에만 Mock 전환

### 6-4. 2회차 사전평가 FAIL: 출력 검증 부족

**문제**: AI가 너무 긴 메시지를 생성하거나 Conventional Commits 양식을 안 지킴
**원인**: 출력 후 검증 로직이 없었음
**해결**: `validator.py` 추가 — 제목 50자 이내 확인, `type: subject` 형식 확인, 불합격 시 경고 출력

### 6-5. 민감정보 노출 위험

**문제**: `git diff`에 `.env` 파일 변경이 포함되어 API Key가 AI 프롬프트에 그대로 노출
**원인**: 마스킹 처리 없이 diff를 프롬프트에 포함
**해결**: `sanitizer.py`에서 정규식으로 `nvapi-[a-zA-Z0-9_\-]+`, `sk-[a-zA-Z0-9]+`, `ghp_[a-zA-Z0-9]+`, 이메일 패턴, 비밀번호 패턴을 `***MASKED***`로 치환 후 프롬프트에 포함

### 6-6. .env 자동 로딩 안 됨

**문제**: `.env` 파일에 `AI_API_KEY`를 넣었지만 환경변수로 인식 안 됨
**원인**: `python-dotenv`의 `load_dotenv()`를 호출하지 않았음
**해결**: `main.py` 시작 부분에 `from dotenv import load_dotenv; load_dotenv()` 추가

---

## 7. 평가 예상 질문 대비

| 질문 | 답변 방향 | 코드 근거 |
|------|----------|-----------|
| AI API 연동 전체 흐름? | 요청 구성(headers, body) → 응답 처리(JSON 파싱) → 예외 대응(timeout, 에러) | `ai_client.py` |
| temperature 영향? | 낮을수록 결정론적, 높을수록 창의적 → 커밋 메시지는 0.3 (정확성) | `ai_client.py: temperature=0.3` |
| 프롬프트 설계 원리? | 역할 부여 + Conventional Commits 양식 + 변경 맥락 + 출력 형식 지정 | `prompt_builder.py` |
| Git 연동 방식? | subprocess로 `git status`, `git diff` 실행 → 문자열 수집 → 프롬프트에 포함 | `git_collector.py` |
| 민감정보 처리? | sanitizer로 정규식 마스킹 (nvapi-/sk-/ghp_ API Key, 이메일, 비밀번호) → 마스킹된 diff만 프롬프트 | `sanitizer.py` |
| 출력 검증? | validator로 제목 50자 이내, `type: subject` 형식 확인 → 불합격 시 경고 | `validator.py` |
| Mock 모드 이유? | API Key 없이 개발/테스트, CI/CD 환경에서 API 호출 회피 | `--mock` / `AI_MOCK_MODE=true` |
| 환경변수 관리? | `AI_API_KEY`를 `.env`에 저장, `load_dotenv()` 자동 로딩, 하드코딩 금지 | `main.py` |
| 1회 실행 요청 제한? | commit/pr 각각 AI API 1회 호출, 로그에 호출 횟수 출력 | 과제 권장사항 준수 |
| max_tokens 왜 500? | 커밋 메시지는 간결, 비용 절감, 잘림 방지 | `ai_client.py` |
