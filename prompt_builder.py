"""
프롬프트 빌더 모듈
- git diff 정보를 AI 프롬프트로 변환
- 커밋 메시지용 / PR 본문용 프롬프트 템플릿
"""
from sanitizer import sanitize_diff


def build_commit_prompt(git_info, safe_mode=False):
    """커밋 메시지 생성용 프롬프트 구성"""
    files = git_info.get("changed_files", [])
    diff = git_info.get("diff", "")
    diff_lines = git_info.get("diff_lines", 0)

    # 민감정보 마스킹 + safe-mode
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
1. 커밋 메시지 형식: `<type>: <요약>` (type: feat/fix/docs/refactor/test/chore)
2. 요약은 50자 이내, 한글로 작성
3. 본문은 변경 내용을 2~3개 bullet point로 요약
4. 코드를 분석해서 적절한 type을 선택하세요

## 출력 형식
```
<type>: <요약>

- <변경 내용 1>
- <변경 내용 2>
```
"""
    return prompt


def build_pr_prompt(git_info, safe_mode=False):
    """PR 본문 생성용 프롬프트 구성"""
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
1. PR 제목: `<type>: <요약>` 형식, 50자 이내
2. PR 본문은 아래 구조를 따르세요:

### Why
- 이 변경을 하게 된 배경/목적 (1~2문장)

### What
- 구체적인 변경 내용 (bullet point 2~3개)

### How to Test
- 테스트 방법 (환경변수 설정, 실행 명령 등)

## 출력 형식
```
## PR Title
<type>: <요약>

## PR Body
### Why
- ...

### What
- ...

### How to Test
- ...
```
"""
    return prompt
