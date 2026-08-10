"""
출력 검증 모듈 (사전평가 #7 보완)
- 커밋 메시지: 제목 길이(50자), type 접두사, 본문 bullet point 확인
- PR 초안: Title/Body 섹션, Why/What/How to Test 섹션 존재 확인
- 검증 실패 시 경고 메시지 출력 (자동 수정 아님 — 사용자 검토 유도)
"""


def validate_commit_message(message):
    """커밋 메시지 형식 검증
    규칙:
    1. 첫 줄이 '<type>: <요약>' 형식 (feat/fix/docs/refactor/test/chore)
    2. 제목(첫 줄)이 50자 이내
    3. 본문에 bullet point(-)가 최소 1개 이상
    """
    errors = []
    warnings = []

    if not message or not message.strip():
        errors.append("빈 메시지입니다.")
        return errors, warnings

    lines = message.strip().splitlines()
    first_line = lines[0].strip() if lines else ""

    # 1. type 접두사 확인
    valid_types = ["feat", "fix", "docs", "refactor", "test", "chore", "style", "perf", "ci", "build"]
    has_type = any(first_line.startswith(f"{t}:") for t in valid_types)
    if not has_type:
        errors.append(f"제목이 '<type>: <요약>' 형식이 아닙니다. (현재: '{first_line[:30]}') "
                       f"유효한 type: {', '.join(valid_types)}")

    # 2. 제목 길이 확인 (50자 이내 권장)
    if len(first_line) > 50:
        warnings.append(f"제목이 50자를 초과합니다. ({len(first_line)}자) "
                         f"간결하게 요약하는 것을 권장합니다.")

    # 3. 본문 bullet point 확인
    body_lines = lines[1:] if len(lines) > 1 else []
    has_bullets = any(line.strip().startswith("- ") for line in body_lines)
    if body_lines and not has_bullets:
        warnings.append("본문에 bullet point('- ')가 없습니다. 변경 내용을 bullet으로 요약하는 것을 권장합니다.")

    # 4. 본문 길이 확인
    if len(body_lines) > 10:
        warnings.append(f"본문이 {len(body_lines)}줄로 다소 깁니다. 3~5줄을 권장합니다.")

    return errors, warnings


def validate_pr_draft(draft):
    """PR 초안 형식 검증
    규칙:
    1. '## PR Title' 섹션 존재
    2. '## PR Body' 섹션 존재
    3. '### Why' 섹션 존재
    4. '### What' 섹션 존재
    5. '### How to Test' 섹션 존재
    """
    errors = []
    warnings = []

    if not draft or not draft.strip():
        errors.append("빈 PR 초안입니다.")
        return errors, warnings

    draft_stripped = draft.strip()

    # 필수 섹션 확인
    required_sections = {
        "## PR Title": "PR 제목 섹션이 없습니다.",
        "## PR Body": "PR 본문 섹션이 없습니다.",
        "### Why": "'### Why' 섹션이 없습니다. 변경 배경/목적을 작성해야 합니다.",
        "### What": "'### What' 섹션이 없습니다. 구체적인 변경 내용을 작성해야 합니다.",
        "### How to Test": "'### How to Test' 섹션이 없습니다. 테스트 방법을 작성해야 합니다.",
    }

    for section, error_msg in required_sections.items():
        if section not in draft_stripped:
            errors.append(error_msg)

    # PR Title 아래 내용 확인 (제목이 비어있지 않은지)
    lines = draft_stripped.splitlines()
    title_idx = -1
    for i, line in enumerate(lines):
        if line.strip() == "## PR Title":
            title_idx = i
            break

    if title_idx >= 0:
        # Title 다음 줄이 비어있거나 다음 섹션이면 제목 없음
        title_content = ""
        for line in lines[title_idx + 1:]:
            if line.strip().startswith("##"):
                break
            if line.strip():
                title_content = line.strip()
                break
        if not title_content:
            warnings.append("PR Title이 비어있습니다. 제목을 입력해주세요.")

    # Why/What 아래 bullet point 확인
    for section in ["### Why", "### What"]:
        if section in draft_stripped:
            section_idx = -1
            for i, line in enumerate(lines):
                if line.strip() == section:
                    section_idx = i
                    break
            if section_idx >= 0:
                section_bullets = False
                for line in lines[section_idx + 1:]:
                    if line.strip().startswith("##") or line.strip().startswith("###"):
                        break
                    if line.strip().startswith("- "):
                        section_bullets = True
                        break
                if not section_bullets:
                    warnings.append(f"{section} 섹션에 bullet point가 없습니다. 변경 내용을 bullet으로 작성하는 것을 권장합니다.")

    return errors, warnings


def print_validation(errors, warnings, output_type="커밋 메시지"):
    """검증 결과 출력"""
    if not errors and not warnings:
        print(f"[VALIDATION] {output_type} 형식 검증 통과 ✅")
        return True

    if errors:
        print(f"[VALIDATION] {output_type} 형식 오류 ({len(errors)}개):")
        for e in errors:
            print(f"  ❌ {e}")

    if warnings:
        print(f"[VALIDATION] {output_type} 형식 경고 ({len(warnings)}개):")
        for w in warnings:
            print(f"  ⚠️ {w}")

    print("[VALIDATION] 검증 결과를 참고하여 초안을 수정 후 적용하세요.")
    return len(errors) == 0
