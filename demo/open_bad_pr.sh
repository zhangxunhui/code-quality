#!/usr/bin/env bash
# 演示用：创建一个“有质量问题”的 PR，预期被 CI / Quality Gate 拦下。
# 用法（在仓库任意位置）：bash demo/open_bad_pr.sh
set -euo pipefail

cd "$(git rev-parse --show-toplevel)"

branch="demo/bad-discount"

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

cp demo/bad/legacy_discount.py src/pricing/legacy_discount.py
git add src/pricing/legacy_discount.py
git commit -m "feat(pricing): 接入历史遗留折扣计算"

git push -u origin "$branch" --force

if gh pr view "$branch" >/dev/null 2>&1; then
  echo "PR 已存在：$(gh pr view "$branch" --json url --jq .url)"
else
  gh pr create \
    --base main \
    --head "$branch" \
    --title "feat(pricing): 接入历史遗留折扣计算" \
    --body-file demo/pr_bodies/bad.md
fi
