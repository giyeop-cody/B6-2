# 추론 기록 #03: 민감정보 마스킹 설계

## 제약사항

> `git diff`에 포함될 수 있는 민감정보(API Key, 개인정보 등)는 프롬프트에 포함하지 않도록 주의한다.
> 아래 중 1개 이상을 `-safe-mode` 옵션으로 제공한다.
> (A) diff에서 특정 패턴을 마스킹 후 전송
> (B) diff 일부만 전송 (예: 최대 10개 파일, 최대 200줄)

## 설계: (A) + (B) 모두 구현

### 기본 모드: 패턴 마스킹만 (항상 수행)
민감정보는 어떤 상황에서도 프롬프트에 들어가면 안 되므로, **마스킹은 기본적으로 항상 수행**.

마스킹 패턴:
- `sk-xxx` (NVIDIA NIM API Key)
- `ghp_xxx` (NVIDIA NIM API Key)
- `sb_publishable_xxx` / `sb_secret_xxx` (Supabase)
- 이메일 (`user@domain.com`)
- `password=xxx`, `secret=xxx`, `token=xxx`, `api_key=xxx`
- JWT (`eyJ...`)
- AWS 키 (`AKIA...`)
- 전화번호 (`xx-xxxx-xxxx`)

### safe-mode: 마스킹 + 파일/줄 제한
`--safe-mode` 시 추가로:
- 최대 10개 파일까지만 diff 전송
- 최대 200줄까지만 diff 전송
- 초과분은 `... (N개 파일 생략)` 메시지로 대체

## 핵심 결정: 마스킹은 "항상", 제한은 "옵션"

마스킹은 보안 필수사항이므로 옵션이 아님. safe-mode의 추가 보호(파일/줄 제한)는 옵션.

```python
def sanitize_diff(diff, safe_mode=False):
    result = mask_sensitive(diff)  # 항상 수행
    if safe_mode:
        result = truncate_diff(result)  # 옵션
    return result
```

## 응용
- 새 패턴 추가: `PATTERNS` 리스트에 regex 추가만 하면 됨
- 다른 보안 요구: 파일명 자체를 마스킹 (예: `.env` 파일 제외)
- 로깅: 마스킹된 항목 수를 로그에 출력하여 보안 감사 가능
