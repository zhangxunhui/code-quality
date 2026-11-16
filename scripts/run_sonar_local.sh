#!/usr/bin/env bash
# 在本机启动 SonarQube 并执行一次扫描（不依赖 GitHub Actions）。
# 前置：Docker Desktop 已启动；已在 SonarQube 页面生成 token。
# 用法：
#   export SONAR_TOKEN=<你的 token>
#   bash scripts/run_sonar_local.sh
set -euo pipefail

cd "$(git rev-parse --show-toplevel)"

if [ -z "${SONAR_TOKEN:-}" ]; then
  echo "请先导出 token：export SONAR_TOKEN=xxxxxxxx" >&2
  exit 1
fi

host_port="${SONAR_HOST_URL:-http://localhost:9000}"

docker compose -f docker-compose.sonarqube.yml up -d

echo "等待 SonarQube 就绪（首次启动通常需要 1~2 分钟）..."
until curl -sf "${host_port}/api/system/status" | grep -q '"status":"UP"'; do
  sleep 5
done
echo "SonarQube 已就绪：${host_port}"

python -m pytest --cov=pricing --cov-report=xml --cov-report=term-missing

docker run --rm \
  -e SONAR_HOST_URL="http://host.docker.internal:9000" \
  -e SONAR_TOKEN="${SONAR_TOKEN}" \
  -v "$PWD:/usr/src" \
  sonarsource/sonar-scanner-cli

echo "扫描完成：打开 ${host_port} 查看项目质量报告。"
