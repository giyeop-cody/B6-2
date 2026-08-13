"""AI 클라이언트 모듈

제약사항 준수:
- AI API Key는 환경변수(AI_API_KEY)로만 관리, 코드에 하드코딩 금지
- API Key 미설정 시 에러 메시지 출력 후 종료
- 1회 실행 = 1회 API 호출

AI API: NVIDIA NIM
- 인증: NVIDIA NIM API Key (nvapi-...)
- 엔드포인트: https://integrate.api.nvidia.com/v1/chat/completions
- 모델: meta/llama-3.1-8b-instruct (기본, 3초 응답)

핵심: AI에게 JSON 스키마를 전달하고, JSON으로 응답받아 파싱합니다.
"""
import os
import json
import re


class AIClient:
    """AI API 클라이언트 (NVIDIA NIM)"""

    def __init__(self, temperature=0.3, max_tokens=500):
        self.api_key = os.environ.get("AI_API_KEY", "")
        self.api_url = os.environ.get("AI_API_URL", "https://integrate.api.nvidia.com/v1/chat/completions")
        self.model = os.environ.get("AI_MODEL", "meta/llama-3.1-8b-instruct")
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.is_mock = os.environ.get("AI_MOCK_MODE", "").lower() in ("true", "1", "yes")

    def _check_key(self):
        """API Key 설정 여부 확인 (제약사항: 환경변수로만 관리)"""
        if not self.api_key:
            print("[ERROR] AI_API_KEY 환경변수가 설정되지 않았습니다.")
            print('  예) export AI_API_KEY="nvapi-your_nvidia_nim_api_key"')
            print("  API Key 발급: https://build.nvidia.com → Settings → API Keys")
            return False
        return True

    def _call_real_api(self, prompt, system_prompt):
        """AI API 호출 → raw 텍스트 반환"""
        try:
            import requests
        except ImportError:
            print("[ERROR] requests 패키지가 필요합니다: pip install requests")
            return None

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        try:
            print(f"[INFO] AI API 요청 중... (model={self.model}, temperature={self.temperature}, max_tokens={self.max_tokens})")
            resp = requests.post(self.api_url, json=payload, headers=headers, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"].strip()
        except requests.exceptions.Timeout:
            print("[ERROR] AI API 요청 시간 초과 (30s)")
            return None
        except requests.exceptions.ConnectionError:
            print(f"[ERROR] AI API 연결 실패: {self.api_url}")
            return None
        except Exception as e:
            print(f"[ERROR] AI API 오류: {e}")
            return None

    def _parse_commit_from_text(self, text):
        """AI가 JSON 대신 텍스트로 응답한 경우, 텍스트에서 커밋 메시지 구조 추출

        예: "feat: 계산기 추가\n\n- 뺄셈 추가\n- 곱셈 추가"
        → {"type": "feat", "subject": "계산기 추가", "body_points": ["뺄셈 추가", "곱셈 추가"]}
        """
        lines = text.strip().split("\n")
        if not lines:
            return None

        # 첫 줄에서 type: subject 추출
        first_line = lines[0].strip()
        match = re.match(r"^(feat|fix|docs|refactor|test|chore|style|perf|ci|build)[\s:]*(.+)", first_line, re.IGNORECASE)
        if match:
            commit_type = match.group(1).lower()
            subject = match.group(2).strip().strip("`*")
        else:
            # type 없으면 전체를 subject로
            commit_type = "fix"
            subject = first_line[:50]

        # bullet points 추출
        body_points = []
        for line in lines[1:]:
            line = line.strip()
            if line.startswith("- "):
                body_points.append(line[2:].strip())
            elif line.startswith("* "):
                body_points.append(line[2:].strip())
            elif line and not line.startswith("```") and not line.startswith("#"):
                # 빈 줄이 아닌 일반 텍스트도 bullet으로
                if not line.startswith("---"):
                    body_points.append(line)

        if not body_points:
            body_points = ["변경 사항 적용"]

        return {
            "type": commit_type,
            "subject": subject,
            "body_points": body_points[:3],  # 최대 3개
        }

    def _parse_pr_from_text(self, text):
        """AI가 JSON 대신 마크다운 텍스트로 응답한 경우, 텍스트에서 PR 구조 추출

        예: "## PR Title\nfeat: xxx\n\n## PR Body\n### Why\n- 이유1\n\n### What\n- 변경1"
        → {"title": "feat: xxx", "why": ["이유1"], "what": ["변경1"], "how_to_test": [...]}
        """
        title = ""
        why = []
        what = []
        how_to_test = []

        # 섹션별로 분할
        current_section = None
        for line in text.split("\n"):
            line = line.strip()

            if "PR Title" in line or line.startswith("feat:") or line.startswith("fix:") or line.startswith("docs:"):
                if not title and ":" in line and not line.startswith("#"):
                    title = line.strip("`*")
                elif not title and line.startswith("#"):
                    pass  # 헤더 무시
                elif not title:
                    title = line

            elif "### Why" in line or line.lower().startswith("why"):
                current_section = "why"
            elif "### What" in line or line.lower().startswith("what"):
                current_section = "what"
            elif "### How" in line or "how to test" in line.lower():
                current_section = "how_to_test"
            elif line.startswith("- ") or line.startswith("* "):
                point = line[2:].strip()
                if current_section == "why":
                    why.append(point)
                elif current_section == "what":
                    what.append(point)
                elif current_section == "how_to_test":
                    how_to_test.append(point)
            elif line and not line.startswith("#") and not line.startswith("```") and current_section:
                # 일반 텍스트도 bullet으로
                point = line
                if current_section == "why":
                    why.append(point)
                elif current_section == "what":
                    what.append(point)
                elif current_section == "how_to_test":
                    how_to_test.append(point)

        # title이 없으면 첫 줄에서 추출
        if not title:
            for line in text.split("\n"):
                line = line.strip()
                if line and not line.startswith("#") and not line.startswith("```"):
                    title = line[:80]
                    break

        if not title:
            title = "feat: 변경 사항"

        if not why:
            why = ["변경 배경 명시 필요"]
        if not what:
            what = ["구체적 변경 내용 명시 필요"]
        if not how_to_test:
            how_to_test = ["테스트 방법 명시 필요"]

        return {
            "title": title,
            "why": why,
            "what": what,
            "how_to_test": how_to_test,
        }

    def _extract_json(self, text):
        """AI 응답 텍스트에서 JSON 추출

        AI가 JSON 외 텍스트를 섞어서 반환할 수 있으므로,
        텍스트에서 JSON 부분만 추출합니다.
        """
        # 1. 순수 JSON인 경우
        text = text.strip()
        if text.startswith("{") and text.endswith("}"):
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                pass

        # 2. 마크다운 코드 블록 안에 JSON이 있는 경우
        match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass

        # 3. 텍스트 중간에서 JSON 객체 추출 (중첩 허용)
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass

        return None

    def _generate_mock_commit(self, git_info):
        """Mock: 커밋 메시지 JSON 생성 (--mock 모드)"""
        files = git_info.get("changed_files", [])
        file_count = git_info.get("file_count", 0)
        diff_lines = git_info.get("diff_lines", 0)

        diff = git_info.get("diff", "")
        has_new_file = "new file mode" in diff
        has_deleted = "deleted file mode" in diff
        has_test = any("test" in f.lower() for f in files)

        if has_new_file:
            commit_type = "feat"
            subject = "신규 파일 추가"
        elif has_deleted:
            commit_type = "chore"
            subject = "파일 삭제"
        elif has_test:
            commit_type = "test"
            subject = "테스트 코드 수정"
        elif any(f.endswith(".md") for f in files):
            commit_type = "docs"
            subject = "문서 수정"
        else:
            commit_type = "fix"
            subject = "코드 수정"

        file_list = ", ".join(files[:5])
        if file_count > 5:
            file_list += f" 외 {file_count - 5}개"

        return {
            "type": commit_type,
            "subject": f"{subject} ({file_count}개 파일)",
            "body_points": [
                f"{file_list} 변경 ({diff_lines}줄 diff)",
                "자동 생성된 커밋 메시지 (mock 모드)",
                "실제 AI 연결 시 더 정밀한 분석 제공",
            ],
        }

    def _generate_mock_pr(self, git_info):
        """Mock: PR 제목/본문 JSON 생성 (--mock 모드)"""
        branch = git_info.get("branch", "unknown")
        files = git_info.get("changed_files", [])
        file_count = git_info.get("file_count", 0)
        diff_lines = git_info.get("diff_lines", 0)
        file_list = ", ".join(files[:5])
        if file_count > 5:
            file_list += f" 외 {file_count - 5}개"

        return {
            "title": f"feat: {branch} 브랜치 변경 사항 ({file_count}개 파일)",
            "why": [
                "코드 변경 사항을 체계적으로 관리하고 리뷰 효율을 높이기 위해 PR을 생성했습니다.",
            ],
            "what": [
                f"{file_list} 변경 ({diff_lines}줄 diff)",
                "자동 생성된 PR 초안 (mock 모드)",
            ],
            "how_to_test": [
                '환경변수 설정: export AI_API_KEY="nvapi-your_key"',
                "커밋 메시지 생성: python main.py commit",
                "PR 초안 생성: python main.py pr",
            ],
        }

    def generate_commit_message(self, prompt, git_info):
        """커밋 메시지 생성 → JSON dict 반환

        반환: {"type": str, "subject": str, "body_points": list[str]}

        흐름:
        1. AI에게 JSON 스키마와 함께 프롬프트 전달
        2. AI 응답에서 JSON 추출
        3. JSON 추출 실패 시 텍스트에서 구조 파싱 (fallback)
        4. 파싱된 dict 반환 → main.py에서 양식에 맞게 조립
        """
        if self.is_mock:
            print("[INFO] Mock 모드로 커밋 메시지 생성 (--mock 또는 AI_MOCK_MODE=true)")
            return self._generate_mock_commit(git_info)
        if not self._check_key():
            return None

        system_prompt = (
            "당신은 Git 커밋 메시지 작성 전문가입니다. "
            "변경 사항을 분석해 간결한 커밋 메시지를 작성하세요. "
            "반드시 요청된 JSON 형식으로만 응답하세요. "
            "JSON 외의 설명, 인사, 마크다운은 절대 출력하지 마세요."
        )
        raw = self._call_real_api(prompt, system_prompt)
        if raw is None:
            return None

        # 1차: JSON 추출 시도
        parsed = self._extract_json(raw)
        if parsed is not None:
            if "type" not in parsed or "subject" not in parsed:
                print("[WARN] AI 응답 JSON에 필수 필드가 없어 텍스트 파싱으로 전환합니다.")
                parsed = self._parse_commit_from_text(raw)
            else:
                if "body_points" not in parsed:
                    parsed["body_points"] = []
                return parsed

        # 2차: JSON 추출 실패 → 텍스트에서 구조 파싱
        if parsed is None:
            print("[WARN] AI가 JSON 대신 텍스트로 응답하여 텍스트에서 파싱합니다.")
            parsed = self._parse_commit_from_text(raw)

        if parsed is None:
            print("[ERROR] AI 응답에서 커밋 메시지를 추출할 수 없습니다.")
            print(f"[DEBUG] AI 응답 (앞 200자): {raw[:200]}")
            return None

        return parsed

    def generate_pr_draft(self, prompt, git_info):
        """PR 초안 생성 → JSON dict 반환

        반환: {"title": str, "why": list[str], "what": list[str], "how_to_test": list[str]}

        흐름:
        1. AI에게 JSON 스키마와 함께 프롬프트 전달
        2. AI 응답에서 JSON 추출
        3. JSON 추출 실패 시 마크다운 텍스트에서 구조 파싱 (fallback)
        4. 파싱된 dict 반환 → main.py에서 양식에 맞게 조립
        """
        if self.is_mock:
            print("[INFO] Mock 모드로 PR 초안 생성 (--mock 또는 AI_MOCK_MODE=true)")
            return self._generate_mock_pr(git_info)
        if not self._check_key():
            return None

        system_prompt = (
            "당신은 PR 작성 전문가입니다. "
            "Why/What/How to Test 구조로 PR 본문을 작성하세요. "
            "반드시 요청된 JSON 형식으로만 응답하세요. "
            "JSON 외의 설명, 인사, 마크다운은 절대 출력하지 마세요."
        )
        raw = self._call_real_api(prompt, system_prompt)
        if raw is None:
            return None

        # 1차: JSON 추출 시도
        parsed = self._extract_json(raw)
        if parsed is not None:
            if "title" not in parsed:
                print("[WARN] AI 응답 JSON에 필수 필드(title)가 없어 텍스트 파싱으로 전환합니다.")
                parsed = self._parse_pr_from_text(raw)
            else:
                for field in ["why", "what", "how_to_test"]:
                    if field not in parsed:
                        parsed[field] = []
                return parsed

        # 2차: JSON 추출 실패 → 마크다운 텍스트에서 구조 파싱
        if parsed is None:
            print("[WARN] AI가 JSON 대신 마크다운으로 응답하여 텍스트에서 파싱합니다.")
            parsed = self._parse_pr_from_text(raw)

        if parsed is None:
            print("[ERROR] AI 응답에서 PR 초안을 추출할 수 없습니다.")
            print(f"[DEBUG] AI 응답 (앞 200자): {raw[:200]}")
            return None

        return parsed
