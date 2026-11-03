# Document Diagrams

为技术方案、需求说明和项目介绍制作 SVG 图表。覆盖 45 种图形，直接交付可独立使用的静态 `.svg` 文件。

可安装的 skill 位于 [skills/document-diagrams](skills/document-diagrams/SKILL.md)。只支持从本仓库 `main` 分支的该目录安装，使用时不依赖本仓库的其他目录。

## 安装

在 Codex 中可以提出：

> 使用 $skill-installer，从 iTgo-lyq/document-diagrams 的 main 分支安装 skills/document-diagrams。

安装完整的 `skills/document-diagrams/` 目录，不要只安装 `SKILL.md`。本 README、维护工具和参考源码不属于安装内容，也不需要初始化 submodule。

更新时仍从 `main` 同步该源码目录，并比对已安装副本中的本地修改。以 Git 提交追踪 skill 的修订；推送 `main` 后，后续源码安装即可获取新内容，已安装的副本不会自动同步。

调用示例：

> 使用 $document-diagrams，依据当前项目实现，为“切换身份时如何处理迟到请求”制作一张中文 SVG 图。自行选择适合的表达，保留关键机制与必要条件。

依据项目材料直接绘制静态 SVG，使用中文系统字体和浅色图形。不生成 HTML 页面、PNG 或动画播放器。不固定模型和思考强度。

结构检查脚本使用 Python 3.10+ 标准库。字体使用系统内置的中文字体回退，不下载网络字体。最终 SVG 仍需在渲染器中检查文字、对比度和实际布局。

## 源码与安装目录

```text
skills/document-diagrams/    可直接安装的完整 skill
  SKILL.md                  使用入口
  agents/openai.yaml        展示信息与默认提示词
  references/               45 种图形详规、语义、布局和视觉规范
  scripts/                  独立使用的 SVG 与结构检查工具
  assets/template.svg       浅色 SVG 模板
  LICENSE                   版权声明与许可原文
upstream/                   维护者参考的固定版本源码
scripts/                    安装目录检查、源码检查和整理工具
tests/                      源码安装隔离、引用边界和运行回归
evals/                      图文行为回归材料
```

安装边界是 `skills/document-diagrams/`。其中的入口、参考文件和元信息直接描述本 skill 的行为，不包含外部 skill 的原始入口、仓库副本、依赖加载说明或规则覆盖关系。来源与维护说明只放在本仓库 README；安装目录仅保留必要的版权声明和许可原文。

## 检查

```bash
python3 scripts/check.py
python3 -m unittest discover -s tests -v
```

检查已安装副本时，向 `scripts/check.py` 的 `--skill-dir` 参数传入实际安装目录。

这些检查不依赖 Git 元数据，验证入口、安装边界和本地引用。它们不能证明图文事实正确或视觉质量；行为回归仍需按 [evals/cases.md](evals/cases.md) 执行并记录结果。

## 来源与维护

内容建模和图形语义参考 [diagram-design](https://github.com/cathrynlavery/diagram-design)，浅色视觉规范参考 [Bybit svg-diagram](https://github.com/bybit-exchange/svg-diagram)。安装目录不携带这两个项目的源码仓库或原始 skill 入口，也不需要另行安装它们。

| 参考项目 | 参考提交 |
|---|---|
| cathrynlavery/diagram-design | `15d44aed098512a9345ebae636409846e2641496` |
| bybit-exchange/svg-diagram | `c30c9e3bc9a70f2b77b60c7ea27157de3a88d81a` |

内容边界是保留 diagram-design 的非样式指导，用 svg-diagram 的视觉样式替换其样式：

| 内容 | 处理方式 |
|---|---|
| 选图路由、45 种类型详规、9 个语义模式 | 保留细则、参数、条件和边界，按需加载 |
| 类型布局、连线语义、复杂度、可访问性 | 保留图形语义；技术图的内容数量与深度作为布局参考，以目标阅读尺寸的可读性决定分区与拆图，不为凑数省略关键组件和关系 |
| SVG 与结构验证 | 使用独立脚本检查文件、语义和几何结构 |
| HTML 页面、PNG 导出、动画控制器、单独的元数据导出 | 不在 SVG 制作范围内；直接编写 SVG，结构追踪信息保留在 SVG 属性中 |
| diagram-design 配色、字体、暗色、纸纹、海报卡片及品牌配置 | 移除；不带首次样式确认、profile、手绘和终端主题 |
| svg-diagram 视觉样式 | 取白底、五组浅色语义配色及关系箭头用色、中文系统字体、16/12/10px 基础字号、细描边、圆角及缺口箭头 |
| svg-diagram 选图、执行流程、输出位置和通用布线政策 | 不引入；图形结构和语义仍由 diagram-design 的规则决定 |

类型示例使用统一视觉角色；配色、字体和 marker 的参数与箭头端点保持一致。结构验证脚本随 skill 安装，文字换行使用原生 SVG `text/tspan`。README 与来源说明位于仓库，版权和许可原文位于 skill 的 LICENSE。

语义配色按角色重复使用：输入蓝、处理橙、数据绿、分析紫、警告粉。焦点通过轮廓、字重或图形规定的标记突出，数量独立计算。热力图使用单色深浅标尺，蜂群图使用统一非焦点填充，瀑布图用填充／空心区分增减，哑铃图用空心／实心区分端点。验证器按 `data-focal="true"` 识别焦点，Polar 使用 `data-polar-focal`。

图标输入标识用通用图形或带名称的节点表达。尺寸公式表达结构关系，文字和徽标按实际字体测量，数量图形的坐标和面积与数值对应。

本 skill 与上述参考材料均采用 MIT 许可。相关版权声明与许可原文保留在 skill 目录的 [LICENSE](skills/document-diagrams/LICENSE) 中，不作为 Agent 的使用指导。

`upstream/` 中的两个 Git submodule 仅供维护者比较和审阅，保留原始文件。维护时按需初始化并检查：

```bash
git submodule update --init --recursive
python3 scripts/check.py --source
```

固定提交以 Git 中的 submodule 指针为准。`scripts/assemble.py` 按固定来源整理 SVG 制作指导；`scripts/semantic_colors.py` 定义语义用色与焦点识别；`scripts/complexity.py` 定义技术图密度指导与架构校验规则。这些工具不随 skill 安装。安装目录中的视觉规范、SVG 模板、`check_svg.py`、展示元信息和许可独立维护，其余内容由整理脚本更新。

更新参考版本时先审阅差异，修订整理规则并运行 `python3 scripts/assemble.py`，更新本 README 中的参考版本，再运行完整性检查与图文行为回归。上游指针有意更新后，先暂存该指针再执行 `--source` 检查。普通安装和使用不执行整理脚本，也不需要初始化 submodule。

本仓库自己的指导和脚本采用 [MIT License](LICENSE)。本项目为独立整理，不代表参考项目的官方发布。
