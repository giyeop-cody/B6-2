"""
민감정보 마스킹 모듈 (제약사항: 보안/safe-mode)
- diff에서 API Key, 이메일, 비밀번호 등 민감정보를 마스킹
- -safe-mode 옵션: (A) 패턴 마스킹 + (B) diff 일부만 전송
"""
import re

# 마스킹할 패턴들
PATTERNS = [
    # API Key 형태 (sk-xxx, ghp_xxx, sb_publishable_xxx 등)
    (re.compile(r'(sk-[a-zA-Z0-9]{20,})'), 'sk-***MASKED***'),
    (re.compile(r'(ghp_[a-zA-Z0-9]{36})'), 'ghp_***MASKED***'),
    (re.compile(r'(sb_publishable_[a-zA-Z0-9]+)'), 'sb_publishable_***MASKED***'),
    (re.compile(r'(sb_secret_[a-zA-Z0-9]+)'), 'sb_secret_***MASKED***'),
    # 이메일
    (re.compile(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'), '***@***.***'),
    # 비밀번호 관련 (password=xxx, pwd=xxx, secret=xxx)
    (re.compile(r'((?:password|passwd|pwd|secret|token|api_key)\s*[=:]\s*["\']?)([^\s"\']{4,})', re.IGNORECASE),
     r'\1***MASKED***'),
    # JWT 토큰 (eyJ... 시작)
    (re.compile(r'(eyJ[a-zA-Z0-9_-]{10,}\.eyJ[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]+)'), '***JWT_MASKED***'),
    # AWS 키
    (re.compile(r'(AKIA[0-9A-Z]{16})'), 'AKIA***MASKED***'),
    # 전화번호 (한국)
    (re.compile(r'(\d{2,3}-\d{3,4}-\d{4})'), '**-****-****'),
]


def mask_sensitive(text):
    """텍스트에서 민감정보 패턴을 마스킹"""
    masked = text
    for pattern, replacement in PATTERNS:
        masked = pattern.sub(replacement if isinstance(replacement, str) else replacement, masked)
    return masked


def truncate_diff(diff, max_files=10, max_lines=200):
    """diff를 파일 수/줄 수로 제한 (safe-mode 옵션 B)
    - max_files: 최대 파일 수
    - max_lines: 최대 줄 수
    """
    if not diff:
        return diff

    lines = diff.splitlines()
    result = []
    file_count = 0
    line_count = 0

    for line in lines:
        if line.startswith("diff --git"):
            file_count += 1
            if file_count > max_files:
                result.append(f"\n... ({file_count - max_files}개 파일 생략, safe-mode 최대 {max_files}파일)")
                break

        result.append(line)
        line_count += 1

        if line_count >= max_lines:
            result.append(f"\n... ({line_count}줄 이후 생략, safe-mode 최대 {max_lines}줄)")
            break

    return "\n".join(result)


def sanitize_diff(diff, safe_mode=False, max_files=10, max_lines=200):
    """diff에서 민감정보를 제거하고 필요시 일부만 전송
    - safe_mode=False: 패턴 마스킹만 수행 (기본)
    - safe_mode=True: 패턴 마스킹 + 파일/줄 수 제한
    """
    # 항상 패턴 마스킹 수행 (제약사항: 민감정보는 프롬프트에 포함 금지)
    result = mask_sensitive(diff)

    if safe_mode:
        result = truncate_diff(result, max_files, max_lines)

    return result
