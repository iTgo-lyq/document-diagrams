# Document Diagrams

为技术方案、需求说明和项目介绍制作 SVG 图表。覆盖 45 种图形，直接交付可独立使用的静态 `.svg` 文件。

可安装的 skill 位于 [skills/document-diagrams](skills/document-diagrams/SKILL.md)。该目录包含独立的使用指导和参考文件，可单独复制、下载或打包，使用时不依赖本仓库的其他目录。

## 安装

在 Codex 中可以提出：

> 使用 $skill-installer，从 iTgo-lyq/document-diagrams 安装 skills/document-diagrams。

也可以从 [Releases](https://github.com/iTgo-lyq/document-diagrams/releases/latest) 下载 `document-diagrams.zip`，解压后将其中的 `document-diagrams/` 放入个人技能目录。发布包不包含本 README、维护工具或参考源码。

也可以克隆后手动复制到个人技能目录。以下示例使用 Codex 的 `~/.agents/skills`；目标已存在时先决定如何更新，不直接覆盖已有修改。

```bash
git clone https://github.com/iTgo-lyq/document-diagrams.git
cd document-diagrams
python3 scripts/check.py
mkdir -p ~/.agents/skills
cp -R skills/document-diagrams ~/.agents/skills/document-diagrams
```

普通克隆和 GitHub 源码 ZIP 都包含完整的可安装目录，不需要递归克隆。不要只复制 `SKILL.md`。

本地开发也可把 `skills/document-diagrams` 链接到技能目录。若以前链接的是仓库根目录，需要将该链接更新到新的 skill 目录。

调用示例：

> 使用 $document-diagrams，依据当前项目实现，为“切换身份时如何处理迟到请求”制作一张中文 SVG 图。自行选择适合的表达，保留关键机制与必要条件。

使用中文系统字体、浅色图形和静态展示，支持从 draw.io、Mermaid、Excalidraw 提取内容并重绘为 SVG。不生成 HTML 页面、PNG 或动画播放器。不固定模型和思考强度。

解析和结构检查脚本使用 Python 3.10+ 标准库。字体使用系统内置的中文字体回退，不下载网络字体。最终 SVG 仍需在渲染器中检查文字、对比度和实际布局。

## 源码与发布目录

```text
skills/document-diagrams/    可直接安装的完整 skill
  SKILL.md                  使用入口
  agents/openai.yaml        展示信息与默认提示词
  references/               45 种图形详规、语义、布局、导入和视觉规范
  scripts/                  独立使用的解析、SVG 与结构检查工具
  assets/template.svg       浅色 SVG 模板
  LICENSE                   版权声明与许可原文
upstream/                   维护者参考的固定版本源码
scripts/                    安装包检查、源码检查和打包工具
tests/                      安装隔离、引用边界和打包回归
evals/                      图文行为回归材料
```

安装与发布的边界是 `skills/document-diagrams/`。其中的入口、参考文件和元信息直接描述本 skill 的行为，不包含外部 skill 的原始入口、仓库副本、依赖加载说明或规则覆盖关系。来源与维护说明只放在本仓库 README，不随 skill 发布；安装目录仅保留必要的版权声明和许可原文。

## 检查与打包

```bash
python3 scripts/check.py
python3 -m unittest discover -s tests -v
python3 scripts/package.py
```

打包默认生成 `dist/document-diagrams.zip`，其中只有 `document-diagrams/` 及其内容。也可通过 `--output` 指定路径。使用安装目录本身运行完整性检查：

```bash
python3 scripts/check.py --skill-dir ~/.agents/skills/document-diagrams
```

这些检查不依赖 Git 元数据，验证入口、发布边界和本地引用。它们不能证明图文事实正确或视觉质量；行为回归仍需按 [evals/cases.md](evals/cases.md) 执行并记录结果。

## 来源与维护

内容建模和图形语义参考 [diagram-design](https://github.com/cathrynlavery/diagram-design)，浅色视觉规范参考 [Bybit svg-diagram](https://github.com/bybit-exchange/svg-diagram)。发布目录不携带这两个项目的源码仓库或原始 skill 入口，也不需要另行安装它们。

| 参考项目 | 参考提交 |
|---|---|
| cathrynlavery/diagram-design | `15d44aed098512a9345ebae636409846e2641496` |
| bybit-exchange/svg-diagram | `c30c9e3bc9a70f2b77b60c7ea27157de3a88d81a` |

内容边界是保留 diagram-design 的非样式指导，用 svg-diagram 的视觉样式替换其样式：

| 内容 | 处理方式 |
|---|---|
| 选图路由、45 种类型详规、9 个语义模式 | 保留细则、参数、条件和边界，按需加载 |
| 类型布局、连线语义、复杂度、可访问性 | 保留，包括生命线、条件片段、特殊关系端点和图表的数量语义；焦点预算不限制语义着色的元素数量 |
| 导入、保真度清单、SVG 与结构验证 | 保留 SVG 制作相关工作流及所引用的独立脚本 |
| HTML 页面、PNG 导出、动画控制器、单独的元数据导出 | 不在 SVG 制作范围内；直接编写 SVG，结构追踪信息保留在 SVG 属性中 |
| diagram-design 配色、字体、暗色、纸纹、海报卡片及品牌配置 | 移除；不带首次样式确认、profile、手绘和终端主题 |
| svg-diagram 视觉样式 | 取白底、五组浅色语义配色及关系箭头用色、中文系统字体、16/12/10px 基础字号、细描边、圆角及缺口箭头 |
| svg-diagram 选图、执行流程、输出位置和通用布线政策 | 不引入；图形结构和语义仍由 diagram-design 的规则决定 |

类型示例中的外观值转为统一视觉角色；配色、字体和 marker 改变时同步适配显示参数与箭头端点。移除依赖仓库的演示画廊和维护命令，实际用到的解析与结构验证脚本随包发布。原有 HTML 文字换行改为原生 SVG `text/tspan`。README 与来源说明不进入发布包，版权和许可原文保留为 LICENSE。

语义配色与焦点强调分开：输入蓝、处理橙、数据绿、分析紫、警告粉可在所有对应节点上重复使用；焦点通过轮廓、字重或图形规定的标记突出，不强制改成蓝色。去掉非焦点一律灰阶、分类系列禁用多色等外观限制，保留热力图的单色深浅标尺、蜂群图的统一填充、瀑布图的增量填充与减量空心，以及哑铃图的空心／实心端点。相关验证器按 `data-focal="true"` 识别焦点，Polar 保留 `data-polar-focal`；更新旧图时应明确补上焦点标记，蓝色本身不再表示焦点。

原有图标集合属于外观素材，不复制其中的第三方路径或品牌 logo；保留图标输入标识与含义，用通用图形或带名称的节点表达。类型中的尺寸公式保留结构关系，文字和徽标按新字体测量后扩展，数量图形则保持数值对应的坐标和面积。

本 skill 与上述参考材料均采用 MIT 许可。相关版权声明与许可原文保留在安装包的 [LICENSE](skills/document-diagrams/LICENSE) 中，不作为 Agent 的使用指导。

`upstream/` 中的两个 Git submodule 仅供维护者比较和审阅，保留原始文件。维护时按需初始化并检查：

```bash
git submodule update --init --recursive
python3 scripts/check.py --source
```

固定提交以 Git 中的 submodule 指针为准。`scripts/assemble.py` 是维护者使用的整理规则，按固定来源保留 SVG 制作相关的非样式内容；`scripts/semantic_colors.py` 集中适配用色指导与验证器的焦点识别。两者不随 skill 发布。发布目录中的视觉规范、SVG 模板、`check_svg.py`、展示元信息和许可独立维护，其余内容由整理脚本更新。

更新参考版本时先审阅差异，修订整理规则并运行 `python3 scripts/assemble.py`，更新本 README 中的参考版本，再运行完整性检查与图文行为回归。上游指针有意更新后，先暂存该指针再执行 `--source` 检查。普通安装和使用不执行整理脚本，也不需要初始化 submodule。

本仓库自己的指导和脚本采用 [MIT License](LICENSE)。本项目为独立整理，不代表参考项目的官方发布。
