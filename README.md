# code-quality

一个可直接推到 GitHub 的完整示例，用来验证这条链路：

> 代码入库 → PR 触发 GitHub Actions → 跑单元测试 → SonarQube 分析 → 质量门禁回传 PR → 人工审查 → 合并 / 拒绝

## 1. 这个仓库包含什么

| 场景环节 | 对应文件 |
| --- | --- |
| 真实业务代码（订单价格计算） | `src/pricing/` |
| 单元测试（57 个用例） | `tests/` |
| CI：测试 + 覆盖率 + JUnit 报告回传 | `.github/workflows/ci.yml` |
| SonarQube 扫描与质量门禁 | `.github/workflows/ci.yml` 的 `sonarqube` job |
| Sonar 项目配置 | `sonar-project.properties` |
| 故意写坏的 PR（用于演示拒绝） | `demo/bad/legacy_discount.py` |
| 修复后的 PR（用于演示合并） | `demo/good/` |
| 一键开 PR 的脚本 | `demo/open_bad_pr.sh`、`demo/open_good_pr.sh` |
| 本地自建 SonarQube | `docker-compose.sonarqube.yml`、`scripts/run_sonar_local.sh` |
| 课堂演示时间线 | `docs/demo-script.md` |

业务代码本身是干净的：没有已知代码坏味道，行覆盖率约 98%，可以直接作为“基线”。

## 2. 目录结构

```text
sonar-ci-demo/
├── .github/
│   ├── workflows/ci.yml
│   └── pull_request_template.md
├── demo/
│   ├── bad/legacy_discount.py          # 有问题的实现
│   ├── good/                           # 修复后的实现 + 测试
│   ├── pr_bodies/                      # PR 描述模板
│   ├── open_bad_pr.sh
│   └── open_good_pr.sh
├── docs/demo-script.md
├── scripts/run_sonar_local.sh
├── src/pricing/
│   ├── __init__.py
│   ├── errors.py
│   ├── models.py
│   ├── parsing.py
│   └── pricing.py
├── tests/
│   ├── test_integration.py
│   ├── test_models.py
│   ├── test_parsing.py
│   └── test_pricing.py
├── docker-compose.sonarqube.yml
├── pyproject.toml
├── requirements-dev.txt
├── requirements.txt
└── sonar-project.properties
```

## 3. 本地先跑通（不依赖 GitHub）

需要 Python 3.11+。

```bash
cd sonar-ci-demo
python -m venv .venv

# Windows (Git Bash)
source .venv/Scripts/activate
# macOS / Linux
# source .venv/bin/activate

pip install -r requirements-dev.txt
pytest --cov=pricing --cov-report=term-missing
```

预期输出：`57 passed`，覆盖率约 98%。

这一步的意义：先证明“代码 + 测试”本身没问题，后面 CI 红了才能确定是流水线或代码质量问题，而不是环境问题。

## 4. 推到 GitHub

```bash
git init
git add .
git commit -m "chore: initial commit"
git branch -M main
git remote add origin https://github.com/<你的用户名>/code-quality.git
git push -u origin main
```

仓库建好后，确认 **Actions 已启用**：`Settings → Actions → General → Allow all actions and reusable workflows`。

## 5. 接入 SonarQube

有两条路。**课堂演示优先选 A（SonarCloud）**，因为免费、开箱即用、PR 装饰完整。

### 方案 A：SonarCloud（推荐，公开仓库免费）

1. 打开 <https://sonarcloud.io>，用 GitHub 账号登录。
2. 点右上角 `+` → `Analyze new project`，选择刚推送的仓库。
3. 按提示安装 **SonarCloud GitHub App**（这是 PR 评论和检查状态能回传的前提）。
4. 创建组织（organization）后，SonarCloud 会给出一段 GitHub Actions 配置，记下两个值：
   - `projectKey`，默认形如 `<org>_code-quality`
   - `organization`，就是你的组织 key
5. 修改 `sonar-project.properties`：

   ```properties
   sonar.projectKey=<org>_code-quality
   sonar.organization=<org>
   ```

6. 生成 token：`My Account → Security → Generate Tokens`，类型选 `Project analysis token`。
7. 到 GitHub 仓库配置：
   - `Settings → Secrets and variables → Actions → Secrets` → 新建 `SONAR_TOKEN`
   - 同一页切到 `Variables` → 新建 `SONAR_HOST_URL`，值为 `https://sonarcloud.io`

> 注意：`SONAR_TOKEN` 放 Secrets，`SONAR_HOST_URL` 放 Variables。两者不要混。

### 方案 B：自建 SonarQube Server

```bash
docker compose -f docker-compose.sonarqube.yml up -d
# 浏览器打开 http://localhost:9000，首次登录 admin / admin
```

然后：

1. `My Account → Security → Generate Tokens` 生成 token。
2. 在 SonarQube 里手动创建项目，project key 与 `sonar-project.properties` 保持一致。
3. **注释掉** `sonar.organization`（这一项只属于 SonarCloud）。
4. GitHub 仓库 Secrets 增加 `SONAR_TOKEN`，Variables 增加 `SONAR_HOST_URL=http://<可被 runner 访问的地址>:9000`。

两个关键限制：

- **GitHub 托管 runner 访问不到你本机的 `localhost:9000`。** 想在 PR 里跑，需要公网服务器、内网穿透，或自建 self-hosted runner。只在本机看报告，用 `scripts/run_sonar_local.sh`。
- **社区版（Community Build）不做 PR 级分析 / PR 装饰。** 免费版只分析主分支；PR 上的“红/绿”来自工作流里的 quality gate 步骤。需要 PR 评论装饰要用 Developer Edition 及以上，或直接用 SonarCloud。

## 6. CI 流水线做了什么

`.github/workflows/ci.yml` 有两个 job：

```text
tests                           sonarqube
  ├─ checkout                     ├─ checkout（fetch-depth: 0）
  ├─ setup-python 3.12            ├─ 下载覆盖率报告
  ├─ pip install -r ...           ├─ sonarqube-scan-action
  ├─ pytest --junitxml ...        ├─ quality-gate-action 轮询门禁结果
  │    --cov-report=xml/json      ├─ 结果写入 Job Summary
  ├─ 回传测试结果到 PR            └─ 门禁非 PASSED 则强制失败
  ├─ 覆盖率写入 Job Summary
  └─ 上传 test-results / coverage
```

几个设计点，讲课时可以展开：

- **`fetch-depth: 0`**：Sonar 需要完整提交历史才能准确判断“新增代码”。浅克隆会让增量分析失真。
- **`needs: tests`**：测试不过就不浪费额度做扫描；测试通过但门禁失败时，PR 仍然是红的。
- **测试结果回传**：`--junitxml` 生成 JUnit 报告，`EnricoMi/publish-unit-test-result-action` 把它变成 PR 上的 Check Run 和评论。失败用例会精确到“哪个测试、哪一行”。
- **覆盖率回传**：既写进 Actions 的 Job Summary，也通过 `coverage.xml` 交给 Sonar 计算“新增代码覆盖率”。
- **门禁双保险**：`quality-gate-action` 本身会因门禁失败而报错；后面再加一个 `Enforce quality gate` 步骤，避免 action 版本行为差异导致“门禁失败但流水线绿了”。
- **`concurrency`**：同一个 PR 连续 push 时自动取消旧任务，课堂演示时不会被排队拖慢。

## 7. 演示：坏 PR 被拒绝，好 PR 被合并

前置：本地装好 `gh` 并执行过 `gh auth login`，且当前在仓库目录。

### 7.1 制造一个有问题的 PR

```bash
bash demo/open_bad_pr.sh
```

脚本会：

1. 从 `main` 拉出 `demo/bad-discount`
2. 把 `demo/bad/legacy_discount.py` 复制成 `src/pricing/legacy_discount.py`
3. 提交、推送、用 `gh` 创建 PR

预期结果：

| 检查项 | 结果 | 原因 |
| --- | --- | --- |
| `tests` | ✅ 通过 | 新文件没有被测试引用，旧测试仍然全绿 |
| `sonarqube` | ❌ 失败 | 新增代码覆盖率 0%；重复代码、未使用变量、`eval` 安全问题 |

PR 页面上应该能看到：

- `Unit test results` 检查：57 个用例全部通过（新文件没有被任何测试引用）
- `sonarqube` 检查：红色，展开日志能看到 `Quality Gate 未通过`
- SonarCloud 的 PR 评论：逐条列出新增问题
- 人工审查：即使门禁没拦住，也能看出金额用了 `float`（`price = float(item["price"])`），存在精度隐患

这就是“自动化门禁 + 人工审查”各司其职的演示点。

### 7.2 拒绝这个 PR

在 PR 页面：

- `Files changed` 里留一条 review comment，例如“金额不能用 float，且新增代码没有测试”
- 点 `Review changes` → `Request changes`
- 或者直接 `Close pull request`，演示“拒绝合并”

### 7.3 提交修复后的 PR

```bash
bash demo/open_good_pr.sh
```

新 PR 会复用统一的 `pricing` 模块，并附带 `tests/test_legacy_discount.py`。

预期：`tests` 与 `sonarqube` 全绿，Quality Gate 为 `PASSED`。

### 7.4 人工审查后合并

- 在 PR 里确认 SonarCloud 没有新增问题、覆盖率达标
- `Approve` → `Squash and merge`
- 合并后 `main` 会再跑一次 CI，确认主干依然绿色

## 8. 强制“检查不过不能合并”

只让 PR 变红还不够，要让它**点不动合并按钮**：

`Settings → Rules → Rulesets → New branch ruleset`

- **Target branches**：`main`
- **Require a pull request before merging**：开启，Required approvals 设为 1
- **Require status checks to pass**：勾选
  - `tests`
  - `sonarqube`
  - `Unit test results`（测试明细检查）
  - `SonarCloud Code Analysis`（仅方案 A；第一次扫描后才会出现在列表里）
- **Block force pushes**：开启

保存后，坏 PR 的合并按钮会变灰，提示 “Required statuses must pass”。

> 注意：必需检查必须至少成功运行过一次，才能在搜索框里被选中。所以先推一次 `main`，再配规则。

## 9. 常见问题

| 现象 | 原因 | 处理 |
| --- | --- | --- |
| `sonarqube` 报 `Not authorized` | token 无效 / 项目 key 或组织不匹配 | 重新生成 token；核对 `sonar.projectKey`、`sonar.organization` |
| `Could not find a default branch` | 浅克隆 | 确认 `fetch-depth: 0` |
| 覆盖率显示 0% | `coverage.xml` 没生成或路径不对 | 确认 `pytest-cov` 已安装、`--cov-report=xml` 生效、`sonar.python.coverage.reportPaths=coverage.xml` |
| 本地 SonarQube 在 Actions 里连不上 | runner 访问不到 `localhost` | 用 SonarCloud，或公网部署 / self-hosted runner |
| 自建服务器报 `sonar.organization` 未知属性 | 该项只用于 SonarCloud | 注释掉这一行 |
| fork 来的 PR 没有 Sonar 结果 | fork PR 拿不到 Secrets | 课堂演示用同仓库分支；fork 场景需 `pull_request_target` 或 self-hosted runner |
| `Unit test results` 检查没有评论 | `permissions` 不足 | 确认 `checks: write`、`pull-requests: write` |
| 门禁 PASSED 但 PR 仍然红 | 还有别的检查失败 | 看 PR 底部 Checks 列表，逐个展开 |

## 10. 可以用来的课堂讨论

1. **为什么覆盖率只统计“新增代码”？** 老项目整体覆盖率可能很低，如果按全量卡门禁，团队永远合不了 PR。
2. **SonarQube 能替代人工审查吗？** 不能。示例里的 `float` 精度问题不一定会被规则命中，但会造成真实的金额误差。
3. **门禁失败时应该改代码还是改规则？** 讨论“误报处理”“技术债豁免”“新增问题零容忍”的边界。
4. **为什么测试和扫描要拆成两个 job？** 失败定位更清晰，也能避免测试挂了还消耗扫描额度。
5. **PR 装饰的价值是什么？** 把问题定位到 diff 的具体行，reviewer 不需要在 Sonar 页面和 PR 之间来回切换。
