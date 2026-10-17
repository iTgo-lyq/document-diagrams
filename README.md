# Document Diagrams

为技术方案、需求说明和项目介绍提供图文表达指导：使用 **diagram-design 的内容建模与图形语义**，搭配 **Bybit svg-diagram 的浅色视觉风格**。

[SKILL.md](SKILL.md) 是唯一使用入口。两个上游以 Git submodule 引用，保持原始文件；本仓库维护职责分工、规则冲突处理和中文图文阅读要求。

## 获取与使用

```bash
git clone --recurse-submodules https://github.com/iTgo-lyq/document-diagrams.git
cd document-diagrams
python3 scripts/check.py
```

已有非递归克隆时：

```bash
git submodule update --init --recursive
```

当前仓库为私有仓库，克隆需要对应 GitHub 权限。GitHub 的源码 ZIP 不包含 submodule 内容；使用递归克隆。

可直接让 Agent 读取本仓库的 `SKILL.md`，或者将整个仓库链接到它的技能目录。以 Codex 和此项目默认路径为例：

```bash
mkdir -p ~/.codex/skills
ln -s ~/workspace/document-diagrams ~/.codex/skills/document-diagrams
```

仅在该目标不存在时创建链接。不要只复制 `SKILL.md`，其相对参考依赖整个目录及已初始化的 submodule。不需要另行安装两个上游 skill。

调用示例：

> 使用 $document-diagrams，依据当前项目实现解释切换身份时如何处理迟到请求。自行选择适合的表达，交付 Markdown 和 SVG；正文说明完整异常语义，图保留关键机制。

默认中文系统字体、静态 SVG、Markdown 相对引用；需要预览时生成自包含 HTML。不固定模型和思考强度，不改变项目文档流程。

## 目录与维护边界

| 路径 | 作用 |
|---|---|
| [SKILL.md](SKILL.md) | 使用入口、内容职责、图文分工和交付检查 |
| [references/visual-style.md](references/visual-style.md) | 默认视觉映射及字号、间距、连线冲突处理 |
| [upstream/diagram-design](upstream/diagram-design) | 内容语义和图形类型参考；skill 位于 `skills/diagram-design/` |
| [upstream/svg-diagram](upstream/svg-diagram) | Bybit 样式、示例与可选诊断工具 |
| [evals/cases.md](evals/cases.md) | 初始四题回归材料和评审关注点 |
| [scripts/check.py](scripts/check.py) | submodule 固定版本、完整性和本地文档链接检查 |

初始上游版本与组合实验的 skill 文件一致：

| 上游 | 初始固定提交 |
|---|---|
| [cathrynlavery/diagram-design](https://github.com/cathrynlavery/diagram-design) | [`15d44aed098512a9345ebae636409846e2641496`](https://github.com/cathrynlavery/diagram-design/commit/15d44aed098512a9345ebae636409846e2641496) |
| [bybit-exchange/svg-diagram](https://github.com/bybit-exchange/svg-diagram) | [`c30c9e3bc9a70f2b77b60c7ea27157de3a88d81a`](https://github.com/bybit-exchange/svg-diagram/commit/c30c9e3bc9a70f2b77b60c7ea27157de3a88d81a) |

当前有效版本以 Git 中的 submodule 指针为准。更新时先审阅上游变化，选定提交，将 submodule 指针加入暂存区，运行 `python3 scripts/check.py`，再按四题回归检查表达和风格。通过后提交指针与必要的组合规则调整。日常绘图不自动拉取上游最新版本，不直接修改上游文件。

`check.py` 验证安装和引用完整性，不会生成图，也不能证明内容正确或视觉质量。本次整合沿用已验证的组合规则；打包后的完整绘图回归需独立运行并记录模型、强度和源码版本。

## 许可与来源

本仓库的组合指导与脚本采用 [MIT License](LICENSE)。上游保留各自的 [diagram-design 许可证](upstream/diagram-design/LICENSE) 和 [Bybit 许可证](upstream/svg-diagram/LICENSE)。本项目是独立组合，不代表上游官方发布。
