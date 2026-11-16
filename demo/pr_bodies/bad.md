## 变更说明

- 新增 `src/pricing/legacy_discount.py`，从旧系统直接搬运折扣计算逻辑。
- 暂时没有为新文件补充单元测试。

## 自检

- [x] 本地可以运行
- [ ] 已补充单元测试
- [ ] SonarQube Quality Gate 为 PASSED

> 演示预期：`tests` 通过，但 `sonarqube` 失败（新增代码覆盖率为 0%，且存在新增问题），PR 不允许合并。
