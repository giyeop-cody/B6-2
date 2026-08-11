# B6-2 학습 노트: 내가 고친 코드 설명을 AI가 대신 써주는 도우미 만들기

> **문과 중졸도 이해할 수 있게** — 전에 코딩을 한 번도 해본 적 없는 사람이 읽어도 이해할 수 있도록 쓴 학습 노트입니다.

---

## 📖 목차

1. [초심자를 위한 용어집](#1-초심자를-위한-용어집)
2. [과제 해석 및 분석](#2-과제-해석-및-분석)
3. [과제를 진행하기 위한 기초](#3-과제를-진행하기-위한-기초)
4. [각 기초를 익히기 위한 간단한 체험 예제](#4-각-기초를-익히기-위한-간단한-체험-예제)
5. [과제를 작게 쪼개기: 잡 → 워크 → 워크플로우](#5-과제를-작게-쪼개기-잡--워크--워크플로우)
6. [워크플로우별 트레이드오프, 이슈, 트러블슈팅](#6-워크플로우별-트레이드오프-이슈-트러블슈팅)
7. [과제 완료 후 학습한 내용 정리](#7-과제-완료-후-학습한-내용-정리)

---

## 1. 초심자를 위한 용어집

> "이 단어들이 전부 외계어처럼 보여도 괜찮습니다. 하나씩, 일상어로 풀어 설명합니다."

### 🤖 AI / API 관련

| 용어 | 쉬운 설명 | 비유 |
|------|-----------|------|
| **AI API** | AI 모델에게 "이 텍스트 읽고 요약해 줘"라고 부탁하는 전화선 | AI에게 일을 시키는 주문서 |
| **API Key** | AI 서비스에 접근하기 위한 비밀번호 | 출입증 (없으면 들어갈 수 없음) |
| **NVIDIA NIM** | NVIDIA에서 제공하는 AI 모델 호출 서비스 | AI 모델을 빌려주는 대여소 |
| **모델 (Model)** | 텍스트를 이해하고 생성하는 AI의 두뇌 | 요리사 (입력=재료, 출력=요리) |
| **llama-3.3-70b** | 이 과제에서 사용한 AI 모델 이름 | 요리사의 이름과 경력 |
| **프롬프트 (Prompt)** | AI에게 주는 지시문. "어떻게 부탁하느냐"가 결과 품질을 결정 | 요리 주문서 ("매운맛으로, 덜 익혀서") |
| **temperature** | AI의 창의성 조절값. 낮을수록 일관됨, 높을수록 다양함 | 요리사의 자유도 (낮음=레시피대로, 높음=즉흥) |
| **max_tokens** | AI가 생성할 수 있는 최대 글자 수 | 요리의 최대 분량 |
| **토큰 (Token)** | AI가 텍스트를 나누는 단위. 대략 단어의 0.75배 | 요리의 한 입거리 |
| **Chat Completions** | 대화 형식으로 AI에게 요청하는 API 방식 | 채팅으로 주문하는 시스템 |
| **스트리밍 (Streaming)** | AI가 답을 다 만들 때까지 기다리지 않고 조금씩 받아오는 방식 | 음식이 다 되면 한꺼번에 가져오지 않고 조금씩 가져오기 |

### 🌳 Git 관련

| 용어 | 쉬운 설명 | 비유 |
|------|-----------|------|
| **Git** | 코드 변경 이력을 관리하는 도구 | 가계부 (언제 무엇을 바꿨는지 기록) |
| **git status** | 현재 뭘 바꿨는지 보여주는 명령 | 냉장고 확인 (뭐가 달라졌나) |
| **git diff** | 구체적으로 어떤 줄이 바뀌었는지 보여주는 명령 | 영수증 (정확히 뭘 샀나) |
| **커밋 (Commit)** | 변경 사항을 "이 시점"으로 저장하는 행동 | 가계부에 한 줄 적기 |
| **커밋 메시지** | "이 변경이 뭘 하는지" 설명하는 짧은 글 | 가계부의 적요 ("점심 - 김치찌개 7,000원") |
| **PR (Pull Request)** | "이 코드 봐주시고 합쳐주세요"라고 팀원에게 보내는 요청 | 보고서 제출 ("검토 부탁드립니다") |
| **Conventional Commits** | 커밋 메시지를 `type: subject` 형식으로 쓰는 규칙 | 가계부의 표준 양식 (날짜-항목-금액) |
| **브랜치 (Branch)** | 원본 코드를 건드리지 않고 따로 작업하는 공간 | 복사본 만들어서 거기서 작업하기 |

### 🔧 Python / CLI 관련

| 용어 | 쉬운 설명 | 비유 |
|------|-----------|------|
| **CLI (Command Line Interface)** | 터미널에서 글자로 명령하는 방식 | 키오스크 대신 점원에게 말로 주문 |
| **argparse** | Python에서 명령줄 옵션을 처리하는 도구 | 주문서 양식 (—commit, —pr, —mock) |
| **subprocess** | Python 안에서 다른 프로그램(git 등)을 실행하는 도구 | Python이 대신 git 명령을 타이핑 |
| **환경변수 (.env)** | 비밀번호 같은 민감 정보를 코드 밖에 저장하는 파일 | 금고 (코드에는 금고 번호 없음) |
| **python-dotenv** | .env 파일을 자동으로 읽어주는 도구 | 금고를 자동으로 열어주는 비서 |
| **async / await** | "데이터 올 때까지 기다렸다가 다음 줄 실행" | 배달 기다렸다가 식사하기 |
| **Mock 모드** | 진짜 AI API를 호출하지 않고 가짜 결과를 반환하는 모드 | 연습용 주방 (진짜 재료 없이 연습) |
| **정규식 (Regex)** | 텍스트에서 특정 패턴을 찾는 규칙 | "nvapi-로 시작하는 문자열 찾기" 같은 탐지기 |

### 🔒 보안 관련

| 용어 | 쉬운 설명 | 비유 |
|------|-----------|------|
| **민감정보 마스킹** | API Key, 이메일 등을 `[REDACTED]`로 가리는 것 | 지문으로 중요 부분 가리기 |
| **하드코딩** | 비밀번호를 코드에 직접 적는 것 (금지) | 금고 비번을 쪽지에 적어 금고 옆에 붙여놓기 |
| **레이트 리밋 (Rate Limit)** | 너무 많이 호출하면 차단하는 제한 | "1인 1주문만 가능합니다" |
| **타임아웃 (Timeout)** | 일정 시간 내에 응답 안 오면 포기 | 배달 30분 넘으면 취소 |

---

## 2. 과제 해석 및 분석

### 2.1 한 줄 요약

**Git 변경 사항을 AI에게 넘기면, AI가 커밋 메시지와 PR 설명을 대신 써주는 CLI 도구를 만들어라.**

### 2.2 과제가 원하는 것

개발자가 코드를 고치고 커밋할 때, "이 변경이 뭘 하는지" 설명하는 커밋 메시지와 PR 설명을 작성하는 건 번거롭다. 이 과제는 AI API를 활용해서 그 과정을 자동화하는 것이다.

```
개발자가 코드를 고침
    ↓
git diff (무엇이 바뀌었는지 수집)
    ↓
민감정보 마스킹 (API Key 등 가리기)
    ↓
프롬프트 설계 (AI에게 "이렇게 써줘"라고 부탁)
    ↓
AI API 호출 (NVIDIA NIM)
    ↓
AI가 커밋 메시지 / PR 설명 생성
    ↓
출력 검증 (형식 맞는지 확인)
    ↓
터미널에 결과 출력
```

### 2.3 반드시 해야 하는 것 (필수)

| # | 요구사항 | 왜 필요한가? |
|---|---------|-------------|
| 1 | **Git 변경 사항 수집** | 뭘 바꿨는지 알아야 AI에게 설명할 수 있음 |
| 2 | **AI API 연동** | AI가 텍스트를 생성해 주는 핵심 기능 |
| 3 | **프롬프트 설계** | "어떻게 부탁하느냐"가 결과 품질을 결정 |
| 4 | **민감정보 마스킹** | API Key 등이 AI에게 넘어가면 유출 위험 |
| 5 | **CLI 설계 (commit/pr 명령)** | 사용자가 터미널에서 쉽게 실행 |
| 6 | **출력 검증** | AI가 형식을 안 지키면 실무에 못 씀 |
| 7 | **환경변수로 API Key 관리** | 코드에 Key를 직접 적으면 GitHub에 노출 |
| 8 | **README 작성** | 다른 사람이 문서만 보고 실행할 수 있게 |

### 2.4 제약 사항

| 제약 | 이유 |
|------|------|
| API Key는 환경변수로만 관리, 하드코딩 금지 | 보안 — GitHub에 Key가 올라가면 유출 |
| 1회 실행 시 AI API 호출 1~2회 이내 | 비용 방지 |
| git diff에 포함된 민감정보는 프롬프트에서 제외 | AI 서버에 민감정보 저장 방지 |
| git push, GitHub PR 생성 등 원격 조작은 구현 안 함 | 범위 제한 (초안 텍스트 출력까지만) |

### 2.5 평가 기준 분석

| 항목 | 무엇을 보는가 | 우리가 대비한 것 |
|------|-------------|-----------------|
| **AI API 연동** | 요청 구성, 응답 처리, 예외 대응 전체 흐름 | ai_client.py: async, timeout, error handling |
| **파라미터 이해** | temperature, max_tokens의 영향 설명 | README + CLI 옵션 (--temperature, --max-tokens) |
| **프롬프트 설계** | 어떻게 프롬프트를 구성했는지 원리 설명 | prompt_builder.py: 역할+양식+맥락+제약 |
| **Git 연동** | git status/diff를 프로그램 입력으로 연결 | git_collector.py: subprocess |
| **출력 검증** | 실무 규칙(길이, 템플릿) 만족하도록 검증 | validator.py: 제목 50자, type: subject 형식 |
| **보안** | 민감정보 마스킹, 환경변수 관리 | sanitizer.py + .env + load_dotenv() |

### 2.6 핵심 도전: "AI 결과물 품질 제어"

이 과제의 핵심은 AI API를 "호출"하는 것이 아니라, AI가 "원하는 품질"의 결과를 내도록 "제어"하는 것이다:

```
단순 호출: "커밋 메시지 써줘" → AI가 막 씀 → 형식 무시, 너무 김, 의미 불명확
품질 제어: "시니어 개발자야. Conventional Commits 양식. 50자 이내 제목. Why/What/How to Test 본문."
         → AI가 규칙을 지킨 결과 생성 → 실무에 바로 사용 가능
```

---

## 3. 과제를 진행하기 위한 기초

### 3.1 기초 1: AI API의 개념과 구조

**무엇을 아야 하나?** AI 모델에게 텍스트 생성을 부탁하는 방법

**왜 필요한가?** 이 과제의 핵심 기능이 AI API 호출이다.

**핵심 개념:**
```
요청 (Request):
  POST https://integrate.api.nvidia.com/v1/chat/completions
  Headers: Authorization: Bearer nvapi-xxxxx
  Body: {
    "model": "meta/llama-3.3-70b-instruct",
    "messages": [
      { "role": "system", "content": "너는 시니어 개발자야" },
      { "role": "user", "content": "이 diff에 대한 커밋 메시지 써줘: ..." }
    ],
    "temperature": 0.3,
    "max_tokens": 500
  }

응답 (Response):
  {
    "choices": [
      { "message": { "content": "feat: 사용자 로그인 기능 추가" } }
    ]
  }
```

### 3.2 기초 2: 프롬프트 설계

**무엇을 아야 하나?** AI에게 "어떻게 부탁할지"를 설계하는 방법

**왜 필요한가?** 같은 git diff를 줘도 프롬프트에 따라 결과 품질이 완전히 다르다.

**핵심 개념 — 4가지 요소:**
1. **역할 부여**: "너는 시니어 개발자야" → AI가 전문가 관점에서 작성
2. **출력 양식**: "Conventional Commits 형식으로 작성: `type: subject`" → 형식 통일
3. **변경 맥락**: git diff 요약 + 변경된 파일 목록 → AI가 맥락을 이해
4. **제약사항**: "제목 50자 이내, 본문은 Why/What/How to Test 구조" → 실무 규칙 준수

### 3.3 기초 3: Git 명령을 Python에서 실행

**무엇을 아야 하나?** Python 코드 안에서 git 명령을 실행하고 결과를 받는 방법

**왜 필요한가?** git diff를 자동으로 수집해서 AI에게 넘겨야 한다.

**핵심 개념:**
```python
import subprocess

result = subprocess.run(['git', 'diff'], capture_output=True, text=True)
diff_text = result.stdout  # git diff의 출력 문자열
```

### 3.4 기초 4: 환경변수와 보안

**무엇을 아야 하나?** API Key를 안전하게 관리하는 방법

**왜 필요한가?** Key를 코드에 직접 적으면 GitHub에 푸시했을 때 유출된다.

**핵심 개념:**
```python
# .env 파일:
AI_API_KEY=nvapi-xxxxxxxxxxxx

# main.py:
from dotenv import load_dotenv
load_dotenv()  # .env 파일 자동 읽기
import os
api_key = os.getenv("AI_API_KEY")  # 환경변수에서 읽기
```

### 3.5 기초 5: 민감정보 마스킹

**무엇을 아야 하나?** git diff에 포함된 비밀 정보를 가리는 방법

**왜 필요한가?** .env 파일 변경이 git diff에 포함되면 API Key가 AI에게 그대로 넘어간다.

**핵심 개념:**
```python
import re

def mask_secrets(text):
    # nvapi-로 시작하는 문자열 마스킹
    text = re.sub(r'nvapi-[a-zA-Z0-9]+', '[REDACTED]', text)
    # 이메일 마스킹
    text = re.sub(r'[\w.-]+@[\w.-]+', '[REDACTED]', text)
    return text
```

### 3.6 기초 6: CLI 설계 (argparse)

**무엇을 아야 하나?** 터미널에서 `python main.py commit` 같은 명령을 처리하는 방법

**왜 필요한가?** 사용자가 터미널에서 쉽게 실행할 수 있어야 한다.

**핵심 개념:**
```python
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('command', choices=['commit', 'pr'])
parser.add_argument('--mock', action='store_true')
parser.add_argument('--temperature', type=float, default=0.3)
args = parser.parse_args()
# python main.py commit --mock --temperature 0.1
```

---

## 4. 각 기초를 익히기 위한 간단한 체험 예제

### 4.1 체험 1: AI API 호출해보기 (기초 1)

```python
# ai_test.py — 가장 간단한 AI API 호출
import requests

response = requests.post(
    "https://integrate.api.nvidia.com/v1/chat/completions",
    headers={"Authorization": "Bearer nvapi-YOUR_KEY"},
    json={
        "model": "meta/llama-3.3-70b-instruct",
        "messages": [{"role": "user", "content": "안녕하세요!"}],
        "max_tokens": 50
    }
)
print(response.json()["choices"][0]["message"]["content"])
```

### 4.2 체험 2: 프롬프트 비교 (기초 2)

```python
# 나쁜 프롬프트
prompt1 = "커밋 메시지 써줘: def login(): pass"

# 좋은 프롬프트
prompt2 = """너는 시니어 개발자야. 다음 Git 변경사항에 대한 커밋 메시지를 작성해.
형식: Conventional Commits (type: subject)
제목: 50자 이내
변경사항: def login(): pass (로그인 함수 추가)"""

# 같은 AI라도 프롬프트에 따라 결과가 완전히 다름
```

### 4.3 체험 3: subprocess로 git 실행 (기초 3)

```python
# git_test.py
import subprocess

status = subprocess.run(['git', 'status'], capture_output=True, text=True)
print("=== git status ===")
print(status.stdout)

diff = subprocess.run(['git', 'diff'], capture_output=True, text=True)
print("=== git diff ===")
print(diff.stdout[:500])
```

### 4.4 체험 4: 환경변수 로딩 (기초 4)

```python
# env_test.py
from dotenv import load_dotenv
import os

load_dotenv()  # .env 파일 읽기
key = os.getenv("AI_API_KEY")
print(f"API Key: {key[:10]}..." if key else "API Key 없음")
```

### 4.5 체험 5: 정규식 마스킹 (기초 5)

```python
# mask_test.py
import re

text = "AI_API_KEY=nvapi-abc123xyz\nEMAIL=test@example.com\nIP=192.168.1.1"

# 마스킹
text = re.sub(r'nvapi-\w+', '[REDACTED]', text)
text = re.sub(r'[\w.-]+@[\w.-]+', '[REDACTED]', text)
text = re.sub(r'\d+\.\d+\.\d+\.\d+', '[REDACTED]', text)
print(text)
# AI_API_KEY=[REDACTED]
# EMAIL=[REDACTED]
# IP=[REDACTED]
```

### 4.6 체험 6: argparse CLI (기초 6)

```python
# cli_test.py
import argparse

parser = argparse.ArgumentParser(description="커밋 메시지 생성기")
parser.add_argument('command', choices=['commit', 'pr'], help='생성할 종류')
parser.add_argument('--mock', action='store_true', help='Mock 모드')
args = parser.parse_args()

print(f"명령: {args.command}")
print(f"Mock: {args.mock}")
# 실행: python cli_test.py commit --mock
```

---

## 5. 과제를 작게 쪼개기: 잡 → 워크 → 워크플로우

### 5.1 전체 잡 분해도

```
과제: AI 기반 Git 커밋/PR 자동 생성기 만들기
│
├── Job 1: Git 변경 사항 수집 (git_collector)
├── Job 2: 민감정보 마스킹 (sanitizer)
├── Job 3: 프롬프트 설계 (prompt_builder)
├── Job 4: AI API 연동 (ai_client)
├── Job 5: 출력 검증 (validator)
├── Job 6: CLI 통합 (main)
└── Job 7: 문서화 (README, .env.example)
```

### 5.2 각 잡별 워크 분해

#### Job 1: Git 변경 사항 수집

| 워크 | 내용 |
|------|------|
| W1-1 | subprocess로 `git status` 실행 |
| W1-2 | subprocess로 `git diff` 실행 |
| W1-3 | 결과를 문자열로 정리 (파일 목록 + diff 내용) |

#### Job 2: 민감정보 마스킹

| 워크 | 내용 |
|------|------|
| W2-1 | nvapi- 패턴 정규식 감지 |
| W2-2 | 이메일 패턴 정규식 감지 |
| W2-3 | IP 주소 패턴 정규식 감지 |
| W2-4 | 감지된 패턴을 [REDACTED]로 치환 |

#### Job 3: 프롬프트 설계

| 워크 | 내용 |
|------|------|
| W3-1 | 시스템 프롬프트 (역할 부여) |
| W3-2 | 커밋 메시지용 템플릿 (Conventional Commits) |
| W3-3 | PR 설명용 템플릿 (Why/What/How to Test) |
| W3-4 | diff + 파일 목록을 컨텍스트로 포함 |

#### Job 4: AI API 연동

| 워크 | 내용 |
|------|------|
| W4-1 | HTTP 요청 구성 (headers, body) |
| W4-2 | 응답 파싱 (JSON → content 추출) |
| W4-3 | 에러 처리 (timeout, 401, 429) |
| W4-4 | Mock 모드 구현 (API 호출 없이) |

#### Job 5: 출력 검증

| 워크 | 내용 |
|------|------|
| W5-1 | 제목 길이 검증 (50자 이내) |
| W5-2 | Conventional Commits 형식 검증 (type: subject) |
| W5-3 | 불합격 시 경고 메시지 출력 |

#### Job 6: CLI 통합

| 워크 | 내용 |
|------|------|
| W6-1 | argparse로 명령/옵션 처리 |
| W6-2 | 전체 흐름 연결 (수집→마스킹→프롬프트→API→검증→출력) |
| W6-3 | load_dotenv()로 .env 자동 로딩 |

### 5.3 워크플로우 실행 순서

```
Job 1 (Git 수집)
  ↓
Job 2 (마스킹)
  ↓
Job 3 (프롬프트 설계)
  ↓
Job 4 (AI API 호출)
  ↓
Job 5 (출력 검증)
  ↓
Job 6 (CLI 통합 — 위 모든 것을 하나로 묶음)
  ↓
Job 7 (문서화)
```

---

## 6. 워크플로우별 트레이드오프, 이슈, 트러블슈팅

### 6.1 Job 4 (AI API): NVIDIA NIM vs OpenAI

#### 🤔 선택의 기로

| 기준 | NVIDIA NIM | OpenAI |
|------|-----------|--------|
| 비용 | 무료 크레딧 | 유료 (사용량 기반) |
| 모델 | llama-3.3-70b-instruct | GPT-4o 등 |
| API 형식 | OpenAI 호환 (동일한 형식) | 표준 |
| 가용성 | NVIDIA 플랫폼 안정성 | 업계 표준 |

#### ✅ 선택: NVIDIA NIM

**이유:** 무료 크레딧으로 비용 부담 없이 테스트 가능, OpenAI 호환 엔드포인트라 코드 구조가 동일함

#### ⚖️ 트레이드오프
- **포기한 것:** OpenAI의 더 큰 커뮤니티와 튜토리얼
- **얻은 것:** 무료, llama-3.3-70b의 충분한 성능
- **판단:** 커밋 메시지 생성에는 llama-3.3-70b가 충분

---

### 6.2 Job 4 (AI API): temperature 값 선택

#### 🤔 선택의 기로

| temperature | 특성 | 적합 용도 |
|------------|------|----------|
| 0.0~0.3 | 결정론적, 일관됨 | 코드, 커밋 메시지 (정확성) |
| 0.4~0.7 | 균형 | 일반 문서, 요약 |
| 0.7~1.0 | 창의적, 다양함 | 마케팅, 아이디어 |

#### ✅ 선택: 0.3

**이유:** 커밋 메시지는 같은 변경에 대해 일관된 결과가 나와야 함. "창의적인" 커밋 메시지는 오히려 혼란을 줌.

#### ⚖️ 트레이드오프
- **포기한 것:** 다양한 표현 (같은 변경도 매번 다른 메시지)
- **얻은 것:** 일관성, 예측 가능성, 정확성
- **판단:** 커밋 메시지는 "정확하고 일관된" 것이 "창의적인" 것보다 중요

---

### 6.3 Job 2 (마스킹): 자동 마스킹 vs 수동 확인

#### 🤔 선택의 기로

| 기준 | 자동 마스킹 (정규식) | 수동 확인 |
|------|---------------------|----------|
| 속도 | 빠름 (자동) | 느림 (매번 확인) |
| 정확성 | 패턴 매칭 (일부 누락 가능) | 완벽 (사람이 확인) |
| 확장성 | 새 패턴 추가 용이 | 매번 사람이 필요 |

#### ✅ 선택: 자동 마스킹

**이유:** CLI 도구는 자동화가 목적이므로 사용자가 매번 확인하는 것은 목적에 반함. 정규식으로 주요 패턴(API Key, 이메일, IP)을 자동 감지.

#### ⚖️ 트레이드오프
- **포기한 것:** 100% 보장 (알 수 없는 패턴은 누락 가능)
- **얻은 것:** 자동화, 속도, --safe-mode 옵션으로 보수적 처리 가능
- **판단:** 자동화 도구에서 수동 확인은 비실용적

---

### 6.4 Job 4 (AI API): AI 응답 잘림 — 🐛 트러블슈팅

#### 🐛 문제
AI가 생성한 커밋 메시지가 중간에 잘림

#### 🔍 원인
`max_tokens`가 너무 낮게 설정되어 있었음. AI가 글을 다 쓰기 전에 토큰 한도 도달.

#### 💡 해결
`max_tokens`를 500으로 증가. 커밋 메시지는 짧지만 PR 설명은 길 수 있으므로 여유 있게 설정.

---

### 6.5 사전평가 1회차 FAIL: API Key 미설정 처리 — 🐛 트러블슈팅

#### 🐛 문제
API Key가 없을 때 Mock으로 전환만 하고, 요구사항인 "오류 출력 및 종료"를 구현하지 않음

#### 🔍 원인
요구사항을 "오류 출력 후 종료"와 "Mock 전환" 둘 다로 해석했으나, 평가는 "오류 출력"을 원했음

#### 💡 해결
- `--mock` 옵션 없이 API Key 미설정 시: 오류 메시지 출력 + 종료
- `--mock` 명시 시에만: Mock 전환 (템플릿 결과 출력)

---

### 6.6 사전평가 2회차 FAIL: 출력 검증 부족 — 🐛 트러블슈팅

#### 🐛 문제
AI가 너무 긴 메시지를 생성하거나 Conventional Commits 양식을 안 지킴

#### 🔍 원인
출력 후 검증 로직이 없었음. AI가 항상 형식을 지킬 것이라 가정했으나 아님.

#### 💡 해결
`validator.py` 추가:
- 제목 50자 이내 확인
- `type: subject` 형식 확인 (feat/fix/docs/refactor 등)
- 불합격 시 경고 메시지 출력

---

### 6.7 Job 2 (마스킹): 민감정보 노출 위험 — 🐛 트러블슈팅

#### 🐛 문제
`git diff`에 `.env` 파일 변경이 포함되어 API Key가 AI 프롬프트에 그대로 노출

#### 🔍 원인
마스킹 처리 없이 diff를 프롬프트에 포함

#### 💡 해결
`sanitizer.py`에서 정규식으로 다음 패턴을 `[REDACTED]`로 치환:
- `nvapi-[a-zA-Z0-9]+` (NVIDIA API Key)
- 이메일 패턴
- IP 주소 패턴

---

## 7. 과제 완료 후 학습한 내용 정리

### 7.1 배운 것: "AI API의 핵심은 호출이 아니라 프롬프트 설계"

**과제 전:** "AI API 연동 = API 호출 코드 작성"
**과제 후:** "AI API 연동 = 프롬프트 설계 + 파라미터 제어 + 출력 검증"

같은 git diff를 줘도 프롬프트에 따라 결과가 완전히 다르다. "커밋 메시지 써줘" vs "시니어 개발자야. Conventional Commits 양식. 50자 이내. Why/What/How to Test." — 후자가 10배 나은 결과를 낸다.

### 7.2 배운 것: temperature와 max_tokens의 영향

| 파라미터 | 낮을 때 | 높을 때 | 커밋 메시지에서의 선택 |
|----------|--------|--------|---------------------|
| temperature | 일관됨, 결정론적 | 다양함, 창의적 | 0.3 (정확성 > 창의성) |
| max_tokens | 짧은 출력 | 긴 출력 | 500 (간결 + 잘림 방지) |

### 7.3 배운 것: 보안 기본 습관

- API Key는 환경변수로만 관리 (하드코딩 금지)
- `.env`는 `.gitignore`에 포함 (GitHub에 푸시 금지)
- `git diff`의 민감정보는 마스킹 후 AI에게 전달
- `load_dotenv()`로 .env 자동 로딩

### 7.4 배운 것: 모듈 분리의 가치

| 분리 안 했을 때 | 분리했을 때 |
|---------------|-----------|
| main.py 하나에 전부 들어있음 | 6개 파일로 역할 분담 |
| "마스킹 로직 수정" → main.py 뒤져야 함 | sanitizer.py만 보면 됨 |
| "AI 클라이언트 교체" → 전체 수정 | ai_client.py만 바꾸면 됨 |
| 테스트: 전체 실행해야 함 | 각 모듈 독립 테스트 가능 |

### 7.5 핵심 인사이트 3가지

1. **"AI에게 일을 시키려면 명확한 지시가 필요하다"**: 프롬프트가 불명확하면 AI도 불명확한 결과를 낸다. 역할, 양식, 맥락, 제약을 명시해야 원하는 품질이 나온다.

2. **"자동화 도구에서 보안은 선택이 아닌 필수"**: git diff에는 API Key, 이메일, IP 등이 포함될 수 있다. 이를 AI에게 그대로 넘기면 유출 위험이 있다. 마스킹은 "하면 좋다"가 아니라 "해야 한다"이다.

3. **"AI의 출력을 신뢰하되 검증해야 한다"**: AI가 항상 형식을 지키는 것은 아니다. validator로 검증하지 않으면 50자가 넘는 제목, 잘못된 형식이 그대로 사용될 수 있다.

### 7.6 다음 단계로 나아가기 위한 메모

| 주제 | 이 과제에서 | 다음에 배울 것 |
|------|-----------|---------------|
| AI 모델 | llama-3.3-70b (텍스트 생성) | 코드 생성, 이미지 생성, 임베딩 |
| 프롬프트 | 단일 턴 (한 번 요청) | 멀티 턴 (대화), Few-shot 예제 |
| 자동화 | 커밋/PR 초안 생성 | git push, GitHub PR 생성 (API 연동) |
| 검증 | 길이/형식 검증 | 코드 리뷰 자동화, 테스트 생성 |
| 보안 | 정규식 마스킹 | AST 기반 분석, 시크릿 스캐너 |

---

> *이 학습 노트는 Codyssey AI/SW 기초 과정 B6-2 과제를 수행하며 학습한 내용을 정리한 것입니다.*
