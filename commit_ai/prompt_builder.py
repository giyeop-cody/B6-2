"""프롬프트 빌더 모듈

- git diff 정보를 AI 프롬프트로 변환
- JSON 스키마를 프롬프트에 포함하여 AI가 JSON으로 응답하도록 요청
- 커밋 메시지용 / PR 본문용 프롬프트 템플릿
"""
from commit_ai.sanitizer import sanitize_diff


# ===== JSON 스키마 정의 =====

COMMIT_SCHEMA = """{
  "type": "feat | fix | docs | refactor | test | chore | style | perf | ci | build",
  "subject": "커밋 제목 (50자 이내, 한글)",
  "body_points": ["변경 내용 bullet 1", "변경 내용 bullet 2", "변경 내용 bullet 3"]
}"""

PR_SCHEMA = """{
  "title": "PR 제목 (type: 요약 형식, 80자 이내)",
  "why": ["변경 배경 1", "변경 배경 2"],
  "what": ["핵심 변경 1", "핵심 변경 2"],
  "how_to_test": ["테스트 방법 1", "테스트 방법 2"]
}"""


def build_commit_prompt(git_info, safe_mode=False):
    """커밋 메시지 생성용 프롬프트 구성

    AI에게 JSON 스키마를 전달하고, JSON 형식으로만 응답하도록 요청합니다.
    """
    files = git_info.get("changed_files", [])
    diff = git_info.get("diff", "")
    diff_lines = git_info.get("diff_lines", 0)

    sanitized = sanitize_diff(diff, safe_mode=safe_mode)
    file_list = "\n".join(f"  - {f}" for f in files)

    prompt = f"""다음 Git 변경 사항을 분석해서 커밋 메시지를 작성해주세요.

## 변경된 파일 ({len(files)}개)
{file_list}

## Git Diff ({diff_lines}줄)
```
{sanitized}
```

## 작성 규칙
1. type: 변경 성격에 맞는 것 선택 (feat/fix/docs/refactor/test/chore/style/perf/ci/build)
2. subject: 변경 사항을 한 줄로 요약 (50자 이내, 한글)
3. body_points: 구체적 변경 내용을 2~3개 bullet point로 작성 (각 1줄)

## 응답 형식 (반드시 아래 JSON 형식으로만 응답할 것)
```json
{COMMIT_SCHEMA}
```

주의: JSON 외의 텍스트는 절대 출력하지 마세요. 마크다운 코드 블록도 필요 없습니다. 오순 JSON만 출력하세요."""
    return prompt


def build_pr_prompt(git_info, safe_mode=False):
    """PR 제목/본문 생성용 프롬프트 구성

    AI에게 JSON 스키마를 전달하고, JSON 형식으로만 응답하도록 요청합니다.
    """
    branch = git_info.get("branch", "")
    files = git_info.get("changed_files", [])
    diff = git_info.get("diff", "")
    diff_lines = git_info.get("diff_lines", 0)

    sanitized = sanitize_diff(diff, safe_mode=safe_mode)
    file_list = "\n".join(f"  - {f}" for f in files)

    prompt = f"""다음 Git 변경 사항을 분석해서 PR 제목과 본문을 작성해주세요.

## 브랜치
{branch}

## 변경된 파일 ({len(files)}개)
{file_list}

## Git Diff ({diff_lines}줄)
```
{sanitized}
```

## 작성 규칙
1. title: `<type>: <요약>` 형식 (80자 이내)
2. why: 이 변경을 하게 된 배경/목적 (1~2개 bullet)
3. what: 구체적인 변경 내용 (2~3개 bullet)
4. how_to_test: 테스트 방법 (환경변수 설정, 실행 명령 등, 2~3개 bullet)

## 응답 형식 (반드시 아래 JSON 형식으로만 응답할 것)
```json
{PR_SCHEMA}
```

주의: JSON 외의 텍스트는 절대 출력하지 마세요. 마크다운 코드 블록도 필요 없습니다. 오순 JSON만 출력하세요."""
    return prompt
