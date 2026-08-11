#!/usr/bin/env python3
"""
B6-2: 내가 고친 코드 설명을 AI가 대신 써주는 도우미

사용법:
  python main.py commit [--mock] [--safe-mode] [--temperature 0.3] [--max-tokens 500]
  python main.py pr     [--mock] [--safe-mode] [--temperature 0.3] [--max-tokens 500]
  python main.py --help

명령:
  commit   git diff 기반 커밋 메시지 자동 생성
  pr       git diff 기반 PR 제목/본문 자동 생성

옵션:
  --mock           명시적 mock 모드 (AI API 호출 없이 템플릿 생성, 개발/테스트용)
  --safe-mode      diff에서 민감정보 마스킹 + 파일/줄 수 제한
  --temperature    AI API temperature (기본: 0.3, 낮을수록 결정론적)
  --max-tokens     AI API max_tokens (기본: 500, 출력 길이 제한)

환경변수:
  AI_API_KEY     NVIDIA NIM API Key (필수, nvapi-... 형식)
                  발급: https://build.nvidia.com → Settings → API Keys
  AI_API_URL     API 엔드포인트 (기본: NVIDIA NIM)
  AI_MODEL       모델명 (기본: meta/llama-3.1-8b-instruct, 3초 응답. 70b, Phi-3 등 선택 가능)
  AI_MOCK_MODE   true 설정 시 mock 모드 (개발/테스트용)
"""
import sys
import os
import argparse
from dotenv import load_dotenv
from git_collector import GitCollector
from ai_client import AIClient
from prompt_builder import build_commit_prompt, build_pr_prompt
from validator import validate_commit_message, validate_pr_draft, print_validation


def cmd_commit(args):
    """커밋 메시지 자동 생성"""
    collector = GitCollector()

    if not collector.has_changes():
        print("[INFO] 변경 사항이 없습니다. 커밋 메시지를 생성하지 않고 종료합니다.")
        return

    git_info = collector.collect()
    print(f"[INFO] Git status 수집 완료: {git_info['file_count']}개 파일 변경 감지")
    print(f"[INFO] Git diff 수집 완료: {git_info['diff_lines']}줄")

    prompt = build_commit_prompt(git_info, safe_mode=args.safe_mode)

    if args.mock:
        os.environ["AI_MOCK_MODE"] = "true"

    client = AIClient(temperature=args.temperature, max_tokens=args.max_tokens)
    result = client.generate_commit_message(prompt, git_info)

    if result is None:
        print("[ERROR] 커밋 메시지 생성에 실패했습니다.")
        sys.exit(1)

    print("[DONE] 커밋 메시지 생성 완료")
    print(f"[INFO] AI API 호출 횟수: {'0 (mock)' if client.is_mock else '1'}")
    print()
    print("--- Commit Message ---")
    print(result)
    print("----------------------")

    errors, warnings = validate_commit_message(result)
    print_validation(errors, warnings, "커밋 메시지")

    print("[INFO] 생성된 메시지는 초안입니다. 검토 후 적용하세요.")


def cmd_pr(args):
    """PR 제목/본문 자동 생성"""
    collector = GitCollector()

    if not collector.has_changes():
        print("[INFO] 변경 사항이 없습니다. PR 초안을 생성하지 않고 종료합니다.")
        return

    git_info = collector.collect()
    print(f"[INFO] 현재 브랜치: {git_info['branch']}")
    print(f"[INFO] Git status 수집 완료: {git_info['file_count']}개 파일 변경 감지")
    print(f"[INFO] Git diff 수집 완료: {git_info['diff_lines']}줄")

    prompt = build_pr_prompt(git_info, safe_mode=args.safe_mode)

    if args.mock:
        os.environ["AI_MOCK_MODE"] = "true"

    client = AIClient(temperature=args.temperature, max_tokens=args.max_tokens)
    result = client.generate_pr_draft(prompt, git_info)

    if result is None:
        print("[ERROR] PR 초안 생성에 실패했습니다.")
        sys.exit(1)

    print("[DONE] PR 초안 생성 완료")
    print(f"[INFO] AI API 호출 횟수: {'0 (mock)' if client.is_mock else '1'}")
    print()
    print("--- PR Draft ---")
    print(result)
    print("----------------")

    errors, warnings = validate_pr_draft(result)
    print_validation(errors, warnings, "PR 초안")

    print("[INFO] 생성된 PR 초안은 자동 적용되지 않습니다. 검토 후 적용하세요.")


def main():
    # .env 파일 자동 로딩 (.env.example을 .env로 복사 후 값만 수정하면 바로 작동)
    load_dotenv()
    
    parser = argparse.ArgumentParser(
        description="내가 고친 코드 설명을 AI가 대신 써주는 도우미",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
  python main.py commit                          # 커밋 메시지 생성 (NVIDIA NIM API 호출)
  python main.py pr                              # PR 제목/본문 생성
  python main.py commit --mock                   # mock 모드 (AI 없이 템플릿, 개발용)
  python main.py commit --safe-mode              # 민감정보 마스킹 + diff 제한
  python main.py commit --temperature 0.1        # 더 결정론적인 출력
  python main.py pr --max-tokens 1000            # 더 긴 출력 허용

NVIDIA NIM 설정 (.env 파일 사용):
  1. API Key 발급: https://build.nvidia.com → Settings → API Keys
  2. .env 파일 생성:
     cp .env.example .env
     # .env 파일에서 AI_API_KEY 값을 실제 NVIDIA NIM API Key(nvapi-...)로 수정
  3. 실행:
     python main.py commit

  또는 환경변수 직접 설정:
     export AI_API_KEY="nvapi-your_key"
     python main.py commit

환경변수:
  AI_API_KEY     NVIDIA NIM API Key (필수, nvapi-... 형식)
  AI_API_URL     API 엔드포인트 (기본: https://integrate.api.nvidia.com/v1/chat/completions)
  AI_MODEL       모델명 (기본: meta/llama-3.1-8b-instruct, 3초 응답. 70b, Phi-3 등 선택 가능)
  AI_MOCK_MODE   true 설정 시 mock 모드 (개발/테스트용)
""",
    )
    subparsers = parser.add_subparsers(dest="command", help="명령")

    def add_common_opts(p):
        p.add_argument("--mock", action="store_true", help="명시적 mock 모드 (AI API 호출 없이 템플릿 생성, 개발/테스트용)")
        p.add_argument("--safe-mode", action="store_true", help="민감정보 마스킹 + diff 제한")
        p.add_argument("--temperature", type=float, default=0.3, metavar="FLOAT",
                       help="AI API temperature (기본: 0.3, 낮을수록 결정론적)")
        p.add_argument("--max-tokens", type=int, default=500, metavar="INT",
                       help="AI API max_tokens (기본: 500, 출력 최대 길이)")

    commit_parser = subparsers.add_parser("commit", help="커밋 메시지 자동 생성")
    add_common_opts(commit_parser)
    commit_parser.set_defaults(func=cmd_commit)

    pr_parser = subparsers.add_parser("pr", help="PR 제목/본문 자동 생성")
    add_common_opts(pr_parser)
    pr_parser.set_defaults(func=cmd_pr)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    args.func(args)


if __name__ == "__main__":
    main()
