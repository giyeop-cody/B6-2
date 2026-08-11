"""
AI 클라이언트 모듈

제약사항 준수:
- AI API Key는 환경변수(AI_API_KEY)로만 관리, 코드에 하드코딩 금지
- API Key 미설정 시 에러 메시지 출력 후 종료
- 1회 실행 = 1회 API 호출

AI API: NVIDIA NIM
- 인증: NVIDIA NIM API Key (nvapi-...)
- 엔드포인트: https://integrate.api.nvidia.com/v1/chat/completions
- 모델: meta/llama-3.1-8b-instruct (기본, 3초 응답), llama-3.3-70b, Phi-3 등 선택 가능
- 무료 (1,000 credits, 40 RPM), 신용카드 불필요

환경변수:
  AI_API_KEY    NVIDIA NIM API Key (필수, nvapi-... 형식)
  AI_API_URL    API 엔드포인트 (기본: NVIDIA NIM)
  AI_MODEL      모델명 (기본: meta/llama-3.1-8b-instruct)
  AI_MOCK_MODE  true 설정 시 mock 모드 (개발/테스트용)
"""
import os
import json


class AIClient:
    """AI API 클라이언트 (NVIDIA NIM — )"""

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

    def _call_real_api(self, prompt, system_prompt="You are a helpful assistant."):
        """AI API 호출 (NVIDIA NIM — NVIDIA NIM API 포맷)

        temperature 영향:
        - 0.0~0.2: 결정론적, 같은 입력에 거의 같은 출력 (커밋 메시지에 적합)
        - 0.3~0.5: 약간의 변형, 자연스러운 문장 (기본값)
        - 0.7~1.0: 창의적, 다양한 표현 (PR 본문에 적합할 수 있으나 일관성 저하)

        max_tokens 영향:
        - 200: 매우 짧은 출력 (커밋 메시지 1줄용)
        - 500: 표준 (커밋 메시지 + 본문, 기본값)
        - 1000+: PR 본문용 (Why/What/How 구조 모두 표현)
        - 주의: 토큰 한계 도달 시 출력이 중간에 잘릴 수 있음 (절단 위험)
        """
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

    def _generate_mock_commit(self, git_info):
        """Mock: 커밋 메시지 템플릿 생성 (--mock 모드, 개발/테스트용)"""
        files = git_info.get("changed_files", [])
        file_count = git_info.get("file_count", 0)
        diff_lines = git_info.get("diff_lines", 0)

        types = set()
        for f in files:
            if f.endswith(".py"): types.add("Python")
            elif f.endswith(".js") or f.endswith(".jsx"): types.add("JavaScript")
            elif f.endswith(".md"): types.add("문서")
            elif f.endswith(".yml") or f.endswith(".yaml"): types.add("설정")
            elif "test" in f.lower(): types.add("테스트")
            else: types.add("기타")
        type_str = "/".join(sorted(types))

        diff = git_info.get("diff", "")
        has_new_file = "new file mode" in diff
        has_deleted = "deleted file mode" in diff
        has_test = any("test" in f.lower() for f in files)

        if has_new_file: prefix, desc = "feat", "신규 파일 추가"
        elif has_deleted: prefix, desc = "chore", "파일 삭제"
        elif has_test: prefix, desc = "test", "테스트 코드 수정"
        elif any(f.endswith(".md") for f in files): prefix, desc = "docs", "문서 수정"
        else: prefix, desc = "fix", "코드 수정"

        file_list = ", ".join(files[:5])
        if file_count > 5: file_list += f" 외 {file_count - 5}개"

        return f"""{prefix}: {desc} ({type_str} 파일 {file_count}개 변경)

- {file_list} 변경 ({diff_lines}줄 diff)
- 자동 생성된 커밋 메시지 (mock 모드)
- 실제 AI 연결 시 더 정밀한 분석 제공"""

    def _generate_mock_pr(self, git_info):
        """Mock: PR 제목/본문 템플릿 생성 (--mock 모드, 개발/테스트용)"""
        branch = git_info.get("branch", "unknown")
        files = git_info.get("changed_files", [])
        file_count = git_info.get("file_count", 0)
        diff_lines = git_info.get("diff_lines", 0)
        file_list = ", ".join(files[:5])
        if file_count > 5: file_list += f" 외 {file_count - 5}개"

        return f"""## PR Title
feat: {branch} 브랜치 변경 사항 ({file_count}개 파일)

## PR Body
### Why
- 코드 변경 사항을 체계적으로 관리하고 리뷰 효율을 높이기 위해 PR을 생성했습니다.

### What
- {file_list} 변경 ({diff_lines}줄 diff)
- 자동 생성된 PR 초안 (mock 모드)

### How to Test
- 환경변수 설정: export AI_API_KEY="nvapi-your_key"
- 커밋 메시지 생성: python main.py commit
- PR 초안 생성: python main.py pr"""

    def generate_commit_message(self, prompt, git_info):
        """커밋 메시지 생성 (mock or real)"""
        if self.is_mock:
            print("[INFO] Mock 모드로 커밋 메시지 생성 (--mock 또는 AI_MOCK_MODE=true)")
            return self._generate_mock_commit(git_info)
        if not self._check_key():
            return None
        return self._call_real_api(prompt, "당신은 Git 커밋 메시지 작성 전문가입니다. 변경 사항을 분석해 간결한 커밋 메시지를 작성하세요.")

    def generate_pr_draft(self, prompt, git_info):
        """PR 초안 생성 (mock or real)"""
        if self.is_mock:
            print("[INFO] Mock 모드로 PR 초안 생성 (--mock 또는 AI_MOCK_MODE=true)")
            return self._generate_mock_pr(git_info)
        if not self._check_key():
            return None
        return self._call_real_api(prompt, "당신은 PR 작성 전문가입니다. Why/What/How to Test 구조로 PR 본문을 작성하세요.")
