---
name: deliver
description: 规划、实现、验证并独立审查项目任务
---
# /shiploom:deliver

首次在项目使用时，如 `harness/verify.py` 不存在，运行 `"${CLAUDE_PLUGIN_ROOT}/init.sh" .`，然后根据项目配置 `harness/verify.json`，然后停止并提示用户检查、配置并提交脚手架；不要继续创建 worktree。文件冲突时停止并报告，不能覆盖。
1. 分析类任务只调用 planner；开发任务调用 planner，确定根因、验收、风险和验证计划。
2. 使用 `python3 harness/worktree.py start <task-id>` 创建独立 worktree，在该目录启动 Builder；创建前确保当前仓库已有提交。避免多任务改同一文件。
3. 在 worktree 用 `python3 harness/flow.py init <task-id>` 建立状态。Builder 实现并执行 `python3 harness/verify.py fast|feature|full`；配置缺失或失败不得声称通过。Bug 每次失败执行 `flow.py bug-fail <id>`；第二次后收集脱敏真实日志、输入输出、环境及复现证据，使用 `bug-evidence` 记录文件路径后才能第三次尝试。第三次失败停止，Planner 重写问题、事实和验收，新方案保存后用 `replan` 解锁。不得假装失败已解决。
4. 用独立 reviewer 审查，每轮先调用 `flow.py review-start <id>`；每轮修复后重新验证。最多三轮，仍有阻塞项则停止并报告未通过。`flow.py review-result <id> pass|fail` 记录结果。
5. 完成前运行 full，准备 PR 模板与提交摘要（变更、验证、回滚）。报告失败、未覆盖风险、证据和 worktree 位置。提交、合并、发布、删除必须由人明确确认并亲自执行；停止等待，不执行。

轮次脚本是工作流约定，不能阻止绕开脚本的代理；隔离和远端保护见 README。
