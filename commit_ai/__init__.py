"""commit_ai — AI 기반 커밋 메시지 / PR 초안 자동 생성 패키지

모듈:
  - git_collector: Git 변경 사항 수집 (git status, git diff)
  - sanitizer: 민감정보 마스킹 + diff 제한 (--safe-mode)
  - prompt_builder: AI 프롬프트 조립 (커밋/PR용)
  - ai_client: NVIDIA NIM API 호출 (mock 지원)
  - validator: 출력 형식 자동 검증
"""
from commit_ai.git_collector import GitCollector
from commit_ai.ai_client import AIClient
from commit_ai.prompt_builder import build_commit_prompt, build_pr_prompt
from commit_ai.validator import validate_commit_message, validate_pr_draft, print_validation

__all__ = [
    "GitCollector",
    "AIClient",
    "build_commit_prompt",
    "build_pr_prompt",
    "validate_commit_message",
    "validate_pr_draft",
    "print_validation",
]
