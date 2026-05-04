#!/usr/bin/env bash
set -euo pipefail

TARGET_VERSION="${TARGET_VERSION:-${1:-}}"
export TARGET_VERSION

python3 - <<'PY'
from __future__ import annotations

import json
import os
import re
import sys
import tomllib
from pathlib import Path

root = Path.cwd()
target_version = os.environ.get("TARGET_VERSION", "").strip()

with (root / "pyproject.toml").open("rb") as handle:
    pyproject = tomllib.load(handle)
with (root / "apps/desktop/package.json").open("r", encoding="utf-8") as handle:
    package_json = json.load(handle)
with (root / "apps/desktop/src-tauri/tauri.conf.json").open("r", encoding="utf-8") as handle:
    tauri_conf = json.load(handle)
with (root / "apps/desktop/src-tauri/Cargo.toml").open("rb") as handle:
    cargo_toml = tomllib.load(handle)

versions = {
    "pyproject.toml": pyproject["project"]["version"],
    "apps/desktop/package.json": package_json["version"],
    "apps/desktop/src-tauri/tauri.conf.json": tauri_conf["version"],
    "apps/desktop/src-tauri/Cargo.toml": cargo_toml["package"]["version"],
}

unique_versions = sorted(set(versions.values()))
if len(unique_versions) != 1:
    details = "\n".join(f"- {path}: {version}" for path, version in versions.items())
    raise SystemExit(f"version mismatch across release surfaces:\n{details}")

aligned_version = unique_versions[0]
semver_pattern = re.compile(r"^\d+\.\d+\.\d+$")
if not semver_pattern.match(aligned_version):
    raise SystemExit(f"aligned version is not strict semver: {aligned_version}")

changelog_text = (root / "CHANGELOG.md").read_text(encoding="utf-8")
if "## [Unreleased]" not in changelog_text:
    raise SystemExit("CHANGELOG.md is missing the required '## [Unreleased]' heading")

if target_version:
    if target_version.startswith("v"):
        raise SystemExit("TARGET_VERSION must not include the 'v' prefix")
    if not semver_pattern.match(target_version):
        raise SystemExit(f"TARGET_VERSION is not strict semver: {target_version}")
    if target_version != aligned_version:
        raise SystemExit(
            f"target version {target_version} does not match aligned repo version {aligned_version}"
        )
    release_heading = f"## [{target_version}]"
    if release_heading not in changelog_text:
        raise SystemExit(
            f"CHANGELOG.md is missing the required heading for release version {target_version}"
        )
    print(f"release compliance ok for target version {target_version}")
else:
    print(f"release surface versions aligned at {aligned_version}")
    print("CHANGELOG.md contains the required [Unreleased] heading")
PY
