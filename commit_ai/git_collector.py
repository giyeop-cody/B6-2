"""
Git 변경 사항 수집 모듈
- git status: 변경된 파일 목록
- git diff: 실제 변경 내용
- 제약: git status, git diff 범위로 제한 (push/PR API 구현 안 함)
"""
import subprocess
import os


class GitCollector:
    """Git 변경 사항을 수집하는 클래스"""

    def __init__(self, repo_path=None):
        self.repo_path = repo_path or os.getcwd()

    def _run_git(self, args):
        """git 명령어 실행 후 stdout 반환"""
        result = subprocess.run(
            ["git"] + args,
            cwd=self.repo_path,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(f"git {' '.join(args)} 실패: {result.stderr.strip()}")
        return result.stdout.strip()

    def get_status(self):
        """git status --short 결과 반환"""
        return self._run_git(["status", "--short"])

    def get_diff(self, staged=False):
        """git diff 결과 반환
        staged=True면 --cached, False면 working tree diff
        """
        args = ["diff"]
        if staged:
            args.append("--cached")
        return self._run_git(args)

    def get_all_diff(self):
        """staged + unstaged diff를 모두 수집

        HEAD 기준으로 diff를 수집하되, 커밋이 없는 빈 레포에서는
        git diff HEAD가 실패하므로 fallback 처리합니다.
        """
        try:
            return self._run_git(["diff", "HEAD"])
        except RuntimeError:
            # HEAD가 없는 경우 (커밋이 없는 빈 레포)
            # staged diff + unstaged diff를 따로 수집해서 합침
            parts = []
            try:
                staged = self._run_git(["diff", "--cached"])
                if staged:
                    parts.append(staged)
            except RuntimeError:
                pass
            try:
                unstaged = self._run_git(["diff"])
                if unstaged:
                    parts.append(unstaged)
            except RuntimeError:
                pass
            return "\n".join(parts)

    def get_branch(self):
        """현재 브랜치명 반환

        커밋이 없는 빈 레포에서 HEAD가 없으므로 fallback 처리합니다.
        """
        try:
            return self._run_git(["rev-parse", "--abbrev-ref", "HEAD"])
        except RuntimeError:
            # HEAD가 없는 경우 (빈 레포)
            return "(no commits yet)"

    def get_changed_files(self):
        """변경된 파일 목록 반환 (git status --short 파싱)"""
        status = self.get_status()
        if not status:
            return []
        files = []
        for line in status.splitlines():
            # XY filename 형식 (X=staged, Y=working tree)
            if len(line) >= 3:
                files.append(line[3:].strip())
        return files

    def has_changes(self):
        """변경 사항 존재 여부"""
        return bool(self.get_status().strip())

    def get_diff_stat(self):
        """diff 통계 (파일 수, 줄 수)"""
        diff = self.get_diff()
        if not diff:
            return 0, 0
        files = set()
        lines = 0
        for line in diff.splitlines():
            if line.startswith("diff --git"):
                files.add(line)
            if line.startswith("+") or line.startswith("-"):
                if not line.startswith("+++") and not line.startswith("---"):
                    lines += 1
        return len(files), lines

    def collect(self, staged=False):
        """모든 변경 사항을 딕셔너리로 수집
        staged=False: HEAD 기준 모든 diff (staged + unstaged)
        staged=True: --cached만
        """
        changed_files = self.get_changed_files()
        file_count = len(changed_files)
        if staged:
            diff = self.get_diff(staged=True)
        else:
            diff = self.get_all_diff()
        diff_lines = len(diff.splitlines()) if diff else 0
        branch = self.get_branch()

        return {
            "branch": branch,
            "changed_files": changed_files,
            "file_count": file_count,
            "diff": diff,
            "diff_lines": diff_lines,
            "status": self.get_status(),
        }
