#!/usr/bin/env bash
# 演示用：创建一个“已修复”的 PR，预期通过全部检查并可合并。
# 用法（在仓库任意位置）：bash demo/open_good_pr.sh
set -euo pipefail

cd "$(git rev-parse --show-toplevel)"

branch="demo/good-discount"

if ! gh auth status >/dev/null 2>&1; then
  echo "请先执行 gh auth login" >&2
  exit 1
fi

git switch main
git pull --ff-only

if git show-ref --verify --quiet "refs/heads/$branch"; then
  git switch "$branch"
  git reset --hard main
else
  git switch -c "$branch" main
fi

cp demo/good/legacy_discount.py src/pricing/legacy_discount.py
cp demo/good/test_legacy_discount.py tests/test_legacy_discount.py
git add src/pricing/legacy_discount.py tests/test_legacy_discount.py
git commit -m "refactor(pricing): 复用统一价格模块并补齐单元测试"

git push -u origin "$branch" --force

if gh pr view "$branch" >/dev/null 2>&1; then
  echo "PR 已存在：$(gh pr view "$branch" --json url --jq .url)"
else
  gh pr create \
    --base main \
    --head "$branch" \
    --title "refactor(pricing): 复用统一价格模块并补齐单元测试" \
    --body-file demo/pr_bodies/good.md
fi
