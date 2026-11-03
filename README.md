# Shiploom：使用手册

这是面向 Claude Code 的本地插件包，提供 `/shiploom:deliver`、Planner / Builder / Reviewer、操作提醒 Hook，以及可安装到项目中的验证和工作流脚本。需要 Claude Code、Python 3.9+、Git 和 Bash。

## 1. 安装插件

解压后，在终端进入 `shiploom` 目录，执行：

```bash
claude plugin marketplace add .
claude plugin install shiploom@shiploom-local
```

默认安装到当前用户的 Claude Code 配置。保留解压目录，本地 marketplace 使用其中的文件。安装后重启 Claude Code，或在会话里使用 `/reload-plugins`。可用 `claude plugin list` 查看是否启用。

只想临时试用，可在项目目录执行：

```bash
claude --plugin-dir /解压路径/shiploom/plugins/shiploom
```

这种方式仅对当前会话生效；路径含空格时请加引号。插件启用后，Hook 在使用该插件的 Claude Code 会话中生效，包括未初始化的项目；它会拦截部分提交、合并、删除和发布命令。禁用或卸载插件后不再运行。项目原有同类 Hook 可能同时运行。

## 2. 初始化项目

进入项目，打开 Claude Code，输入：

```text
/shiploom:deliver 初始化这个项目的交付流程。
```

插件会使用自身的 `init.sh` 安装项目文件。也可自行执行（把路径换成实际解压路径）：

```bash
/解压路径/shiploom/plugins/shiploom/init.sh /项目路径
```

初始化不覆盖同名文件；如有冲突，先安装到空目录，再手动合并。审查 `harness/verify.json`、CI、`AGENTS.md` 等生成文件，并填写项目的检查命令。三个等级各自独立，Full 不自动包含 Fast 或 Feature。

```json
{
  "fast": [["python3", "-m", "unittest", "tests.test_fast"]],
  "feature": [["python3", "-m", "unittest", "discover"]],
  "full": [["python3", "-m", "unittest", "discover"]]
}
```

这是示例，请换成真实命令。默认空配置会使验证和 CI 失败。每个命令是参数数组，直接运行，不经过 shell；配置中的代码会被执行，请先审核。确认后**由你提交**项目文件：worktree 从 Git 的当前提交创建，不会带入未提交文件。项目需要至少一次提交。

## 3. 日常使用

在项目中输入：

```text
/shiploom:deliver 增加账号切换功能；先分析，再实现、验证和独立审查。
```

Planner 负责计划，Builder 在独立 worktree 开发，Reviewer 负责独立审查；最终由你确认并亲自提交、合并、发布和删除。插件名是命名空间，命令是 `/shiploom:deliver`，不是原脚手架的 `/deliver`。

自己运行验证：

```bash
python3 harness/verify.py fast
python3 harness/verify.py feature
python3 harness/verify.py full
```

报告保存在 `.harness/`；分享前检查和脱敏。CI 会运行 Full；需要自己在 Git 平台开启分支保护并将其设为必需检查。

## 4. 遇到问题

- Bug 连续两次失败：补充脱敏日志、输入输出和复现数据；第三次失败后停止并重新规划。
- 独立审查最多三轮；仍有阻塞问题就停止，不能声称通过。
- `harness/flow.py` 记录状态，`harness/worktree.py` 创建独立工作目录。脚本需要工作流主动调用；不保证模型遵循流程，也不验证证据质量。状态可被改动或绕过，不支持同任务并发写入。
- Beta 示例 `examples/beta_flag.py` 默认关闭。上线先内部测试，再小范围开放；关闭开关不能撤销数据迁移，必须单独准备恢复方案。
- Codex 不加载此 Claude Code 插件或 Hook。初始化后，可要求 Codex 参考 `AGENTS.md`、`harness/DELIVER.md` 和 `harness/roles/`，并手动使用相同脚本。

## 5. 安全边界

Hook 只做启发式拦截，无法可靠识别间接命令、其他工具、网络 API 或被修改的配置；它不是沙箱，也不是强制审批。Git worktree 共享仓库元数据。要实现硬边界，应另行配置独立系统账号或容器、只读挂载、最小权限、凭据与网络隔离、远端分支保护及受控部署系统。CI 使用只读权限；不可信 PR 会执行验证代码，需隔离运行环境，不给它生产密钥。报告和 CI 工件可能包含敏感信息，上传前须脱敏。

参考：[Claude Code 插件](https://code.claude.com/docs/en/plugins) · [插件市场](https://code.claude.com/docs/en/plugin-marketplaces) · [插件参考](https://code.claude.com/docs/en/plugins-reference)
