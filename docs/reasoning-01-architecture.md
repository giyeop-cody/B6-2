# 추론 기록 #01: 아키텍처 설계

## 설계 원칙: 단일 책임 + 관심사 분리

터미널 도구이지만, 모든 로직을 main.py에 넣으면 유지보수가 어렵다. 그래서 **5개 모듈로 분리**했다.

## 모듈별 역할

| 모듈 | 역할 | 분리 이유 |
|------|------|-----------|
| `main.py` | CLI 인터페이스 (입력/출력) | 사용자 접점 분리 |
| `git_collector.py` | Git 데이터 수집 | Git 의존성 격리 — Git 없는 환경에서도 다른 모듈 테스트 가능 |
| `ai_client.py` | AI API 호출 | API 의존성 격리 — mock/real 분기로 개발과 운영 분리 |
| `prompt_builder.py` | 프롬프트 조립 | 프롬프트 설계와 비즈니스 로직 분리 — 프롬프트 개선 시 이 파일만 수정 |
| `sanitizer.py` | 민감정보 마스킹 | 보안 로직 독립 — 마스킹 패턴 추가 시 이 파일만 수정 |

## 데이터 흐름

```
사용자 (CLI)
  ↓ (명령: commit/pr)
main.py
  ↓ (변경사항 수집)
git_collector.py → git status/diff
  ↓ (diff 데이터)
prompt_builder.py → 프롬프트 조립
  ↓ (sanitizer.py로 마스킹)
ai_client.py → mock or real API
  ↓ (결과)
main.py → 터미널 출력
```

## 응용
- 다른 Git 도구에 재사용: git_collector + sanitizer는 독립적으로 재사용 가능
- 다른 AI 모델 연결: ai_client의 `_call_real_api`만 수정하면 새 모델 지원
- 다른 프롬프트 추가: prompt_builder에 새 함수 추가 (예: `build_review_prompt()`)
