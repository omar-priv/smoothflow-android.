#!/usr/bin/env python3
"""Dependency-light, cross-language QA runner for Universal Code Lab."""
import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

SKIP = {".git", ".venv", "venv", "node_modules", "__pycache__", ".next", "dist", "build", "target", ".gradle", "vendor", ".universal-code-lab"}
MAX_OUTPUT = 10000


class Lab:
    def __init__(self, root, output, timeout):
        self.root = Path(root).resolve()
        self.output = Path(output).resolve()
        self.timeout = timeout
        self.results = []
        self.stacks = []

    def record(self, name, status, detail="", command=None, duration=0, output=""):
        self.results.append({"name": name, "status": status, "detail": detail,
                             "command": command or [], "duration_seconds": round(duration, 2),
                             "output": str(output)[-MAX_OUTPUT:]})
        print("[{}] {} — {}".format(status, name, detail))

    def run(self, name, cmd, timeout=None):
        if not shutil.which(cmd[0]):
            self.record(name, "SKIP", "Tool not installed: " + cmd[0], cmd)
            return False
        start = time.monotonic()
        try:
            p = subprocess.run(cmd, cwd=self.root, text=True, stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT, timeout=timeout or self.timeout,
                               env=dict(os.environ, CI="1"), check=False)
            status = "PASS" if p.returncode == 0 else "FAIL"
            detail = "exit code {}".format(p.returncode)
            if "unittest" in cmd and "Ran 0 tests" in (p.stdout or ""):
                status = "WARN"
                detail = "No unittest cases were discovered; this is not a test pass"
            self.record(name, status, detail, cmd, time.monotonic() - start, p.stdout or "")
            return status == "PASS"
        except subprocess.TimeoutExpired as e:
            out = e.stdout.decode("utf-8", "replace") if isinstance(e.stdout, bytes) else (e.stdout or "")
            self.record(name, "FAIL", "Timed out", cmd, time.monotonic() - start, out)
            return False
        except Exception as e:
            self.record(name, "FAIL", "Could not execute: {}".format(e), cmd, time.monotonic() - start)
            return False

    def files(self, pattern):
        return [p for p in self.root.rglob(pattern) if not any(part in SKIP for part in p.parts)]

    def check(self):
        py = self.files("*.py")
        if py:
            self.stacks.append("Python")
            syntax_errors = []
            for source_file in py:
                try:
                    compile(source_file.read_text(encoding="utf-8"), str(source_file), "exec")
                except Exception as exc:
                    syntax_errors.append("{}: {}".format(source_file.relative_to(self.root), exc))
            if syntax_errors:
                self.record("Python syntax", "FAIL", "\\n".join(syntax_errors))
            else:
                self.record("Python syntax", "PASS", "{} Python files parsed without execution".format(len(py)))
            if shutil.which("ruff"):
                self.run("Ruff lint", ["ruff", "check", str(self.root)])
            else:
                self.record("Ruff lint", "SKIP", "Install ruff for additional linting")
            if (self.root / "tests").exists() or (self.root / "pytest.ini").exists():
                if shutil.which("pytest"):
                    self.run("Pytest", ["pytest", "-q"], 300)
                else:
                    self.run("Python unittest", [sys.executable, "-m", "unittest", "discover", "-s", "tests"], 300)

        for p in self.files("*.json"):
            try:
                json.loads(p.read_text(encoding="utf-8"))
            except Exception as e:
                self.record("JSON parse: " + str(p.relative_to(self.root)), "FAIL", str(e))

        for p in self.files("*.toml"):
            try:
                import tomllib
                tomllib.loads(p.read_text(encoding="utf-8"))
            except ModuleNotFoundError:
                self.record("TOML parse", "SKIP", "Python 3.11+ required for built-in TOML parser")
                break
            except Exception as e:
                self.record("TOML parse: " + str(p.relative_to(self.root)), "FAIL", str(e))

        yaml_files = self.files("*.yml") + self.files("*.yaml")
        if yaml_files:
            try:
                import yaml
                for p in yaml_files:
                    try:
                        list(yaml.safe_load_all(p.read_text(encoding="utf-8")))
                    except Exception as e:
                        self.record("YAML parse: " + str(p.relative_to(self.root)), "FAIL", str(e))
            except ImportError:
                self.record("YAML parse", "SKIP", "Install PyYAML to validate YAML syntax")

        pkg_path = self.root / "package.json"
        if pkg_path.exists():
            self.stacks.append("JavaScript/TypeScript")
            try:
                pkg = json.loads(pkg_path.read_text(encoding="utf-8"))
                scripts = pkg.get("scripts", {})
                if not (self.root / "node_modules").exists():
                    self.record("JavaScript scripts", "SKIP", "Install project dependencies first")
                else:
                    manager = "pnpm" if (self.root / "pnpm-lock.yaml").exists() else ("yarn" if (self.root / "yarn.lock").exists() else "npm")
                    for key in ("lint", "typecheck", "check", "test", "build"):
                        if key in scripts:
                            self.run("JavaScript " + key, [manager, "run", key], 300)
                if (self.root / "tsconfig.json").exists():
                    if shutil.which("tsc"):
                        self.run("TypeScript compiler", ["tsc", "--noEmit"], 300)
                    else:
                        self.record("TypeScript compiler", "SKIP", "tsc not installed")
            except Exception as e:
                self.record("package.json", "FAIL", str(e))

        if (self.root / "go.mod").exists():
            self.stacks.append("Go")
            self.run("Go tests", ["go", "test", "./..."], 300)
            self.run("Go vet", ["go", "vet", "./..."], 300)

        if (self.root / "Cargo.toml").exists():
            self.stacks.append("Rust")
            self.run("Rust formatting", ["cargo", "fmt", "--all", "--", "--check"], 300)
            self.run("Rust tests", ["cargo", "test", "--workspace"], 600)
            self.run("Rust Clippy", ["cargo", "clippy", "--workspace", "--all-targets", "--", "-D", "warnings"], 600)

        if any((self.root / n).exists() for n in ("pom.xml", "build.gradle", "build.gradle.kts", "gradlew", "mvnw")):
            self.stacks.append("Java/JVM")
            if (self.root / "mvnw").exists() and os.name != "nt":
                self.run("Maven tests", ["./mvnw", "-B", "test"], 600)
            elif (self.root / "gradlew").exists() and os.name != "nt":
                self.run("Gradle tests", ["./gradlew", "test"], 600)
            elif (self.root / "pom.xml").exists():
                self.run("Maven tests", ["mvn", "-B", "test"], 600)
            else:
                self.run("Gradle tests", ["gradle", "test"], 600)

        if list(self.root.glob("*.sln")) or list(self.root.glob("*.csproj")):
            self.stacks.append(".NET")
            self.run(".NET tests", ["dotnet", "test"], 600)

        if (self.root / "composer.json").exists():
            self.stacks.append("PHP")
            self.run("Composer validation", ["composer", "validate", "--no-check-publish"], 300)
            if (self.root / "vendor/bin/phpunit").exists():
                self.run("PHPUnit", ["vendor/bin/phpunit"], 300)

        if (self.root / "Gemfile").exists():
            self.stacks.append("Ruby")
            self.run("Bundler check", ["bundle", "check"], 300)

        shell_files = self.files("*.sh")
        if shell_files:
            self.stacks.append("Shell")
            for p in shell_files:
                self.run("Shell syntax " + str(p.relative_to(self.root)), ["bash", "-n", str(p)])

        if (self.root / "Dockerfile").exists():
            self.stacks.append("Docker")
            self.run("Docker build", ["docker", "build", "-t", "universal-code-lab-check", str(self.root)], 900)

        # Optional security scanners: only run when explicitly available in the environment.
        if shutil.which("gitleaks"):
            self.run("Gitleaks secret scan", ["gitleaks", "detect", "--source", str(self.root), "--no-git", "--redact"], 300)
        else:
            self.record("Gitleaks secret scan", "SKIP", "Install Gitleaks for secret scanning")
        if shutil.which("semgrep"):
            self.run("Semgrep security scan", ["semgrep", "scan", "--config", "auto", "--error", str(self.root)], 600)
        else:
            self.record("Semgrep security scan", "SKIP", "Install Semgrep for static security analysis")
        if (self.root / "requirements.txt").exists() and shutil.which("pip-audit"):
            self.run("Python dependency audit", ["pip-audit", "-r", str(self.root / "requirements.txt")], 300)

        if not self.stacks:
            self.record("Stack detection", "WARN", "No supported project manifest detected")

    def report(self):
        self.output.mkdir(parents=True, exist_ok=True)
        counts = {s: sum(x["status"] == s for x in self.results) for s in ("PASS", "FAIL", "WARN", "SKIP")}
        status = "FAIL" if counts["FAIL"] else ("PASS WITH WARNINGS" if counts["WARN"] or counts["SKIP"] else "PASS")
        data = {"lab": "Universal Code Lab", "version": "1.0.0", "root": str(self.root),
                "stacks": sorted(set(self.stacks)), "overall": status, "counts": counts,
                "results": self.results,
                "limitations": ["Only available checks were executed.",
                                "Passing checks do not prove absence of bugs or exhaustive branch coverage.",
                                "External services, credentials, real devices, and production systems are not verified unless project tests cover them."]}
        (self.output / "report.json").write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        lines = ["# Universal Code Lab report", "", "**Overall:** " + status,
                 "", "**Stacks:** " + (", ".join(data["stacks"]) or "None"), "",
                 "| Status | Count |", "|---|---:|"]
        lines += ["| {} | {} |".format(k, v) for k, v in counts.items()]
        for r in self.results:
            lines += ["", "## {} — {}".format(r["status"], r["name"]), "", r["detail"]]
            if r["command"]:
                lines += ["", "Command: " + " ".join(r["command"])]
            if r["output"].strip():
                lines += ["", "Output:", r["output"][-4000:]]
        lines += ["", "## Limitations"] + ["- " + x for x in data["limitations"]]
        (self.output / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
        print("Reports saved in " + str(self.output))
        print("Overall: " + status)
        return counts["FAIL"] == 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--output", default=".lab-report")
    ap.add_argument("--timeout", type=int, default=180)
    args = ap.parse_args()
    root = Path(args.root)
    if not root.is_dir():
        print("Project root does not exist: " + str(root), file=sys.stderr)
        return 2
    lab = Lab(root, args.output, args.timeout)
    lab.check()
    return 0 if lab.report() else 1


if __name__ == "__main__":
    raise SystemExit(main())
