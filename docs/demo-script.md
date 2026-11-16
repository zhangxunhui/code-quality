# 课堂演示脚本（约 20 分钟）

## 0. 演示前检查（课前 10 分钟）

```bash
git switch main && git pull
gh auth status
```

确认三件事：

- [ ] GitHub 仓库首页的 Actions 里，最近一次 `main` 的运行是绿色
- [ ] SonarCloud 项目页能看到上一次分析结果
- [ ] 分支保护规则已生效：`main` 不能直接 push，必须走 PR

如果 `main` 最近没有跑过，先随便改一行文档提交，等 CI 绿了再开始。

---

## 1. 讲清“三道闸门”（2 分钟）

在黑板 / 幻灯片上画：

```text
开发者 push
   │
   ▼
PR  ──►  ① 单元测试（tests）
   │     ② SonarQube 质量门禁（sonarqube）
   │     ③ 人工 Code Review
   ▼
合并到 main
```

强调：**前两道是自动化的，第三道是人。三者都过，才能合并。**

---

## 2. 展示基线：绿色 PR（3 分钟）

先展示一个正常 PR 长什么样，让学生有对照。

```bash
# 新建一个只改文档的分支，演示完整流程
git switch -c docs/add-note main
# 随便加一行说明后提交
git add .
git commit -m "docs: add note"
git push -u origin docs/add-note
gh pr create --base main --fill
```

打开 PR 页面，依次指出：

1. 底部 Checks 区域：`tests` ✅、`sonarqube` ✅、`Unit test results` ✅
2. `Unit test results` 点进去：57 个用例，耗时、通过率
3. SonarCloud 评论：`Quality Gate passed`，0 new issues
4. 合并按钮是可点的

---

## 3. 制造坏 PR（5 分钟）

```bash
bash demo/open_bad_pr.sh
```

打开新 PR，按下面的顺序讲：

### 3.1 单元测试仍然通过

`tests` 是绿的。为什么？因为坏代码是**新增文件**，旧测试没有覆盖它，所以不会失败。

**讨论点**：测试通过 ≠ 代码没问题。覆盖率看的是“新增代码有没有被测到”。

### 3.2 SonarQube 门禁失败

点开 `sonarqube` job 的日志，找到：

```text
Quality Gate 未通过（FAILED）
```

再到 SonarCloud 的 PR 评论里逐条看问题：

| 问题 | 规则 | 说明 |
| --- | --- | --- |
| 新增代码覆盖率 0% | Coverage on New Code < 80% | 没有任何测试触达新文件 |
| 重复代码 | Duplicated Lines on New Code > 3% | `apply_coupon` 与 `apply_coupon_v2` 完全重复 |
| 未使用变量 | `unused_debug_flag` | 调试残留 |
| 动态执行代码 | `eval(data)` | 安全问题，用户输入可执行任意代码 |

### 3.3 人工审查还能发现什么

打开 `Files changed`，指出：

```python
price = float(item["price"])
```

金额用 `float` 会引入二进制浮点误差（例如 `0.1 + 0.2 != 0.3`）。这条不一定会被 Sonar 规则命中，但它是真实缺陷。

**这就是“SonarQube 不能替代人工审查”的最好例子。**

### 3.4 拒绝 PR

- 留一条 review comment
- `Review changes → Request changes`
- 或者直接 `Close pull request`

指出合并按钮此时是灰的，提示 `Required statuses must pass`。

---

## 4. 提交修复版（5 分钟）

```bash
bash demo/open_good_pr.sh
```

打开新 PR，对照 `Files changed` 讲三点：

1. **复用统一模块**：不再自己算折扣，调用 `pricing.order_total`
2. **消除重复**：`COUPON_RATES` 字典替代三个 `if`
3. **补齐测试**：`tests/test_legacy_discount.py` 覆盖正常路径和异常路径

看 Checks：

- `tests` ✅
- `sonarqube` ✅，Quality Gate `PASSED`
- 覆盖率保持在高位

让一位学生上来点 `Approve`，然后 `Squash and merge`。

合并后回到 Actions，展示 `main` 分支的 CI 也是绿的。

---

## 5. 收尾讨论（3 分钟）

1. 如果团队刚引入 SonarQube，历史代码有几千个问题，应该怎么设置门禁？
   - 参考方向：只卡“新增代码”，历史问题进技术债清单，逐步清理。
2. 如果 SonarQube 报了一个你认为的误报，怎么办？
   - 参考方向：先确认是否真误报；确认为误报后用 `// NOSONAR` 或界面标记，并写清原因；不要全局关规则。
3. 为什么要求“新增代码覆盖率 ≥ 80%”，而不是“全仓库 ≥ 80%”？
4. 如果 CI 挂了，但本地是好的，排查顺序是什么？
   - Python 版本 → 依赖版本 → 环境变量 / Secrets → 路径大小写 → 缓存

---

## 6. 失败预案

| 情况 | 处理 |
| --- | --- |
| SonarCloud 额度用完 / 网络不可用 | 切到本地 `scripts/run_sonar_local.sh`，只演示扫描和报告，PR 环节用截图 |
| `gh` 未登录 | 提前在浏览器里手动开 PR，脚本跳过 |
| 分支保护导致脚本 push 失败 | 规则只应作用于 `main`，检查 `demo/*` 是否被误加进 ruleset |
| 第一次扫描很慢 | 提前跑一次预热，演示时直接用已有结果 |
| 学生问“为什么 PR 上没看到 Sonar 评论” | 检查 SonarCloud GitHub App 是否安装到了该仓库 |
