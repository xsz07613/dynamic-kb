## 2026-10-21
- 将单体 main.py 拆分为 models/database/crawl/scheduler/main，实现工程化分层
- 修复了 scheduler 重复实例化、order_by 失效等Bug
- 引入 set() 实现内存 URL 去重（体会哈希表思想）
- 独立完成 /crawl/batch 批量抓取接口，支持错误跳过和结果汇总
- 踩坑：return 缩进错误导致循环提前中断；变量名覆盖。
- 