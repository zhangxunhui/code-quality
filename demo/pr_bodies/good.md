## 变更说明

- 删除重复实现，改为复用统一的 `pricing` 模块（金额统一使用 `Decimal`）。
- 优惠券折扣率集中到 `COUPON_RATES`，新增券种只改一处。
- 新增 `tests/test_legacy_discount.py`，覆盖正常路径与异常路径。

## 自检

- [x] 本地 `pytest` 全部通过
- [x] 已补充单元测试
- [x] SonarQube Quality Gate 为 PASSED

## 审查关注点

- 金额是否全部使用 `Decimal`，是否统一四舍五入到分。
- 新旧接口行为是否一致：满 10 / 50 / 100 件的批量折扣。
- 优惠券为空或未知时是否安全降级。
