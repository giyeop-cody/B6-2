# 추론 기록 #02: Mock + Real 듀얼 모드 설계

## 문제 상황

이 과제는 AI API 연결이 필수이지만:
1. 개발/테스트 환경에서 API Key가 없을 수 있음
2. NVIDIA NIM(PAT) 발급 전에 코드를 테스트해야 할 수 있음
3. 평가 환경에서 API 호출이 불가능할 수 있음

→ API Key 없이도 도구가 동작해야 함 (개발/테스트용)

## 해결: Mock 모드 명시적 전환

```python
class AIClient:
    def __init__(self, ...):
        # --mock 옵션 또는 AI_MOCK_MODE=true 환경변수일 때만 mock
        self.is_mock = os.environ.get("AI_MOCK_MODE", "").lower() in ("true", "1", "yes")
```

- 기본: Real 모드 (NVIDIA NIM API 호출, API Key 필수)
- `--mock` 옵션 또는 `AI_MOCK_MODE=true`: Mock 모드 (템플릿 기반)
- API Key 미설정 + Real 모드: 에러 메시지 출력 후 종료 (과제 요구사항)

## Mock 모드 구현 전략

Mock이 단순한 고정 텍스트면 의미가 없다. **실제 diff를 분석해서 의미 있는 결과**를 생성:

1. **파일 타입 추정**: 확장자로 언어/타입 파악 (.py → Python, .md → 문서)
2. **커밋 타입 분류**: diff 패턴으로 feat/fix/docs/test 추정
3. **PR 구조**: Why/What/How to Test 템플릿 + 실제 파일명/줄수 반영

## 응용
- CI/CD에서 mock 모드로 테스트: API 호출 없이 로직 검증
- mock을 더 정교하게: diff에서 함수명 추출, 변경 라인 분석 등
- 다른 AI API로 교체: ai_client.py의 _call_real_api만 수정하면 됨
