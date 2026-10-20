# ball3d 开发文档总汇

本文由原先分散在 `ball3d/` 下的任务、需求、报告与审核文档合并而成，内容保持原样，只统一了标题层级并加了目录。原始文件已从仓库移除；需要查看拆分版本时，可在 git 提交 `2d1b87b` 中找到。

## 目录

- [JSON music ball video: implementation and review contract](#doc-task)
- [音乐弹球装置：开发需求与联合审核标准](#doc-music-machine-requirements)
- [彩色木板音乐装置：实现与审核报告](#doc-music-machine-report)
- [Codex independent review — changes required before visual acceptance](#doc-music-machine-review-1)
- [自然下落与倾斜木板反弹：Claude Code 开发需求包](#doc-natural-fall-requirements)
- [NATURAL_FALL 交付说明（第 2 轮收尾）](#doc-natural-fall-handoff)
- [Codex 独立审核：自然下落实验版](#doc-natural-fall-codex-review)
- [自然下落第二版：缩窄木板、拉开间隙、解决整曲穿板](#doc-natural-fall-spacing-requirements)
- [窄木板自然下落版：Codex 独立审核](#doc-natural-fall-spacing-review)
- [Three.js export prototype](#doc-realtime-task)
- [Three.js 快速版验收报告](#doc-realtime-report)
- [Reviewer checks during implementation](#doc-realtime-review-1)
- [Correct wood-drop to the actual reference video](#doc-reference-video-task)
- [实际视频参考版审核](#doc-reference-video-report)
- [参考模型与 JSON 适配](#doc-reference-asset-integration)
- [Supported wood boards, falling ball](#doc-wood-drop-task)
- [木板支架下落版审核](#doc-wood-drop-report)
- [Performance task 2026-10-10](#doc-performance-task)
- [渲染性能优化审核报告](#doc-performance-report)
- [Reviewer findings — must fix before acceptance](#doc-review-1)
- [Visual review and final integration corrections](#doc-review-2)
- [Final narrow corrections](#doc-review-3)
- [ball3d 独立审核报告](#doc-review-report)
- [网页 3D 调节与同场景视频导出：实施需求](#doc-web-editor-requirements)
- [网页小球视频编辑器：Codex 最终审核](#doc-web-editor-codex-review)
- [小球音乐视频：长音／滑音轨道规则交接](#doc-track-rules-handoff)


---

<a id="doc-task"></a>

## JSON music ball video: implementation and review contract

<p><sub>原文件：<code>ball3d/TASK.md</code></sub></p>


Planner/reviewer: Codex. Implementer: Claude Code using the existing DeepSeek provider.

### Scope
Create a standalone Blender-based true 3D video generator in ball3d only. Do not modify existing application files or discard any user changes. Do not change provider settings or read credentials. First milestone: a reproducible 12-second portrait preview from D:/Downloads/10_notes.json. Then full-song and sequential batch CLI. No new OCR, web UI, original vocal reconstruction or game controls.

### Input and timing
Accept jianpu2letter-notes-v1, lines[].notes[] in stored order. n=1..7 is scale degree, n=0 rest; o is signed octave. q is positive quarter-note duration. tempo_qpm is positive finite quarter-notes per minute. key=1=B transposes diatonic degrees; define middle 1=C as MIDI 60 and document it. letter is keyboard mapping, not pitch. Validate unknown notes, missing q, invalid tempo before rendering. Report errors with line/index. Rests consume time and never trigger audio or a new sounding landing. No implicit repeats or ties. All audio and animation derive from one absolute-time event list, with optional fixed lead-in. Never accumulate rounded per-note frames. Sample frames at frame_index/fps; a landing may lie between frames. Audio onset error <=1 sample and visual sampling error <=1 frame.

### Visual target
Reference is a pearl-like ball jumping across small suspended piano-like boards with visible thickness and supports, long shadows on a neutral background, colored glow and sparse star particles on each sounding landing, oblique follow camera. Geometry and lighting must be real 3D, not PIL painted pseudo-3D. Use deterministic analytic motion, no free-running physics. Ensure consecutive landings are continuous, board collision positions are correct, rests do not produce ghost strikes, repeated pitches remain separate events, and long notes do not create extreme leaps. Keep a single consistent visual template. Optional lyric text must not render broken Chinese glyphs; omit with clear explanation if font unavailable.

### Audio and output
Use built-in synthesized melody for MVP; call it synthesized, not sampled piano. No external sound asset downloads. Write WAV, render frames, mux H.264/yuv420p MP4 with audio using available imageio-ffmpeg executable. Paths must support spaces and Chinese via argument arrays, never shell concatenation. Preview defaults 360x640 30fps for timely review; final support 720x1280. Support --seconds preview, --output, --blender explicit executable and a bounded sequential batch mode. No input overwrites. Temporary files in per-run output directories. Fail on subprocess errors and report missing Blender clearly.

### Acceptance
Input fixture: 13 lines, 377 events =335 sounding +42 rests, sum q=188, tempo=65, exact score duration=188*60/65 seconds before lead/tail. Do not assert OCR correctness. Meaningful tests for rests, transposition, octave, repeated notes, invalid timing and absolute onset accumulation. Provide CLI help and a concise README, exact commands, dependency requirements, and known limitations. Reviewer runs tests independently, checks real rendered frames at several times and audio/video metadata. A successful code-generation response alone is NOT delivery.

### Current environment
Windows PowerShell; Python D:/python/python11/python.exe includes numpy, cv2, Pillow, imageio-ffmpeg. Blender not found in common install paths yet. No engine install or global modifications by implementer. Existing make_video.py is dirty: do not edit or import it. Only read if needed for conventions. Keep implementation small, avoid speculative abstraction.

---

<a id="doc-music-machine-requirements"></a>

## 音乐弹球装置：开发需求与联合审核标准

<p><sub>原文件：<code>ball3d/MUSIC_MACHINE_REQUIREMENTS.md</code></sub></p>


日期：2026-10-10。需求方：用户；开发：Claude Code（DeepSeek‑V4.1）；策划与技术审核：Codex；视觉验收：用户与 Codex 一起完成。

### 1. 目标与范围

输入不同歌曲的现有简谱 JSON，自动生成具有参考视频观感的纵向三维音乐装置视频，适合长期批量制作。优先解决木板模型、音乐驱动的非固定编排、长音/休止过渡和击板亮起。不得把当前固定 10 音符循环换一种排列后称为完成。

本轮采用“二维编排预览 → Blender 制作可复用模型 → Three.js 动画和快速导出”。二维预览是同一份场景数据的示意视图，不做先开发完整 2D 动画再重写 3D 的流程。

不包含歌词输出、歌词识别、简谱图片识别、社交平台界面、手机外框、发布功能。保留现有 classic 和 Blender 视频入口。现有其他业务文件的未提交修改不属于本任务。

### 2. 参考与输入

- 主要视频：`D:/微信文件存储/xwechat_files/wxid_m81o5g1ycsde22_7a76/msg/video/2026-09/7289cff2d3118ffb9cf9bb7a98f78d0f.mp4`。
- 木纹、支臂、圆底座、纵向构图参考：同目录 `7289cff2d3118ffb9cf9bb7a98f78d0f.jpg`。
- 彩色木板和同色击板亮起参考：同目录 `785eb7c5cc6ec1b244de8b247be0117b.jpg`。
- 已提取视频帧：`ball3d/out/reference_video/`。
- 真实歌曲：`D:/Downloads/10_notes.json`，格式 `jianpu2letter-notes-v1`。`n=0` 为休止，`q` 为四分音符拍数，`o` 为八度。`letter` 不是音高。沿用现有解析器的音高和时间定义。
- “空音”本轮按休止符理解。不要凭 JSON 行号断言那就是音乐乐句；没有乐句标注时，用休止、时值和节奏分组作为可解释的近似。

### 3. 木板和支架模型

用 Blender 创建可复现的建模脚本，实际运行产出 `.blend` 和 `.glb`，不能仅写脚本却声称已产出模型。

- 小木板有合理厚度、倒角、可见木纹；支撑为细金属弯臂、连接件和圆形安装底座，比例参照图片，不能像大货架。
- 可调整板面朝向与倾斜，不让板面、支架脱开。模型局部原点、上表面接触点/法线、支架安装点必须明确。
- 板面本身有颜色，木纹仍可见；至少展示暖木色、青、紫、绿、橙几种配色，不把全部部件一起染色。
- 材质用实时可支持的 PBR；Blender 程序材质需要烘焙或转成 GLB 可用贴图，不假设节点能原样导出。纹理尽量复用，外部资源和新依赖无必要不引入。
- Three.js 实际加载并使用该 GLB；模型预览应显示正面、侧面/斜面和击中前后，避免只有远景看不清结构。
- 目标是接近参考的造型和材质，不承诺通过翻拍素材还原原作者精确模型。

### 4. 一份场景数据，两种预览

音乐事件 → 编排数据（木板姿态/颜色/触板时刻、球路径、滑槽及原因）→ 2D 示意图和 3D 场景。

- 提供最小本地预览页面或可打开的自包含二维布局预览，能看见整段路线、音符/休止区间、长音/休止滑槽的触发原因；能定位当前播放时间更好，但不要扩大成完整编辑器。
- 二维与三维使用同一份数据，不各写一套布局公式。
- 提供短片和完整视频的现有 CLI 使用方式。正常生产的视频不显示调试标记。

### 5. 音乐驱动编排

- 木板可组成短横排、浅弧排、斜向单板、疏密变化的组合。根据音符数量、时值、节奏密度和休止选择与连接，而非 `index % 10` 的固定场景循环。
- 可以有少量可复用组合，但分组长度、朝向、间距应受歌曲影响；连续相同节奏允许合理重复，不能为了“随机”牺牲节奏和可读性。
- 同一输入和同一 seed 的路线可复现；不同歌曲实际产生不同编排。首版不需要为 seed 增加复杂 UI。
- 先校验空间与可达性，再输出路线；无可行滑槽时回退到安全的无声过渡，不能穿板或私自延长歌曲。
- 相机总体向下跟随，提前显示下一组物体；球的局部反弹清楚可见。画面边界、阴影范围和模型池按实际空间范围处理，不能依赖原来的固定板距。

### 6. 长音与休止使用滑槽

禁止每隔固定音符数放滑槽。每条滑槽都应记录可审计的触发依据。

- 长音：先在音符开始时击中彩色木板；在持续音及下一落点允许的时间内，用滑槽或平缓过渡延续运动。不要额外敲出新音，不改变音符时值。
- 休止：依据实际休止区间规划无声过渡，不把休止符当作发声音符的木板。保留原音频，不为填满动作擅自补声音。
- 条件必须兼顾拍数、实际可用秒数、空间距离和入槽/出槽时间。明确首版阈值与理由，做边界测试。短休止或短音不强行插槽。
- 不能把所有长 onset 间隔都称作长音；区分“发声音符持续时间”和“其后休止”。音符重叠时不能用持续时间代替可用转场时间。
- 槽有真实槽底和侧沿，球实际经过；曲线与球路径共用几何依据，入口、出口连续。木板、支架、滑槽、邻近装置不能明显互相穿插。
- 长音段的音频仍以现有合成器为准，不在本轮私自改音色/包络；如发现现有音频不足以表现持续音，应在交付中指出而非悄悄改曲。

### 7. 击板发光与动作

- 木板平时已有可辨底色。球在音符 onset 触板时，该块板同色亮起，短暂增强再自然衰减；木纹、板形和底色不能被烧成纯白。
- 仅被击中的木板亮起，复用材质/实例时不能导致其他板同时发光；连续密集击中可让不同板各自独立衰减。
- 不发声的休止不触发击板光；不加入歌词或大范围遮挡光团。
- 可以有小幅击板摆动，但必须保证触板位置正确，模型和支架连接自然；不要以随机晃动掩盖错误接触。
- 小球保留反光质感、接触反弹与总体下落。用解析路径保证节奏即可，不要求自由物理模拟。

### 8. 性能与兼容

- 保留 Three.js + WebCodecs 快速导出，Blender 用于一次性资产制作而非逐首逐帧渲染。
- 保留原 JSON 输入、音符 onset、曲长、帧率和音频；不覆盖输入、原参考媒体或上一版视频。
- 复用几何、贴图与材质，维护附近物体，避免为每首歌复制整套高面数模型或逐帧调用 Blender。
- 验收默认 720×1280、30 fps。当前整曲约 175.838 秒，上版本机端到端约 46.45 秒；新版本记录同条件实测，性能若明显变慢须解释与优化，不能把目标时间当实测。

### 9. 开发与联合审核顺序

1. 保存现状，检查当前代码；输出简短实现计划与必要假设。
2. 完成 Blender 木板资产和同数据二维编排预览；生成模型近景、多色、击中前后图片。
3. 接入三维短片，覆盖短音、长音、休止、密集音与不完整结尾；完成自动检查。
4. Codex 技术审核：模型确实加载，触板准时，颜色独立，路径连续，无明显穿插，滑槽全部有合规触发原因，图像和视频能打开。
5. 交付 10–20 秒代表性样片和真实歌完整视频、计时、运行命令、已知不足。Codex 和用户一起看模型、排列、亮起与滑槽过渡。未经用户看过样片，不把“视觉通过”记成事实。

### 10. 验收清单

- [ ] `.blend`、`.glb`、建模脚本均可用，实时场景确实引用该模型。
- [ ] 木板形体、细支架和圆底座近景可辨；基础配色与击中发光都保留木纹。
- [ ] 2D/3D 使用相同编排数据，无固定每 N 音符必放滑槽的代码。
- [ ] 普通短音片段没有不合条件的滑槽；長音/休止示例有符合条件的平滑过渡。
- [ ] 所有音符 onset 对应正确接触；没有为路径改变音频、曲长或增添音符。
- [ ] 连续性、球与板/槽间距、颜色互不污染、末尾/全休止/单音边界都有必要的验证。
- [ ] 不同歌曲可处理，同输入可重现；整曲后半段模型不消失，无明显场景弹出。
- [ ] 真实整曲导出通过全帧检查，计时和音频对照记录真实。
- [ ] 样片与不足供用户审核；用户视觉意见待收到后单独记录。

### 11. 开发约束与交付报告

修改集中在 `ball3d/`。不得清理或覆盖根目录未提交修改，不改全局供应商设置，不读取/打印任何凭证。开发过程不要联系其他人或发布产物。

交付报告须写明改动文件、实际执行的命令、测试结果、产物绝对路径、性能记录、尚未完成项。没有运行的测试不得写“通过”。遇到问题先保留可审查结果，说明阻碍。

本机工具：Python `D:/python/python11/python.exe`；Node `D:/node/node.exe`；Blender `D:/apps/Blender/blender-4.5.3-windows-x64/blender.exe`；现有依赖在 `ball3d/realtime/node_modules`。模型与截图请写入项目目录，保留上一版视频以供对照。

---

<a id="doc-music-machine-report"></a>

## 彩色木板音乐装置：实现与审核报告

<p><sub>原文件：<code>ball3d/MUSIC_MACHINE_REPORT.md</code></sub></p>


2026-10-10。需求见 `MUSIC_MACHINE_REQUIREMENTS.md`。状态：首版实现和技术审核完成，待用户视觉审核，未声明与参考视频完全一致。

> **后续更新（同日，窄板间距版）**：木板已从 0.60 m 缩到 **0.30 m 宽 × 0.06 m 厚 × 0.40 m 深**，球半径 0.22 → **0.10**，
> 渲染器默认加载 `assets/music_machine_compact.glb`（`--preset compact`），并在运行时量取真实载入的网格、
> 与 `realtime/src/layout.mjs` 的碰撞常量不符就报错。整曲 5276 帧、`forced == 0` / `clearance_fails == 0` / 板与板不互相穿插，
> 一键 CLI 导出已通过（`ERR_STRING_TOO_LONG` 根因是整段视频单次 POST 被浏览器镜像成超 512 MiB 的协议消息，已改为 2 MiB 有界分块上传）。
> 样片、抽帧、二维预览与实测数据见 `out/natural_fall_spacing/NATURAL_FALL_SPACING_HANDOFF.md` 与同目录 `delivery.json`。
> 本文以下内容描述首版 0.60 m 装置的实现与审核，仍可用于对照。

### 开发与审核

已将需求交给本机 Claude Code，通过 CC Switch 已保存的 DeepSeek 服务，以 `deepseek-flash`（DeepSeek-V4.1-Flash）运行。Claude 完成初版及一次审核修订；Codex 独立运行 Blender、测试和整曲导出，并修复审核中发现的问题。开发子进程不修改全局供应商，不在项目保存凭证。

主要修复：过宽分组、跨排穿板、滑槽入口擦碰、过曝丢失底色、模型预览相机、可见物体池容量、旧风格兼容。原开发交接草稿保存在 `out/music_machine_v2/claude_handoff_draft.md`，其未验证说明不代表最终状态。

### 实现

- `assets/build_music_machine.py`：Blender 生成带倒角木板、小接头、细弯铜支臂和圆底座，输出 `.blend`、嵌入木纹贴图的 `.glb` 和近景预览。GLB 的 Board/Arm/Foot 网格被实时场景实际加载。
- `realtime/src/layout.mjs`：2D/3D 共用编排；按音长、休止、密度和音高分组，横排、浅弧、斜排、单板变化，每组最多 5 块。同一输入和 seed 可重现。
- 长音候选要求至少 1.0 秒且 1.5 拍；休止候选至少 1.2 秒。还需跨组、可用时间至少 0.7 秒、端点距离至少 0.85、垂直落差至少 2.8、路径平均速度不超过 4.2；不满足时使用跳跃。各滑槽记录触发原因。实际槽底、侧沿和球路径共用曲线。
- `music_machine.mjs`、`instance_glow.mjs`：实例化 GLB，按板染色；命中板同色亮起并衰减，保留木纹。镜头总体下移，球反弹后继续下降。
- `make_layout_preview.py`、`preview2d.mjs`、`preview_build.mjs`：单文件 HTML 编排预览，显示路线、时间轴、休止和滑槽原因，可拖动时间；不播放音频。
- `make_realtime_video.py`、`export.mjs`、`export_session.mjs`：默认新风格 `music-machine`，保留 `classic` 和旧 `wood-drop` 用于对照；沿用 JSON、音频、批量及快速视频输出。
- 原 `score.py`、`audio.py`、Blender 视频入口及 classic 场景文件 SHA256 与开发前一致；未改根目录已有用户修改。

### 实际验证

- Python：84 项通过；JavaScript：90 项通过。
- 验证同输入可重现、不同曲目、单音/空编排、短音、长音、休止、精确 onset 接触、段间连续、GLB 网格及尺寸、二维预览导出。全休止输入仍遵循原解析器规则拒绝生成，并不承诺生成全休止视频。
- 真实《孤勇者》：335 个发声音符、42 个休止、80 组、14 条滑槽。全曲球与木板 OBB 检查通过；实际滑槽三角面密集采样检查通过，曲面离散容差 0.003（球半径 0.22，最小实测间距 0.217623）。这不是所有可能输入或装饰件的完整物理证明。
- Edge 打开最终二维 HTML，无页面错误，两个画布和时间滑块可用。
- 12.2 秒混合短片：366 帧全部解码通过，包含短音、长音与休止，最终版本 CLI 实测约 7 秒。
- 真实整曲：720×1280、30 fps、175.838 秒、5276 帧，H.264 + AAC；全部帧解码通过。端到端实测 **49.76 秒**，其中 CLI 49.39 秒、浏览器导出约 36.02 秒。GPU 为 RX 6500 XT，H.264 软件编码。这是本机单次结果，不是其他歌曲或长期批量保证。
- 整曲 WAV 与上一版逐字节相同。音频仍是 JSON 合成旋律，没有原唱或伴奏。
- 已抽查开头、35.37 秒滑槽衔接、中段和末尾图像；未见后段模型消失。详细证据在 `out/music_machine_v2/full_timing.json`、`full_wall.json`、`trough_validation.json`、`delivery_validation.json`。

### 交付文件（绝对路径）

- 需求：`D:/Letter piano jk/ball3d/MUSIC_MACHINE_REQUIREMENTS.md`
- 模型：`D:/Letter piano jk/ball3d/assets/music_machine.blend`、`D:/Letter piano jk/ball3d/assets/music_machine.glb`
- 模型预览：`D:/Letter piano jk/ball3d/out/music_machine_preview/oblique.png`、`palette.png`、`hit_before.png`、`hit_after.png`
- 混合审核样片：`D:/Letter piano jk/ball3d/out/music_machine_v2/mixed_review.mp4`
- 整曲：`D:/Letter piano jk/ball3d/out/孤勇者_彩色音乐装置_待审核.mp4`
- 二维预览：`D:/Letter piano jk/ball3d/out/music_machine_v2/layout_review.html`
- 整曲抽帧：`D:/Letter piano jk/ball3d/out/music_machine_v2/full_contact.jpg`

### 运行命令

在项目目录 PowerShell 运行；资产已生成，通常无需重建。

```powershell
# 整曲；换 --input 即可处理另一份相同格式 JSON
& D:/python/python11/python.exe ball3d/make_realtime_video.py --input D:/Downloads/10_notes.json --style music-machine --node D:/node/node.exe --output "D:/Letter piano jk/ball3d/out/孤勇者_音乐装置.mp4"
# 二维编排
& D:/python/python11/python.exe ball3d/make_layout_preview.py --input D:/Downloads/10_notes.json --output "D:/Letter piano jk/ball3d/out/孤勇者_编排2d.html"
# 验证
& D:/python/python11/python.exe -m pytest ball3d/tests -q
& D:/node/node.exe --test 'ball3d/realtime/tests/*.test.mjs'
# 需要修改模型时才重建
& D:/apps/Blender/blender-4.5.3-windows-x64/blender.exe -b -P ball3d/assets/build_music_machine.py -- --render-previews
```

以上模型构建和测试实际执行过；最终整曲通过 `out/music_machine_v2/render_review.py --full` 执行相同导出入口，额外保存计时及抽帧。二维预览也已实际生成并浏览器检查。

### 共同视觉审核与限制

待用户确认以下三项，不能提前标为通过：

1. 木板厚度、木纹、细支架和圆底座是否接近参考；当前木纹偏规则、阴影偏硬，质感尚有调整空间。
2. 排列是否足够自然；目前虽由歌曲决定分组与形状，横排仍偏多，属于有限形状规则，尚非对乐句的高级理解。
3. 同色亮起是否够明显、球的反弹及滑槽入口/出口是否顺畅；使用控制路径而非自由刚体物理，位置连续不等于全程速度/加速度物理连续。

未加入歌词、简谱图片识别或社交界面。未做数百首连续耐久测试；视频仍在浏览器内存中完成封装。支持按 JSON 顺序批量，但长期无人值守的稳定性需另行验证。

---

<a id="doc-music-machine-review-1"></a>

## Codex independent review — changes required before visual acceptance

<p><sub>原文件：<code>ball3d/MUSIC_MACHINE_REVIEW_1.md</code></sub></p>


The initial asset build ran successfully with Blender 4.5.3. The GLB/blend and five PNGs exist. No need to claim all Blender execution is pending now; reviewer ran it.

Independent probe: `D:/node/node.exe ball3d/out/music_machine_v2/audit_layout.mjs` (from workspace root). Current real song: max group 14, max board |X| 4.68, multiple sphere/board intersections. This cannot pass portrait render acceptance.

1. `groupLandings`: `current.length` is undefined; use actual members count. Add a dense-note regression that fails on over-wide groups. Validate visible width with actual camera and mesh bounds, including start pad and troughs.
2. Start pad directly above board 0 causes the ball to fall through its departing pad. Other row transitions intersect boards too. Motion must clear the source and every nearby board. Use an independent sphere/OBB probe on real score and varied fixtures; fix geometry/path rather than weakening tests.
3. Channel entry/exit currently bounce at the SAME coordinate because `channelCenter(seg,0)===seg.p0` and `channelCenter(seg,1)===seg.p1`. Actual trough spans onto the boards. Separate free entry/exit endpoints from contacts. Inspect actual triangle surfaces and nearby board/arm intersections. `channelNormal` sign flipping whenever dx changes can create a discontinuous twisted trough; use a continuous consistent normal, and safe control points/clearance. Reject unsafe channel candidates with an audited fallback instead of rendering intersections.
4. Requirements say use beat duration AND available seconds; current long-note rule only uses seconds, and excludes long notes within groups without proactively separating them. Add beat-aware decisions, record unrounded values for boundary validation, and use sustainable music-driven groups so eligible long notes can actually produce transitions. Do not create fixed periodic channels.
5. Preserve uninterrupted bounce/fall motion rather than restoring the old frozen hold on every short note. Small contact dwell is fine but half every short note is visually robotic. Long time budgets can use a chute; rests must stay silent.
6. Current Blender previews: metal arm disappears into black background, coloured preview removes wood texture entirely, outer colours cropped, only central arm shown. Use neutral lit background, frame all assemblies, retain shared wood texture tinted per board, show actual before/after appearance without clipping highlights. Improve grain away from uniform diagonal stripes. Add a visible small mount/joint where board meets arm if simple. Do not claim a colour/material near-view passed yet.
7. Check GLB geometry world transforms, coordinate axes, and dimensions, not just mesh names. Loader must actually use GLB in exported render; static route and async builder should be verified.
8. Scene pool coverage must use real spatial bounds (uneven rows) rather than assuming the old 12 notes per side always cover view. Protect end-of-song wall coverage. Remove any obsolete variables/imports introduced by this task, but do not touch unrelated existing code.

Keep the requested scope, revise tests to catch real errors, and report remaining limitations honestly. Codex will execute scripts and render again. User visual approval remains pending.

Actual runtime evidence: `out/music_machine_v2/draft.mp4` rendered the mixed fixture, 366 frames, loaded GLB successfully. `draft_contact.jpg` shows excessive row width, multiple washed-out near-white lit planks, and a visible lower wall edge. Thus geometry/asset transport works, but those appearance/coverage problems need fixes. Emissive should be modulated by the wood texture and preserve hue, with lower intensity/shorter decay as needed. Merely asserting per-instance attribute independence is insufficient.

`node --test realtime/tests/layout.test.mjs` failed the actual sphere/board test: channel segment at u=0.15 penetrates board 4 (d2=0.004035...). Fix the geometry, keep meaningful collision coverage.

Restore the old `wood-drop` CLI choice alongside `classic` and new `music-machine` so existing user commands and comparison runs still work. New default can be music-machine. Remove any test/README stale assumptions created by new default, while preserving old tests that verify classic motion.

Preview HTML embeds arbitrary song JSON directly inside a script; escape `<` as `\u003c` (and safe separators as appropriate) so song titles/lyrics containing `</script>` cannot break the page or run script. The Python preview CLI must reject output aliases to input and non-HTML suffixes before writing. New deletion logic should only remove its verified unique work directory. These are concrete input edgecases, not an invitation to build generic security infrastructure.

---

<a id="doc-natural-fall-requirements"></a>

## 自然下落与倾斜木板反弹：Claude Code 开发需求包

<p><sub>原文件：<code>ball3d/NATURAL_FALL_REQUIREMENTS.md</code></sub></p>


日期：2026-10-10。委托对象：外部 Claude Code，DeepSeek-V4.1-Flash。Codex 负责策划和独立审核；本轮实现、测试、样片生成均由受委托开发者执行。完成时必须交回真实 MP4 文件路径，而不只是渲染命令。

### 用户原始要求

“我现在希望小球是自然下落，而不是从右边最后一个木板跳跃到下一行的最左边的木板，要符合自然规律，如果要实现这种远距离跳跃，就把木板斜着放；同理若是有的音比较长，可以让小球弹得高好在小球触碰下一个木板时刚好响起下一个音。”

### 目标与优先级

1. 优先让木板位置适应球的下落轨迹和歌曲时间。取消每排向右走完后大幅向左重置的布局；下一块优先在当前球附近的下方，用自然连续的路线组织整曲。必要折返只能在碰撞时发生，倾斜板面给出可见原因。
2. 自由飞行使用统一重力的解析抛体：p(t)=p0+v0*t+0.5*g*t²。水平匀速、竖直加速度固定，不可在空中 smoothstep 横移、突然改方向、绕前景 Z 偏移穿板或随意按插值控制点拉球。
3. 音符时间不可改。根据相邻发声音符的真实 onset 间隔反求飞行初速度、目标板位置与板面法线。长间隔允许更高的反弹和更长腾空；到达下一块板的时刻恰好是下一音 onset。不要在板上停住很久再快速赶路。
4. 对远距离横移或明显折返，真实倾斜承托面，不能只绕竖轴 yaw 装饰性旋转。记录碰撞前后速度和板面法线；接触点、球半径、显示姿态、碰撞检测使用同一数据。倾斜板与支架连接不能脱开。
5. 音乐同步优先但不可假称严格被动真实物理：任意不规则音长与有限画幅下，单靠固定被动木板未必可实现所有定时弹跳。优先用布局和下降高度解决；若需要供能，明确建模为有弹性的主动击板（轻微可见弹动），记录速度增益和限制，不允许静止木板无说明无限增能。报告采用何种碰撞模型。困难输入应有明确可审计处理，不能悄悄改音频或恢复空中转向。

### 长音、休止与滑槽

- 本次“长音高弹”优先于上一轮“长音候选滑槽”。长音不必自动配滑槽；不改变音频包络、音高、音符个数和休止静音。
- 滑槽仍可用于确实需要的长休止或过渡，不得按固定音符周期生成，不得作为掩盖不连续运动的装饰。保留时须验证入口/出口位置和速度合理衔接、球贴合槽底、不穿侧沿。若本轮有理由减少滑槽，报告规则及实际数量。
- 长音高度与下一音间隔相关：同等端点条件下较长间隔应有更高顶点；不得统一低跳靠慢放凑时间。设置能容纳真实曲目长音的镜头，而非简单截断高度造成节拍错误。

### 画面、输入及兼容

- 保留现有 Blender GLB 彩色木板、细支臂、圆底座、木纹、命中同色亮起、反光球；不加歌词。
- 2D 预览与 3D 共用布局和运动；2D 应能看出板倾角和球路径。相机容纳高弹顶点和落点，下降跟随平滑，无突然追球导致眩晕。
- 新行为更新 `music-machine`，网页已有“小球弹跳视频”自动使用新版。保留 `classic`、`wood-drop` 及原音频/JSON 接口。
- 局限修改于 ball3d；不改根目录网页/歌词未提交工作，不安装软件、不联网取素材、不更改全局供应商或读取凭证、不提交或发布。只有开发调用可连接已配置模型服务。
- 可使用 Read/Edit/Write/Glob/Grep/Bash 执行项目代码与本机 Python/Node/Blender/Edge。禁止清理其他工作目录、删除旧视频、修改原曲谱。保留上一版用于审核对照。

### 验收与测试（必须实际执行）

1. 新增能重现旧缺陷的测试：跨排大回跳、空中变速/转向、长音低跳停顿；改为验证新版规则，不能简单删除不通过的测试或放宽穿透阈值。
2. 统一重力、飞行水平速度、有限差分竖直加速度；所有 onset 触点和相邻段位置连续；碰撞法线/反弹方向一致；倾斜板球面接触和全程 sphere/OBB 检查。记录主动供能（如有）。
3. 实际歌曲 `D:/Downloads/10_notes.json` 的完整 335 音符路径与整曲后段；密集短音、明显长音、休止、单音、混合节奏。检查球、倾斜板、支架、保留滑槽与相机可见范围。声明检查范围，不能声称有限采样证明所有输入。
4. Python 和 JS 测试都运行；更新过时的旧 music-machine 断言以新需求为准，classic/wood-drop 测试继续通过。
5. 生成 15–25 秒代表性样片（含自然下降、倾斜反弹、长音高弹、下一音精确触板），真实曲目前段样片，以及真实整曲。样片必须是本轮代码真实渲染，非旧 MP4 复制或静态图。整曲难以完成时如实交付样片和具体阻碍，不假报成功。
6. 默认 720×1280/30fps，报告实际帧数、解码验证、耗时；不把之前 50 秒结果当本次实测。不要把“用户视觉通过”记为事实。

### 工具、入口及输出

工作目录 `D:/Letter piano jk/ball3d`。Python `D:/python/python11/python.exe`；Node `D:/node/node.exe`；Blender `D:/apps/Blender/blender-4.5.3-windows-x64/blender.exe`；Edge 已安装。Git Bash 下工具用正斜杠绝对路径。环境已经有依赖，不需要安装。

主要文件：`realtime/src/layout.mjs`、`music_machine.mjs`、`preview2d.mjs`、`realtime/tests/layout.test.mjs`、`tests/test_realtime_video.py`。现有说明 `MUSIC_MACHINE_REPORT.md`。基线备份 `out/natural_fall/before.zip`。样片 JSON 可参考 `out/music_machine_v2/mixed.json`，需自行构造充分展示本轮变化的新例。

命令示例（Bash，当前目录 ball3d）：

```sh
D:/python/python11/python.exe -m pytest tests -q
D:/node/node.exe --test realtime/tests/*.test.mjs
D:/python/python11/python.exe make_realtime_video.py --input out/natural_fall/demo.json --node D:/node/node.exe --style music-machine --output out/natural_fall/deepseek_sample.mp4 --timing out/natural_fall/sample_timing.json
D:/python/python11/python.exe make_realtime_video.py --input D:/Downloads/10_notes.json --seconds 20 --node D:/node/node.exe --output out/natural_fall/song_sample.mp4
D:/python/python11/python.exe make_realtime_video.py --input D:/Downloads/10_notes.json --node D:/node/node.exe --output out/natural_fall/full_song.mp4 --timing out/natural_fall/full_timing.json
```

交回 `NATURAL_FALL_HANDOFF.md`：改动清单、运动/碰撞模型、实际测试与渲染命令及结果、已知不足、样片绝对路径。生成 `out/natural_fall/delivery.json`，列出实际存在的视频、时长、帧数、测试结果与当前模型。最终回复必须给出样片绝对路径，供 Codex 读取和展示给用户；不联系其他人，不外发上传视频。

---

<a id="doc-natural-fall-handoff"></a>

## NATURAL_FALL 交付说明（第 2 轮收尾）

<p><sub>原文件：<code>ball3d/NATURAL_FALL_HANDOFF.md</code></sub></p>


**结论一句话**：本轮把「自然下坠 + 真实倾斜板反弹」做成了可跑、可审、可回滚的实现并渲染出真实 MP4；
但**真实歌曲的密集段落仍有实质性穿板**，因此按评审指示：实验版源码隔离保存、`realtime/` 与测试
**已恢复到 `out/natural_fall/before.zip` 基线**（网页按钮回到已验收版本），样片只作为**实验交付**，
**不是生产版本**。没有声称密集段落的碰撞已解决。

---

### 1. 交付物（绝对路径）

#### 1.1 视频（全部为本轮实验版代码真实渲染，720x1280 / 30fps / H.264 yuv420p + AAC）

| 文件 | 内容 | 时长 | 帧数（实测解码） | 字节 |
|---|---|---|---|---|
| `D:/Letter piano jk/ball3d/out/natural_fall/natural_descent_demo.mp4` | 代表性演示：自然下坠、倾斜板转向、长音高弹、逐音精确落点 | 19.400 s | 582 = 582 | 5,544,676 |
| `D:/Letter piano jk/ball3d/out/natural_fall/song_sample.mp4` | 真实曲 `D:/Downloads/10_notes.json` 前 20 s | 20.000 s | 600 = 600 | 9,096,206 |
| `D:/Letter piano jk/ball3d/out/natural_fall/full_song.mp4` | 真实曲全曲（孤勇者，335 音符 + 42 休止） | 175.838 s | 5276 = 5276 | 109,622,151 |
| `D:/Letter piano jk/ball3d/out/natural_fall/baseline_restored_check.mp4` | 恢复基线后的自检片段（证明恢复后的代码可渲染） | 4.000 s | 120 | 1,182,737 |

- 演示与 20 s 样片由流水线一次跑完（`EXIT=0`，写了 `timing.json`）；渲染耗时见第 2 节。
- **全曲的 `timing.json` 缺失**：画面 5276 帧全部渲染并落盘到 `browser.mp4`（106,484,638 字节），
  但 Playwright 控制通道在传回成品文件时抛出 `ERR_STRING_TOO_LONG`（单条消息超过 V8 字符串上限），
  进程在写 `node.json`/`timing.json` 之前就退出了。我用流水线自带的 `mux()`（ffmpeg，
  `-c:v copy -c:a aac`）把 `browser.mp4` + `audio.wav` 合成了 `full_song.mp4`，
  并用 `count_video_frames()` 解码校验得到 5276 帧。**这是渲染器的一个已知规模限制，不是画面缺失。**

#### 1.2 2D 预览（与 3D 共用同一份 `layout.mjs` 数据；显示板面倾角、板面法线、球路径、主动击板环、审计面板）

- `D:/Letter piano jk/ball3d/out/natural_fall/preview_demo.html`
- `D:/Letter piano jk/ball3d/out/natural_fall/preview_song20.html`

#### 1.3 复核用抽帧 / 拼图（ffmpeg 从上面这些视频直接解码）

- `out/natural_fall/demo_contact.jpg`（演示 20 格拼图）
- `out/natural_fall/song_sample_contact.jpg`（真实曲 20 s 拼图）
- `out/natural_fall/full_song_contact.jpg`（全曲 8 格拼图）
- `out/natural_fall/frames/demo_apex.png`（长音高弹顶点）、`demo_strike.png`、`demo_mid.png`
- `out/natural_fall/frames/sample_f5.png` / `sample_f12.png` / `sample_f18.png`
- `out/natural_fall/frames/full_t26.png`、`full_t100.png`（**缺陷区**：密集段落的板堆叠/倾斜聚簇）

#### 1.4 实验版源码隔离（可回滚、可复核）

- `out/natural_fall/natural_fall_src/`（本轮改动过的 5 个文件的完整副本）
  - `realtime/src/layout.mjs`、`realtime/src/music_machine.mjs`、`realtime/src/preview2d.mjs`
  - `realtime/tests/layout.test.mjs`、`tests/test_realtime_video.py`
  - `diff_vs_before.patch`（相对 `before.zip` 基线的 unified diff）
- 基线与实验版的差异**只有这 5 个文件**（逐字节比对确认，其余 21 个快照文件字节相同）。

#### 1.5 可复现的审计数据

- `out/natural_fall/audit_report.json`：用**隔离副本**里的 `layout.mjs` 重新构建 demo / 20 s / 全曲三种
  layout 的 `audit` 与 60 点全路径球-OBB 扫描直方图（脚本 `out/natural_fall/audit_report.mjs`）。
- 其它测量脚本：`smoke.mjs`、`hist.mjs`、`window.mjs`（分时段统计）、`thr.mjs`（密度阈值）、
  `pen*.mjs`、`dbg*.mjs`、`ffmpeg_path.txt`。

---

### 2. 渲染实测（本轮，未沿用上一轮任何数字）

来自 `out/natural_fall/demo_timing.json` / `song_sample_timing.json`（流水线自己写的 JSON）：

| | 演示 | 真实曲 20 s |
|---|---|---|
| 帧数 / 时长 | 582 帧 / 19.400 s | 600 帧 / 20.000 s |
| 解码校验帧数 | 582 | 600 |
| CLI 总耗时 | 7.94 s（node 6.91 s） | 8.05 s（node 7.06 s） |
| 浏览器 setup / update / encode | 741 / 1164 / 2609 ms | 1103 / 1237 / 2425 ms |
| 场景 | music-machine，23 板位、5 组、seed 3601343228 | music-machine，222 板位、1 滑槽、80 组、seed 1074576649 |
| WebGL | ANGLE (AMD Radeon RX 6500 XT, D3D11)，非软件渲染 | 同左 |

全曲：5276 帧全部渲染完成并解码校验通过；`browser.mp4` 17:07-17:08 落盘，分块 mux 2.4 s。
**没有把上一轮 50 s 的结果当作本轮测量。**

---

### 3. 本轮代码改动（相对 `before.zip` 基线）

- `realtime/src/layout.mjs`：600 -> 1373 行。重写过渡求解（统一重力解析抛体 + 倾角可达域 + 落点/板姿联合选择）、
  `plankPose`/`hingeFor` 基准统一（`centre = hinge + (H/2)·n`，**与 `off` 无关**，这是「off=0.3 但看着居中」那个 bug 的根因）、
  全路径球-OBB 间隙检查（6 个粗采样 + 24 步细扫 + 沿板面最近点解析解）、板堆叠检测，以及审计字段
  （`transitions/flights/chutes/active_strikes/forced/clearance_fails/clearance_fail_deep/plank_overlaps/min_clearance/clearance_scan/...`）。
- `realtime/src/music_machine.mjs`：实例化板按 hinge 旋转（`setFromAxisAngle(Z, -tilt)`），
  支架/底座与板同一 pivot、不脱开；主动击板时板面按记录增益做 0.17 s 阻尼弹动；
  正交尺度与相机抬高放宽（`ORTHO_SCALE 9.5->10.5`、`CAM_LIFT 1.9->2.5`），保住高顶点与落点。
- `realtime/src/preview2d.mjs`：2D 预览按 `board.tilt` 旋转绘制板、画板面法线、主动击板画环，
  新增「本轮运动模型（可审计）」面板。
- `realtime/tests/layout.test.mjs`（269->395 行）与 `tests/test_realtime_video.py`（167->202 行）：见第 5 节。

---

### 4. 运动 / 碰撞模型（可审计）

1. **统一重力** `G = 6.5 m/s2`（`G_VEC = (0,-G,0)`）。每次自由飞行都是解析抛体
   `p(t) = p0 + v0·t + 0.5·g·t^2`，水平速度恒定、竖直加速度恒定；有限差分校验（测试 defect 2）
   断言 `vy = v0y - G·(t-t0)`、`ax = 0`、`ay = -G`。**空中不改向、不插值、不临时改重力。**
2. **碰撞**：法线 `n ∝ (v_out - v_in)`（切向分量被完整保留，不做任意偏转），
   `e = -(v_out·n)/(v_in·n)`。`e <= 1` = 被动反弹；`e > 1` = **主动弹性击板**，
   记录增益（`active_strike_boards` 里的 `e/dv/drop/apex`），渲染里可见板面弹动、2D 预览画环；
   上限 `E_MAX = 5.0`（强制回退 `E_FORCED = 9.0`）。全曲 47 次主动击板，全部可列。
3. **板姿唯一基准**：`plankPose(hinge, tilt, off)` -> `normal = (sin t, cos t)`、`tangent = (cos t, -sin t)`、
   `contact = hinge + (H/2)·n + off·tangent`、`centre = hinge + (H/2)·n`（与 off 无关）、
   `ball = contact + R·n`；`hingeFor` 是其逆。求解器间隙检查、渲染矩阵、2D 预览、测试四处
   **都用 `(centre, tilt)` 这一对数据**。
4. **支撑点**：`off = ±CONTACT_OFF = ±0.30 = W/2`，即球被支撑在它**行进方向的前缘**，
   板不会悬在球已离开的一侧（旧的「落在自己刚离开的板上」就是这样来的）。
5. **倾角可达域（解析）**：`n = (sin t, cos t)`、`s = tan t`，落点条件 `v_in·n < 0`
   化为 `tan t < -v_in.y/v_in.x`，与 `|t| <= TILT_MAX` 相交得到整个可达集合；
   横向位移区间 `dx ∈ [(v_in.x + s_lo·dvy)·T, (v_in.x + s_hi·dvy)·T]`（要求 `dvy > 0`）。
   即「板不能比落上来的轨迹更陡」——这是解析约束，不是调参。
6. **间隙检查**：候选弧对「本板 + 最近 6 块板」做全路径球-OBB 采样（6 个粗分数 + 24 步细扫 +
   沿板面坐标的解析最近点），高弹时另外对上方早期板做 3 点顶点检查；审计里公开
   `clearance_scan = 24`、每块板的 `clearance`、`clearance_fail(_deep)` 与失败清单。
7. **限速/步长**：`VX_MAX 2.2`、`V_MAX 6.0`、单次飞行横向 `STEP_MAX 0.60`、走廊 `X_BAND ±2.1`、
   `TILT_MAX 0.80 rad`；不允许「走到右边后跳回最左」的伪重置（测试 defect 1）。
8. **长音**：间隔越长、同端点下顶点越高（测试断言），长音**不自动**给滑槽；
   滑槽只在真正长的休止（`REST_CHANNEL_MIN = 1.2 s`、可用时间 >= 0.7 s、速度 <= 4.2 m/s）出现。
   全曲只有 **1 条**滑槽：`t0 = 115.669 s`，ride 9.258 s @ 0.606 m/s，休止 12.462 s，落差 7 m。
9. **确定性**：FNV-1a 种子 + mulberry32，无 `Math.random`（测试断言可复现）。

---

### 5. 测试实跑结果（真实执行，未放宽任何穿透阈值）

| 状态 | JS `D:/node/node.exe --test realtime/tests/*.test.mjs` | Python `D:/python/python11/python.exe -m pytest tests -q` |
|---|---|---|
| **实验版（隔离副本里那 5 个文件在树内时）** | tests 92 / suites 22 / **pass 92 / fail 0**（586 ms） | **85 passed**（2.78 s） |
| **恢复基线后（当前树 = 交给网页的状态）** | tests 90 / suites 22 / **pass 90 / fail 0** | **84 passed**（1.80 s） |

实验版新增/改写的关键断言：

- 精确落点：每个 onset 与球心-板面接触误差 `< 1e-9`（实测 8.5e-14）、每段接缝连续（实测 8.5e-14）。
- defect 1（隔行大跳重置）：`|dx| <= STEP_MAX`、走廊有界。
- defect 2（空中变速/转向）：水平速度恒定、`ay = -G`、`ax = 0`。
- defect 3（长音低跳/停顿）：长间隔顶点 > 短间隔顶点、长音无滑槽、`sit <= SIT_MAX`、单次飞行 <= `FLY_MAX`。
- 碰撞：法线单位长度、`e` 范围、主动击板记账（`e>1` 必须记录）。
- 穿透：**0.5 s 及以上间隔必须完全不擦板**（60 点扫描 `count == 0`、`clearance_fails == 0`、`plank_overlaps == 0`，
  四个 fixture，含音高差）；**密集间隔另立一条测试**，只断言「必须被报告」：
  `clearance_fails > 0`、失败清单非空、每条失败都带实测 `clearance`、`clearance_fail_deep <= clearance_fails`、
  `clearance_scan` 公开。**没有把穿透失败改写成通过，也没有删掉旧的兼容性覆盖。**
- Python 侧 `test_realtime_video.py` 把旧的「只按 yaw 判断的盒子探测」换成与求解器同一基准的
  **倾斜球-OBB**（`L.plankDistance`），并新增 `test_supported_spacing_never_touches_a_plank`。

---

### 6. 缺陷与限制（诚实清单，含实测数字）

#### 6.1 支持的密度区间（实测，均匀间隔 fixture，16 音）

| 间隔 | `clearance_fails` | 板相交 | 擦碰采样点 | 深穿（球心进板） |
|---|---|---|---|---|
| 1.0 / 0.8 / 0.6 / 0.5 s | 0 | 0 | 0 | 0 |
| 0.45 s | 1 | 0 | 26 | 0 |
| 0.40 s | 1 | 0 | 38 | 0 |
| 0.35 s | 2 | 0 | 124 | 0 |
| 0.30 s | 4 | 0 | 134 | 326 |
| 0.25 s | 5 | 2 | 463 | 145 |
| 0.24 s | 5 | 2 | 314 | 272 |
| 0.20 s | 2 | 12 | 152 | -- |

**>= 0.5 s 是这套「板宽 0.60 / 板厚 0.075 / 球半径 0.22 / G 6.5」机械组件的干净区间。**
更密的间隔在几何上无解：一次 0.25 s 的飞行最多下落 `0.9·0.5·G·T^2 ≈ 0.18 m`，
而板宽 0.60、球半径 0.22，球无法在落向下一块板的同时从上方那块板的下面穿过。

#### 6.2 真实歌曲（335 音符）实测

- `transitions 334`、`flights 333`、`chutes 1`、`active_strikes 47`、`forced 6`、`safe_mode_boards 0`，
  横向最大 0.6 m、最大顶点 2.693 m、最大倾角 0.80 rad、`descends true`。
- **间隙**：`clearance_fails = 135/334`（其中 `clearance_fail_deep = 71`）、`plank_overlaps = 44`、
  `min_clearance = 0`。60 点全路径扫描：667 段中 256 段存在「球心比球半径更近某块非落点板」的采样点，
  其中 **38 段的球心已经落在板体内部（d = 0，肉眼可见的穿板）**、63 段 < 0.05、22 段 < 0.10。
- **分时段**（用来区分「干净演示」与「真实缺陷」）：

| 窗口 | 段数 | 亚半径接近 | >0.10 深穿 | 球心在板内 | 最小距离 |
|---|---|---|---|---|---|
| 前 20 s | 82 | 2 | 0 | 0 | 0.1889（约 3 cm 擦入边缘） |
| 前 45 s | 153 | 15 | 7 | 2 | 0 |
| 全曲 | 667 | 256 | 123 | 38 | 0（最早出现在 t ≈ 23.91 s） |

  ⇒ **交付的 20 s 样片基本干净（只有两处 3 cm 级擦边、无穿板），实质性穿板从约 24 s 才开始**；
  全曲视频在 24 s 之后确实会看到球切入板、以及板与板相交（见 `frames/full_t26.png`、`frames/full_t100.png`）。
- **未解决**：这不是「浅/深分类后就当解决了」。分类只是把它公开出来；真正的修法（按密集段落
  一致地缩小机械组件，或全局重排布局）本轮**没有做**，也没有偷偷调阈值让它看起来通过。
- 其它未决：全曲缺 `timing.json`（见 1.1）；主动击板弹动幅度较小（0.010-0.085 rad）但可见；
  相机是固定正交 + 抬高的平滑跟随，没有做逐帧预测。

#### 6.3 复核范围的声明

测试与扫描都是**有限采样**（每段 60 点、求解器 24 步 + 解析最近点），**不能证明任意输入下都不穿板**；
上面所有数字都是在这台机器、这些 fixture / 这支曲子上实测得到的。音频包络、音高、音符数与休止静音
**未做任何修改**。

---

### 7. 当前仓库状态与如何恢复实验版

- **当前（交付给网页）状态 = `before.zip` 基线**：`realtime/src/{layout,music_machine,preview2d}.mjs`、
  `realtime/tests/layout.test.mjs`、`tests/test_realtime_video.py` 这 5 个文件已按基线还原（sha1 见 `delivery.json`），
  其余 21 个快照文件逐字节相同、未动。恢复后 JS 90/90、Python 84/84 全过，
  并用基线代码渲染了 `baseline_restored_check.mp4`（120 帧，EXIT=0）——**网页按钮不会落到坏版本上**。
- **想复看实验版**：把 `out/natural_fall/natural_fall_src/` 里的 5 个文件按相对路径复制回原位置即可
  （`diff_vs_before.patch` 是相对基线的完整改动）。复看后可再用 `before.zip` 还原。

复核命令（在 `D:/Letter piano jk/ball3d` 下）：

```
D:/node/node.exe --test realtime/tests/*.test.mjs
D:/python/python11/python.exe -m pytest tests -q

# 2D 预览（与 3D 同一份 layout 数据）
D:/python/python11/python.exe make_layout_preview.py --input out/natural_fall/demo_score.json --node D:/node/node.exe --output out/natural_fall/preview_demo.html

# 重新渲染（实验版；需先从 natural_fall_src 恢复那 5 个文件）
D:/python/python11/python.exe make_realtime_video.py --input out/natural_fall/demo_score.json --style music-machine --output out/natural_fall/natural_descent_demo.mp4 --timing out/natural_fall/demo_timing.json --node D:/node/node.exe --build-dir out/natural_fall/build
D:/python/python11/python.exe make_realtime_video.py --input D:/Downloads/10_notes.json --seconds 20 --style music-machine --output out/natural_fall/song_sample.mp4 --node D:/node/node.exe --build-dir out/natural_fall/build_song

# 重算审计数字（用隔离副本，不需改树）
D:/node/node.exe out/natural_fall/audit_report.mjs > out/natural_fall/audit_report.json
```

---

### 8. 本轮没做的事（范围声明）

- 没有安装任何软件、没有联网取素材、没有动 `web/` 与 `lyric_sync.py` 等根目录未提交的改动，
  没有提交、没有上传、没有删除任何旧视频。
- 没有为了「看起来通过」放宽穿透阈值或删除测试；旧的 `classic`/`wood-drop` 及其测试未动
  （92 个 JS 测试里包含它们，实验版全过）。
- 没有做全局布局重排/按段落缩放组件——这是密集段落缺陷的正解，留给下一轮（或明确接受降级）。

---

### 9. 复核用 plan.json（与视频一一对应）

- `out/natural_fall/demo_plan.json`（演示视频用的 layout plan）
- `out/natural_fall/song_sample_plan.json`（20 s 样片用的 plan；注意 plan 覆盖全曲，`--seconds` 只截取画面）
- `out/natural_fall/full_song_plan.json`（全曲）
- 独立复核：`ffmpeg -i <video> -f null -` 解码计数 = 582 / 600 / 5276 / 120，与 `timing.json` 一致。

---

<a id="doc-natural-fall-codex-review"></a>

## Codex 独立审核：自然下落实验版

<p><sub>原文件：<code>ball3d/NATURAL_FALL_CODEX_REVIEW.md</code></sub></p>


2026-10-10。外部开发者：Claude Code / DeepSeek-V4.1-Flash (`deepseek-flash`)；会话 `d031ef09-5415-4b17-99d8-0b381642e019`。需求、三轮委托与开发日志保存在 `out/natural_fall/`。本轮产品实现由外部会话完成，Codex 编写需求、退回意见及独立核查脚本，没有接手实现运动代码。

### 结论

收到真实演示样片、真实歌曲样片及完整 MP4。**演示方向可以共同审看，整曲自然运动验收不通过，不能部署到网页。** 实验源码已隔离在 `out/natural_fall/natural_fall_src/`，原网页所用代码已恢复。独立逐字节比对基线备份的 26 个文件，无差异。

### 独立证据

审核脚本 `out/natural_fall/codex_audit.mjs` 直接载入隔离实验源码，不使用已经恢复的旧版。按每段 101 个采样点，自行实现倾斜球/板 OBB 间距计算，不调用实现方的碰撞判断。

- 演示片：22 块板，触板时间误差约 2e-15；球/板检测没有穿透。自由飞行竖直加速度与统一重力误差约 1.83e-7，水平加速度约 4.44e-8。抽帧可见倾斜板和高弹，视觉效果仍待用户确认。
- 真实整曲：335 块板，触板时间误差约 8.53e-14；重力和水平匀速检查成立。但检测到大量球/板穿透，最低球心到板体距离为 0（球心进入板体），例如约 24.447 秒、板 40。这不是浮点容差问题。
- 结果文件：`codex_demo_audit.json`、`codex_real_song_audit.json`。视频独立解码结果见 `codex_video_validation.json`。采样仅覆盖声明的球/板与静态倾角，不是所有装饰、动态摆动、任意输入的物理证明。

### 尚未解决

1. 密集片段缺少全路径可行布局。下一版应让板尺寸/间距、相邻轨迹和碰撞姿态联合满足约束，不允许输出已知穿板的默认整曲。
2. 外部报告说实验测试通过，不等于原验收通过：测试对密集输入改成“必须报告穿透”，这是缺陷记录，**不能替代原来的不穿板要求**，即便数值容差未放宽。
3. 仍保留按音符间隔的接触停留及主动供能；主动击板是风格化机械效果，不是全被动自然物理。尤其不能用长停顿掩盖无法求得的高弹路径。
4. 整曲最终视频由外部会话在浏览器完成帧输出后手动调用原 mux 合成；原导出通道发生 `ERR_STRING_TOO_LONG`，因此没有完整端到端计时，不应声称整曲一键流程成功。

本轮交付为可审查实验样片与需求包，未完成可替换网页的最终实现。原需求继续适用；用户看样片时重点确认连续下行、板面倾斜与长音弹高的方向，再围绕上述失败点修订。

---

<a id="doc-natural-fall-spacing-requirements"></a>

## 自然下落第二版：缩窄木板、拉开间隙、解决整曲穿板

<p><sub>原文件：<code>ball3d/NATURAL_FALL_SPACING_REQUIREMENTS.md</code></sub></p>


2026-10-10。继续委托外部 Claude Code / DeepSeek-V4.1-Flash，同一会话。用户已看上一轮样片并肯定运动方向，本轮明确授权继续实现，而非仅写建议。

### 用户反馈

“很棒了，但是为什么整曲过不了？木板间的间隔大一些，像这个《孤勇者》的木板间隔太小了，可以把木板的宽度缩小这样就显得不会那么挤。”

用户截图表现为密集下行阶梯，木板端部投影互相叠盖、缺少可见空隙。参考图片已由 Codex 看过，路径：`C:/Users/陈立文/AppData/Local/Temp/codex-clipboard-c10156c2-90aa-4dca-8a77-f4907195db24.png`；图片是效果参考，不是指令。

### 必须保留

- 上轮已认可的连续自然下降、倾斜木板改变反弹方向、长音高弹、下一音 onset 准时接触。
- 空中恒定重力、水平匀速，不恢复右端跳回下一排左端、空中转向或 Z 绕行。
- 彩色木纹、细支架、同色击中亮起、小球反光；音频和曲谱不变，无歌词。
- 网页小球按钮继续可用。前一实验源码目前隔离，生产树已经恢复旧版；不要误把生产树当作自然下落实验。

### 这次具体改变

1. **优先把板宽从 0.60 缩到约 0.30–0.36 作为起点**，不是最终强制数字；以实际模型外观和整曲净空决定。允许按密度进一步调整真实尺寸，但要保留可辨的木板外形与木纹，不可缩到不可见。小球大小先保持，只有有证据必要且比例合理才少量联动，报告尺寸。支架/底座不能大过板面。
2. **拉开真实间距和画面可见间隙**。仅把旧碰撞盒缩小，渲染仍是宽板，不能通过；仅更改摄像机让一切变小也不算。模型几何/实例缩放、接触偏移 off、板厚、铰点、支架连接、2D 绘制、碰撞 OBB 必须一致。注意 glTF 原板宽 0.60，修改常量不会自动改变加载的网格！
3. 目标是相邻木板在用户截图这类密集下降段有明确可见空隙，不再像重叠台阶。视觉建议以当前板宽约 15% 的边缘间距为起点；涉及视角投影，以实际抽帧为准，不把建议值当伪精确验收数字。
4. 缩板优先，再调整下降落差、横向间隔、倾角和局部前瞻。密集音符可适配紧凑但分离的装置；不能把音符间隔/拍速改慢，不能通过提高无上限速度或跳出镜头换取间距。
5. 上轮“密集段是几何硬限制”只是当时固定尺寸和求解策略的限制，**不是歌曲无法实现的物理定理**。这次用户已经放开板宽约束，要实际探索可行尺寸与路线；优先小规模自动参数/尺寸试验，选出可行解，避免再做数十轮无目标字符串调参。
6. 绝不能以“记录密集穿透”代替修复。对 `10_notes.json` 整首做实际球/板全路径扫描，要求 0 个超过数值/离散合理容差的穿透；检查板与板、支架和保留滑槽，明确范围。原约 24.447 秒板 40 的深穿板是明确回归例。
7. 修复完整导出链的实际 `ERR_STRING_TOO_LONG` 原因（检查巨量调试输出/Playwright 通道/大对象重复序列化）；不要不经证据就归咎 100MB 视频，也不要只交手工 mux 的最终文件来假称一键导出成功。诊断后最小修改。

### 工作方式、范围

先读 `NATURAL_FALL_CODEX_REVIEW.md` 与 `NATURAL_FALL_HANDOFF.md`。将 `out/natural_fall/natural_fall_src/` 的实验实现恢复到工作树继续开发，先备份当前生产源/相关文件到新目录 `out/natural_fall_spacing/`。不得覆盖上轮样片和日志。

只修改必要的 ball3d 文件，根目录网页、歌词修改保持。不得安装软件、读取凭证、改全局设置、发布或联系他人。现有许可仍包括本机 Bash/Python/Node/Blender/Edge 测试和渲染。你负责代码和视频生成；Codex 负责需求、独立审核，用户看画面。

工具：Python `D:/python/python11/python.exe`；Node `D:/node/node.exe`；Blender `D:/apps/Blender/blender-4.5.3-windows-x64/blender.exe`；工作目录 `D:/Letter piano jk/ball3d`。

### 验证与交付

1. 针对整首真实歌曲和密集输入真正断言“无穿板”，不得删除/弱化为“有穿板也算测试通过”。检查所有 onset、统一重力、倾角与反弹方向、衔接和高弹镜头范围。
2. 运行 Python / JS 回归，保留 classic/wood-drop 兼容；报告实验源码、模型尺寸及实际测试结果。
3. **由你实际生成**：
   - `out/natural_fall_spacing/demo.mp4`：沿用上次 demo_score.json，便于对比板宽和间隙。
   - `out/natural_fall_spacing/dense_review.mp4`：整曲中 20–40 秒或其他最密集段，不要只挑稀疏片段。可先完整导出，再无损或重编码剪审核片，注明时间范围，保留音频同步。
   - `out/natural_fall_spacing/full_song.mp4`：实际 `D:/Downloads/10_notes.json`，720×1280/30fps，完整端到端 CLI 成功，记录计时、5276 帧全帧解码。
   - 对照抽帧、共享布局的 2D HTML、`delivery.json` 与 `NATURAL_FALL_SPACING_HANDOFF.md`。
4. 两段连续密集/长音样片都必须符合本轮方向：更窄、分离、自然下落、高弹准时接触。交付说清楚整曲是否真正通过；不能把样片成功当整曲成功。
5. 若仍无法完成，不用旧视频充数，不把错误版放进网页：隔离新版、恢复备份、交回实际样片和具体剩余失败。但先尽力利用本轮允许的缩板/间隙调整解决问题，不能直接沿用上一轮结论停止。

最终答复要给出真实存在的绝对视频路径。所有视频通过本地文件交回，不外发上传。

---

<a id="doc-natural-fall-spacing-review"></a>

## 窄木板自然下落版：Codex 独立审核

<p><sub>原文件：<code>ball3d/NATURAL_FALL_SPACING_REVIEW.md</code></sub></p>


2026-10-10。开发由外部 Claude Code / DeepSeek-V4.1-Flash 完成，沿用会话 `d031ef09-5415-4b17-99d8-0b381642e019`。Codex 编写需求、退回具体问题、独立复核，没有接手产品实现。委托记录在 `out/natural_fall/revision_*.jsonl`，本轮需求为 `NATURAL_FALL_SPACING_REQUIREMENTS.md`。

### 结果

**本次《孤勇者》整曲技术检查通过，新版保留在默认 music-machine 入口，网页“小球弹跳视频”会使用它。** 外观仍供用户共同审看，不提前声明用户验收。

原来密集音符下，宽木板与固定球尺寸/贪心排列导致球穿过旧板，部分板自身重叠。本轮板宽从 0.60 改为 0.30、厚度 0.06、深度 0.40；球半径从 0.22 改为 0.10，路线和姿态同时调整。真实 compact GLB、接触点、碰撞盒和视频显示尺寸一致，不能误载旧宽板。原资产保留。

### 独立验证

- Python + 网页相关回归：119 项通过、3 个子测试通过；JavaScript 最终复跑：106 项通过。
- 真实曲目 335 个音符，全路径每段 101 点的独立 sphere/倾斜 OBB 扫描：0 个超过数值容差的穿透，最小间距约 0.10，等于球半径。触板误差约 1.71e-13。自由飞行保持水平匀速和统一重力。
- 原 Python 整曲测试已改为明确要求 `forced == 0`、`clearance_fails == 0`、`plank_overlaps == 0`，并检查实际最小球/板间距；不能再以“报告失败”当作通过。
- 外部开发者的实际 GLB 三角面检查覆盖 Board/Arm/Foot，镜头与装置间距检查均通过。Codex 抽查 3、12、24.45、27、32、39、76、85、95、125、155、175 秒图像，可见窄板、板间空隙、倾斜板、长音高弹与后半段装置。
- 默认加载 `assets/music_machine_compact.glb`；渲染报告实测板宽 0.30000001、厚 0.06000000、深 0.40000001、球半径 0.10，尺寸检查通过。
- 原 WAV 与这次整曲 WAV 逐字节一致，没有改变节拍、旋律或曲长。
- 完整 CLI 正常结束，5276 帧编码及全帧解码通过，720×1280、30fps、约 175.84 秒，端到端实测 **76.908 秒**。不再需要手工 mux 补救。
- 大视频采用顺序分块上传，校验序号、块长度和总长度，避免原先大 POST 被浏览器网络调试通道放大后触发字符串上限。诊断用全局 socket 补丁已移出生产入口。

独立证据：`out/natural_fall_spacing/codex_current_audit.json`、`codex_video_validation.json`、`codex_smoke_contact.jpg`、`codex_full_contact.jpg`。实现方证据：`verify_src.json`、`full_song_timing.json`、`full_song.log`。

### 交付与边界

- `out/natural_fall_spacing/demo.mp4`：19.4 秒演示。
- `out/natural_fall_spacing/dense_review.mp4`：整曲视频时间 75.1–105.1 秒，最密集段，900 帧。
- `out/natural_fall_spacing/later_dense_review.mp4`：整曲视频时间 75.1–100.1 秒，750 帧。两段有重合，观看上一段即可；时间包含片头 1.2 秒，不是曲谱从零起算的时间。
- `out/natural_fall_spacing/full_song.mp4`：完整歌曲。

当前真实歌曲及测试输入通过，不代表任意歌曲、所有连续时刻和所有动态摆动都有数学证明，也未做数百首无人值守测试。球更小、个别折返点木板在屏幕投影中仍很接近，是否需要进一步调整视觉比例由用户看样片确认。外部 `screen_gaps.json` 的像素换算字段为 null，不把其中“低于若干像素的数量”为零当成有效像素间隙证据；本次外观判断依赖实际抽帧，几何不穿透与视觉间隙分开评价。自由飞行采用统一重力，但含记录在案的主动弹性击板，不把整套效果称为纯被动刚体物理。供能、接触停留和长休止滑槽仍属于音乐同步动画的设计选择。

---

<a id="doc-realtime-task"></a>

## Three.js export prototype

<p><sub>原文件：<code>ball3d/REALTIME_TASK.md</code></sub></p>


Implementer: Claude Code / DeepSeek. Reviewer: Codex. User approved this prototype.

Create a separate `realtime/` directory under ball3d and `make_realtime_video.py` CLI. Do not change existing score.py, audio.py, Blender renderer or existing CLI. Reuse them for plan/audio/validation where sensible. Preserve unrelated work and out/* benchmarks.

Goal: render first 10 seconds of D:/Downloads/10_notes.json at 720x1280 30fps (300 frames) much faster than Blender's 107.334 seconds. 20s is an unverified target, not a claim. Same plan, exact deterministic t=i/fps, same synthesized WAV. Full-song and existing batch input patterns should work if prototype succeeds.

Use locally installed npm three, canvas-record, playwright-core and esbuild (reviewer installs). Bundle browser JS locally using esbuild. Use existing Edge via Playwright channel msedge; no browser download, no CDN at runtime. Node orchestrator starts a loopback-only HTTP server, launches headless Edge with GPU allowed, calls browser export, captures download or local binary POST into unique work dir, closes browser/server in finally. Avoid transferring raw per-frame pixels through Playwright. Log actual WebGL vendor/renderer so software rendering is detectable. Exact frame count, export errors must fail nonzero; no screen recording/time-based MediaRecorder.

Read installed canvas-record API/source to get start/step/stop and download behavior right; start may encode frame 0 automatically so render it FIRST and avoid duplicate/off-by-one. Prefer WebCodecs encoder to MP4 with explicit duration/frameRate; autoDownload false and await completed buffer/download. Mediabunny (transitive dependency) can be used directly if canvas-record obstructs correctness; explain any deviation. Export losslessly timed frame count, H264 sensible bitrate ~8Mbps, audio mux with existing ffmpeg. No PNG sequence except a few optional QA snapshots. Use streaming output where straightforward; bounded encoder queue/backpressure.

Scene: use plan Y-up directly; match Blender camera by mapping Blender (-3,-6,5.5) offset -> Three(-3,5.5,-6), lookahead x .6, ortho vertical8. Gray floor, directional long shadows, soft fill, pearl ball, dark thick piano boards on narrow supports, colored landing flashes/sparse stars. Use fixed bounded pool of nearby boards/posts and particles, shared geometries/materials but independent glow state (avoid all boards glowing). Include enough offscreen shadow casters to avoid pop. Do not build 335 individual materials. Camera follows sample_track (no vertical bounce), ball uses exact sample_ball math. Floor and light follow track stably; camera near/far adequate. Add bloom if performant; avoid heavy complexity. Read render_scene.py for established visual style.

CLI supports --input --output --seconds --width --height --fps and --batch/--limit/--out-dir, default720x1280/30. Uses unique work directory, existing input validation, score plan, audio synth. Measure full CLI wall time, Node setup/render/export times and frame count into timing.json. End prints output + timings. No global config changes.

Add meaningful tests for JS/Python trajectory equivalence at all landings, rests, segment boundaries and representative midpoints; pool coverage at start/middle/end, incomplete export failure if feasible. Expose simple pure functions for motion unit tests. README setup/commands and explicitly state visual rendering differs. No assertions about speed before reviewer measures. Do not run shell; only Read/Write/Edit/Glob/Grep allowed. Reviewer installs deps and runs tests/benchmarks. Finish with changed files and risks.

Reviewer environment check: Node + headless Edge works outside sandbox, actual WebGL renderer ANGLE AMD Radeon RX 6500 XT Direct3D11. npm installed exact three 0.186.1, canvas-record 6.0.0, playwright-core 1.64.0, esbuild 0.28.2. canvas-record's option is `download: false` (not autoDownload), start({initOnly:true}) skips automatic first frame. Its WebCodecsEncoder stop returns ArrayBuffer, Recorder.stop may dispose encoder; inspect source carefully. Use loopback origin for secure WebCodecs context.

---

<a id="doc-realtime-report"></a>

## Three.js 快速版验收报告

<p><sub>原文件：<code>ball3d/REALTIME_REPORT.md</code></sub></p>


2026-10-10。Claude Code / DeepSeek 实现主体，Codex 策划、代码审核、修正与独立实测。当前机器为 Windows，WebGL 实际使用 AMD Radeon RX 6500 XT / ANGLE Direct3D11；H.264 使用浏览器软件编码。

### 结果

| 项目 | 优化后的 Blender | Three.js 快速版 |
|---|---:|---:|
| 同曲前 10 秒，720×1280，30 fps，300 帧 | 107.334 秒 | **7.078 秒** |
| 完整歌曲，5276 帧，约 2 分 56 秒 | 约 31 分钟（此前外推，未复测） | **44.850 秒（本轮实测）** |

10 秒比较约快 15.16 倍。最终外部计时覆盖 Python 进程启动、计划与合成音频、前端打包、Edge 启动、绘制和 H.264 编码、完整帧数解码检查、AAC 合成与进程退出；还包含 6 张审核截图。最终两次顺序执行，没有其它本任务渲染并行。不是屏幕录制，不以降低帧数或分辨率换速度。

两种渲染器画质与编码方式不同：Blender 为 EEVEE 16 samples + libx264 CRF20；快速版为 Three.js 阴影、MSAA、Bloom + WebCodecs 目标 8 Mbps。快速版阴影更硬，接触光更集中，不能称为无损或同等画质的提速。速度也不是其它机器、任意长曲的保证。

### 验证

- 75 项 Python 测试、74 项 JavaScript 测试通过，无失败。
- 真实整曲的全部帧时间、全部落点、段边界/中点和休止符端点/中点：JS 小球与镜头轨迹和 Python 原公式数值相等。另测带前置休止符、跨八度及尾部休止符的不同调号样本。
- 首轮同曲 10 秒计划与 Blender 计划结构完全相等，WAV 逐字节相等；歌曲处理与 Blender 管线四个原文件哈希未变。
- 10 秒视频完整解码为 300 帧；完整歌曲在 CLI 中完整解码为 5276 帧。最终容器 H.264/yuv420p、720×1280、30 fps，AAC 44.1 kHz 单声道，时长 175.87 秒，约 103 MB。
- 对照检查了 0、1.2、1.57、3.97、6.97、9.97 秒，以及整曲 60、120、173.33、175.83 秒。镜头方向、板体、球与阴影正常，后半段没有因对象池移动而被错误裁掉。
- 两份不同调号、速度且带休止符的 JSON 顺序批量导出通过，各 3 秒、90 帧。

### 关键实现及审核修复

1. 新增独立入口 `make_realtime_video.py`，复用原有 score/audio，保留原 Blender 命令。
2. 镜头附近实例化踏板/支柱与粒子池。本曲 28 个踏板槽、18 个粒子槽、5 个场景材质；颜色与发光按实例独立变化。
3. `t=i/fps` 同时控制动画和编码时间，避免首帧重复及累计时间误差；导出后核对帧数、文件字节数，再合成音轨。
4. 审核修复实例包围范围缓存导致的后段消失、坐标手性导致的镜头反向、过期粒子、审核帧参数与会话 token 拼接、脚本资源鉴权以及上传输出路径不一致。
5. 修复浏览器无法解析未使用编码器的裸模块导入；仅保留实际使用的 WebCodecs 路径。保留打包许可证注释。
6. 对发光强度作视觉调整，增加着色器编译错误失败路径。原有 Blender、音频、时间轴代码没有修改。

### 文件与使用

- 整曲：`D:/Letter piano jk/ball3d/out/孤勇者_快速版.mp4`
- 10 秒样片：`out/realtime_20261010/preview.mp4`
- 对照图：`out/realtime_20261010/comparison.jpg`
- 外部计时：`out/realtime_20261010/preview_final_wall.json`、`full_final_wall.json`
- 完整日志与各阶段计时：同目录 `preview_final.log`、`full_final.log`、对应 `*_timing.json`
- 元数据、源码哈希、计划/音频比对：同目录 `full_metadata.txt`、`source_hashes.json`、`audio_plan_check.json`
- 使用命令与批量说明：[realtime/README.md](realtime/README.md)

当前验证范围是约 3 分钟整曲及小规模顺序批量；尚未做数百首无人值守耐久测试。编码器按背压等待，但成品 MP4 在浏览器内存中封装后上传，本轮不宣称无限时长流式输出。音轨继续使用合成旋律，没有原唱、伴奏或新加入的歌词/OCR 功能。

---

<a id="doc-realtime-review-1"></a>

## Reviewer checks during implementation

<p><sub>原文件：<code>ball3d/REALTIME_REVIEW_1.md</code></sub></p>


- InstancedMesh bounding sphere is cached by Three.js. When moving a fixed instance pool along a 350m track, disable frustumCulled for these small pooled meshes or recompute bounds every update. Otherwise later-song objects/shadows disappear although matrices are correct. Test an actual rendered later frame.
- Swapping Blender Y/Z into a right-handed Three Y-up system reflects handedness. Inspect camera orientation against baseline; if track slopes opposite on screen, mirror projection horizontally (or use a proper rotation mapping for all coordinates) consistently. Motion can remain mathematically identical while screen appearance is reflected.
- Measured Edge headless WebGL on RX6500XT works. H264 VideoEncoder supports no-preference/prefer-software, prefer-hardware false. Do not force hardware. Simple 300-frame720x1280 H264 encode probe took0.792s; not a full scene benchmark.
- No need to implement unused parity helpers or tests of copied constants. Keep focus on rendered export and actual trajectory/pool correctness.

Reviewer already applied fixes in source while implementation proceeded:
- Scene Z reflection + matching camera Z restores handedness; frustumCulled=false on pools avoids cached bounds.
- /qa token query building fixed; bundle URL receives session token; upload saved at correct outPath.
- Unused encoder modules stubbed at build time (bare external imports prevented browser startup); legal comments retained.
- Recorder time explicitly i/fps; bloom reduced to .18 after visual QA.
- burstPool returns empty when latest burst expired; fade test threshold corrected to .001 of peak (original Blender formula gives .00019, not <.0001).

Measured first full CLI10s ~6s; full175.838s export46s,5276frames decoded. DO NOT overwrite these reviewer fixes. Finish remaining tests/docs; no speed claims beyond these measurements. Reviewer will author final performance report.

---

<a id="doc-reference-video-task"></a>

## Correct wood-drop to the actual reference video

<p><sub>原文件：<code>ball3d/REFERENCE_VIDEO_TASK.md</code></sub></p>


User rejected the staircase version and supplied an actual 9-second video. We inspected contact frames in out/reference_video/contact.jpg and dense.jpg (native vision by reviewer). Implement now, limited to realtime/src/wood_motion.mjs, realtime/src/wood_drop.mjs, matching tests/documentation. Preserve classic renderer, score/audio/export pipeline, all unrelated edits. No lyrics or phone/social UI.

Reference requirements:
- A dark grey vertical panel background with fine panel joints.
- Warm SMALL wood paddles mounted on ONE slim bent brass arm with a round dark/gold wall mounting foot. NOT two triangular shelf brackets. Paddles may tilt when struck (small damped response, correct contact at onset).
- Course composition: groups of 3-4 wood paddles forming shallow curved rows, mixed with diagonal single paddles, descending down the screen. NOT strict left/right alternation every note. Board width around .55-.65, ball radius around .23-.27 (reference sphere visibly large relative to board).
- Ball glossy pearlescent reflective sphere with strong broad cream/dark reflections. Use procedural environment via local Three RoomEnvironment/PMREM or an inexpensive generated environment, not a flat white ball or external asset. Keep GPU speed.
- Ball continuously bounces between notes, and falls between groups; no frozen hold then robotic slide on each note. Overall course downward but local upward bounce REQUIRED (previous monotonic-Y requirement was wrong). Preserve every exact original note onset and total duration; analytic deterministic trajectories, not physical solver.
- Curved golden open channels between selected row groups, with visibly raised sides; ball must actually follow the channel on those transitions, not pass through decorative scenery. Also curved double thin brass rails with a handful of hanging bead/bell shapes placed between groups/as side detail, with enough spacing to avoid ball passing through them. Keep these bounded/reused near camera, not all-song geometry.
- Camera vertically follows smoothly with ball's bounce visible in frame, front/slightly raised view showing board top, brackets, channels. Whole row width fits portrait. Light softly lit charcoal background, wood orange/golden, brass, strong but soft shadows. No flashy glow, no star effects.

Design simple dependency-free wood_motion helpers as source of truth for layout, onset-to-onset trajectories and channel centerline. Reuse functions in scene for exact geometry. E.g. deterministic repeating course sections grouping several notes; source rests can lengthen motion but must not add/delete time. Handle empty/single-note plans, lead and tail, partial final sections. Avoid abrupt camera jumps. Channel path should have valid clearance and use same analytic centerline for geometry/ball with radius offset; path endpoints at contacts continuous. At contact center sphere exactly one radius over local plank top (keep contact plank level if necessary; only rotate after ball departed to avoid collision).

Replace outdated monotonic staircase test with meaningful exact onset, continuity, finite motion, near-board no-penetration checks and channel geometry/path consistency using real song + edgecases. Do NOT simply remove coverage to pass. You have Read/Write/Edit/Glob/Grep only; reviewer runs tests/export. Do not invoke shell, credentials or network. Finish code with a concise report of files and limitations. Do not do unrelated cleanup.

---

<a id="doc-reference-video-report"></a>

## 实际视频参考版审核

<p><sub>原文件：<code>ball3d/REFERENCE_VIDEO_REPORT.md</code></sub></p>


2026-10-10。用户否定上一版左右交替阶梯，改以 7289cff2d3118ffb9cf9bb7a98f78d0f.mp4 的实际运动为准。Claude Code / DeepSeek 实现场景初稿，达到 30 轮上限后由 Codex 完成审核修正和验证。

### 本轮改变

- 单根弯金属支臂、圆安装脚、暖色木纹小拨片；浅弧形横排与斜向单板组合。
- 球触板反弹，整体沿纵向装置下降；原音符时刻不变，取消每个音符的固定停留。
- 宽弯槽使用连续槽底和两侧围边；球中心与槽面由同一条曲线及法线偏移得到。入槽、出槽连续。
- 增加固定在场景里的弯曲双轨挂珠；不会黏着相机移动。滑槽按空间范围保留，避免用时间范围造成可见位置突然消失。
- 程序化环境反射、曝光映射、柔和阴影、灰色大面板缝。没有歌词、手机外框和社交 UI。
- 修正初稿曝光过亮、路线过密、支架遮挡、短管代替弯槽，以及反弹碰到上方木板/上一段槽口的问题。

这是参考风格重建，不是原视频模型的逐像素复制。路线采用固定的 10 音符组合重复，尚未根据歌词或乐句自动设计变化；球由音符驱动的解析路径控制，不是自由刚体物理。音频仍是原 JSON 合成旋律。

### 结果与验证

- 完整输出：`D:/Letter piano jk/ball3d/out/孤勇者_机械木板参考版.mp4`
- 720×1280、30 fps、5276 帧，歌曲计划 175.838 秒。导出后全部帧解码检查通过。
- 本机整曲总耗时 **46.45 秒**，包含启动、渲染编码、全帧解码检查、音频合成及审核截图；单次测量，不是其他设备的速度保证。
- 76 项 Python 测试、77 项 JavaScript 测试通过。
- 对整曲各过渡密集采样，核对全部 335 个精确落点、连续性和球与带偏转角木板的间距。
- 对两轮装置组合的入槽、槽内、出槽及下一跳密集采样，检查实际三角形槽面与球的距离（网格离散误差容限 0.003 场景单位）；测试空音符、单音符、末尾不完整组合及可见滑槽池覆盖。
- WAV 与上一版逐字节相同。score.py、audio.py、Blender 入口/场景、classic 场景、导出管线的散列保持不变。
- 已查看首段、60 秒、120 秒、173 秒和曲尾截图。记录在 `out/reference_style/validation.json`、`full_wall.json`、`full_timing.json`、`full_contact.jpg`。
- 沙箱中的 Python 全套测试受系统临时目录权限影响，正常本机权限下重新运行全部通过；没有为绕过失败而修改旧测试。

### 命令

```powershell
python ball3d/make_realtime_video.py --input "D:/Downloads/10_notes.json" --style wood-drop --output "D:/Letter piano jk/ball3d/out/孤勇者_机械木板参考版.mp4"
```

之前的 `WOOD_DROP_REPORT.md` 留作旧阶梯版本记录，当前行为以本报告为准。

---

<a id="doc-reference-asset-integration"></a>

## 参考模型与 JSON 适配

<p><sub>原文件：<code>ball3d/REFERENCE_ASSET_INTEGRATION.md</code></sub></p>


默认 `music-machine` 视频入口和网页编辑器已换用新模型。

- 木板：参考图的粉色、米白、黄色木板平台（板面朝上，从墙面向外伸出），每个有声音符对应一次准确落板。
- 滑道：金色双轨、7 个下方固定挂件；不含示例滚动球。视频仍有一颗主动画小球。
- 自动分类：按 **q ≥ 2** 判断长音，与歌曲速度无关。长音落板后进入滑道，最后一个长音也生成滑道。休止符不新增模型。
- 原 JSON 的顺序、音高、节拍、休止时长不变，无需转换文件。
- 滑道会利用长音及后续休止期间持续滑行，末端直接接下一段下落。休止仍静音；不在轨道尽头停住等下一音符。出轨前平滑调整速度，与下落的初速度一致。最后一个长音收尾时减速停住。

很长的休止会降低滑行速度。例如此 JSON 的一段休止为 12.46 秒，保留原滑道长度时会缓慢滑行；若希望这类段落也保持较快速度，需要进一步加长轨道。

### 运行

在 `D:/Letter piano jk` 中运行：

```powershell
& "D:/python/python11/python.exe" ball3d/make_realtime_video.py `
  --input "D:/Downloads/10_notes.json" --style music-machine `
  --output "D:/Letter piano jk/ball3d/out/10_notes.mp4"
```

默认 720×1280、30 fps。查看长音段可加 `--start 18 --seconds 10`。
网页编辑器使用同一个资产和布局模块；打开的旧页面应刷新，若此前保存过板长设置，可重置几何参数以使用新默认板长 0.50 m。

### 可选延音与滑音

原文件只有时值，无法区分连音、延音或滑音，所以默认只按 q 判断长音，不自动猜测演奏标记。需要时可添加以下可选字段：

```json
{
  "format": "jianpu2letter-notes-v1",
  "key": "1=C",
  "tempo_qpm": 65,
  "lines": [{"notes": [
    {"n": 1, "o": 0, "q": 1},
    {"n": 3, "o": 0, "q": 2},
    {"n": 5, "o": 0, "q": 1, "articulation": "sustain"},
    {"n": 1, "o": 0, "q": 1, "articulation": "glissando",
     "glissando_to": {"n": 5, "o": 0}},
    {"n": 0, "o": 0, "q": 1}
  ]}]
}
```

`articulation` 可省略，或为 `normal`、`sustain`、`glissando`。后两者即使 q < 2 也使用滑道。`glissando_to` 为目标音级及八度，沿用当前调号；滑音需明确目标。休止符不能带延音/滑音标记。

明确延音的音量保持到音符结束再释放；滑音在音符时长内连续到达目标音高。未加字段时维持原来的合成音频。

### 模型与实现

- 源文件：`assets/reference_planks/reference_planks.blend`、`assets/reference_slide/reference_slide.blend`。
- 集成模型：`assets/reference_music_machine.blend`、`assets/reference_music_machine.glb`。
- 重建：`blender -b --python-exit-code 1 -P ball3d/assets/build_reference_music_machine.py`。
- 输入与音频：`score.py`、`audio.py`；运动：`realtime/src/layout.mjs`；显示：`realtime/src/music_machine.mjs`、`reference_geometry.mjs`。

木板默认尺寸为 0.30 × 0.06 × 0.50 m（宽、厚、深），后沿嵌入墙面 8 mm；底部增加金属支架和墙面圆形固定座，支架位于小球运动区域后方。改变板长时墙面与固定座随模型深度一起缩放。木板使用 Blender 烘焙木纹与三色调色板。滑道采用源模型的宽弧形轮廓，并根据行进方向翻转；实际模型和小球共用曲线坐标。普通跳跃使用重力抛物线，入轨与滑行按音符时间驱动，属于编排动画。镜头保留向下跟随，修正重复计算的俯视偏移，并加入 12° 侧视，让平台上表面、伸出深度及底部支架可见。可在编辑器调整斜视角和缩放。

### 本次验证

输入：`D:/Downloads/10_notes.json`。335 个有声音符、42 个休止符，生成 335 个音符木板和 14 条滑道；总时长 175.838 秒（含片头尾）。

- Python：120 项测试、29 个子测试通过。
- JavaScript：124 项测试通过，覆盖不同速度、最后一个长音、延音/滑音、休止期间不停顿、出轨速度连续性及实际 Blender 网格接触。
- 整曲路径扫描：木板穿透、滑道穿透、木板实体重叠及强制求解均为 0。双轨扫描容差 0.5 mm；本曲最小表面距离 0.0999192 m，球半径 0.1 m。密集段的木板画面投影仍可能遮挡，实体检测与屏幕可见性不同。
- 视频：720×1280 / 30 fps / H.264 + AAC，5276 帧编码和完整解码一致；RX 6500 XT，连续滑行版本实测用时 50.5 秒，详见 `out/smooth_slides/full_render.log`；合成音频与上一版逐字节一致。

最新连续滑行版：`out/smooth_slides/10_notes_smooth.mp4`；前后对比：`out/smooth_slides/comparison.mp4`；10 秒预览：`out/smooth_slides/preview.mp4`。

整曲原有 13 次滑道末端等待已全部取消。位置差分测得出轨速度衔接误差小于 0.000033 m/s；非终止滑道最低速度约 0.142 m/s，持续前进。详细导出与测试记录保存在 `out/smooth_slides/`；旧版保留在 `out/wall_mount/`，用于对比。

---

<a id="doc-wood-drop-task"></a>

## Supported wood boards, falling ball

<p><sub>原文件：<code>ball3d/WOOD_DROP_TASK.md</code></sub></p>


User approved replacing the fast renderer's boards with warm wood planks on metallic brackets, overall downward ball motion, NO lyrics. Implementer Claude Code/DeepSeek; reviewer Codex. Only edit realtime/src/wood_drop.mjs (new), realtime/src/export.mjs minimal selection, make_realtime_video.py minimal --style option and plan visual_style. Do not modify existing score/audio/Blender/classic scene, tests, docs or dependencies. Reviewer handles tests/docs. Do not inspect credentials. Use only Read/Write/Edit/Glob/Grep. Aim for a simple ~300-line new module, avoid sprawling parity helpers/tests. Finish when these edits are complete.

Reference image described by reviewer: small orange warm wooden planks, short gold/brass support arms and circular dark-gold wall mounting feet; grey vertical background, pearl/chrome ball falling from one board to lower boards arranged across the portrait frame. Need visually recognizable brackets, not long floor poles. No text/lyrics/social app overlay; no need ornamental bells or chute from reference image. Pure generated geometry/wood grain is enough.

Add --style choices classic/wood-drop, default wood-drop for this user's requested style; put visual_style in plan. In browser export choose buildWoodScene when plan.visual_style==='wood-drop', otherwise existing buildScene. Preserve same controller {update,render,stats,dispose}. Same audio/onset/frame timings and exporter. Output explicit paths used by reviewer so naming can stay compatible.

Suggested scene in Three Y-up: camera looks from positive Z slightly above toward vertical grey wall behind boards (plane XY at z=-.7). Each board top descends by ~.75m per sounding note, horizontal position sin(i*0.65)*1.25 and z~0. Board width~.85, depth~.6, thickness .10, ball radius .16. Board flat top Y normal, wood grain from deterministic canvas texture shared across pooled boards. Brass support consists of round wall foot, short horizontal arm and diagonal strut under wood, preferably two side triangles per board for readability. Fixed pool nearby indices enough for camera8m vertical view (back/ahead~10). Use shared geometries/materials or InstancedMesh, frustumCulled=false on moving pools. No per-note model/material construction.

Keep all motion analytic using existing plan.segments times and endpoints to identify board i (-1 pad to last board). Build new positions from board index. Hold on a board during segment hold, then fall to next LOWER board during hop: y=lerp(y0,y1,u*u), x smoothstep(u) between endpoints. Monotonic down during flight (no upward parabola), exact landing at original note onset. First lead-in: ball starts above first board at pad position then falls. In holds camera remains stable; smooth track interpolation for camera and aim lookahead down to show future boards. No random physics that can miss notes. Negative Y later in song must work: follow wall/light/shadow frustum with camera, short brackets attached to wall, no floor poles.

Use warm textured wood with visible thickness/beveled edges if existing Three addon helps; metallic/brass braces recognizable in shadows; pearl ball large enough to see; subtle brief impact glow, do not wash out wood with huge white emission. Lighting shadow one directional plus soft fill/env as useful. Keep scene fast (<20s for10s7201280) and no runtime network/assets. Import pure drop layout/motion functions from same module for reviewer tests? Better export layout/position helpers in separate wood_motion.mjs (allowed extra file) dependency-free for Node verification. No other files.

Actual environment ready npm under realtime/node_modules, three0.186.1, esbuild, canvas-record, Edge. Prior core supports same-size10s~7s/full176s~45s. Reviewer runs all code; do NOT claim execution/speed. Do not add lyric rendering; user only wants cost explained separately.

Motion correction before implementation: avoid ball falling THROUGH its departure plank. Prefer alternating board X=-1/+1 (wide zigzag) rather than close sinusoid. During a flight, x interpolates using smoothstep(u); y stays at source top until horizontal displacement clears half plank width + ball radius + .02, then y falls monotonically with squared normalized remaining progress to the next landing. Both endpoints retain exact note times. Camera X stays centered on the zigzag and follows descending Y, so both columns remain visible. This gives a short rolling departure followed by a drop, without an upward hop or passing through the departing board.

---

<a id="doc-wood-drop-report"></a>

## 木板支架下落版审核

<p><sub>原文件：<code>ball3d/WOOD_DROP_REPORT.md</code></sub></p>


2026-10-10。Claude Code / DeepSeek 实现主体；Codex 审核、修正并实测。用户要求：参考图中的支架木板、小球下落，不输出歌词。

### 交付

- 暖色木纹、圆角木板、双侧金属斜撑和圆形安装脚；灰色背景墙。
- 路线左右交替、每个音符逐级下降。先离开木板边缘再下落，避免从板体内部穿过；不是自由物理模拟，落点按原音符时序严格控制。
- 保留原合成旋律，未添加歌词。音高仍控制声音，新路线的高度由序号控制。
- 默认风格改为 `wood-drop`，原风格可用 `--style classic`。
- 完整视频：`D:/Letter piano jk/ball3d/out/孤勇者_木板下落.mp4`
- 样片：`out/wood_drop/preview.mp4`

### 验收

- 720×1280、30 fps；10 秒 300 帧，整曲约 175.84 秒共 5276 帧，全部解码通过。
- 最终外部总耗时：10 秒样片 **5.07 秒**，完整歌曲 **37.76 秒**。包括启动、计划/音频、绘制/编码、解码检查、合成和 6 张审核截图；本机单次最终测量，不是速度保证。首次整曲测得约 43 秒，运行负载/缓存会影响耗时。
- 76 项 Python 测试、74 项 JavaScript 测试通过。
- 新增真实整曲验证：335 个落点准时，所有视频帧和每个运动段的密集采样均不向上跳；球体与附近板体的距离检查未发现穿板。
- 完整 WAV 与上一版逐字节相等。
- 检查首段、60 秒、120 秒与曲尾画面；对象池和墙面在负 Y 的后半段保持可见。
- 审核修正：离板路径、双侧支架实际尺寸和可见底座、墙面曲尾余量、精确触板时刻的反馈，以及遮住木纹的过强闪光。

计时、日志、完整帧数和音频检查位于 `out/wood_drop/`，包括 `full_wall.json`、`full_timing.json`、`full.log`、`validation.json`、`full_contact.jpg`。

### 使用

```powershell
cd "D:/Letter piano jk"
python ball3d/make_realtime_video.py --input "D:/Downloads/10_notes.json" --style wood-drop --output "ball3d/out/孤勇者_木板下落.mp4"
```

### 歌词成本说明（本轮未实现）

该 JSON 有 263 项非空 lyric，已有音符时序。直接显示这些文本可以完全在本机实现，生成视频不需要新增识别或文字生成 API，因此不产生这类按字/按首的接口费用。仍消耗本机算力、电力；开发阶段的工具调用费用按用户已有账户计费。

普通字幕开发量较小；将歌词贴在对应木板附近、逐字变色和处理遮挡的工作量较高。还需核对空歌词是延长音、前奏还是漏字，不能仅凭非空字段数量保证整曲歌词完整。

渲染方案可预先缓存中文文字贴图并复用，避免逐帧重新排字。增加多少秒尚未做有/无歌词对照测试，本轮不虚构百分比或秒数。

---

<a id="doc-performance-task"></a>

## Performance task 2026-10-10

<p><sub>原文件：<code>ball3d/PERFORMANCE_TASK.md</code></sub></p>


Planner/reviewer: Codex; implementer: Claude Code with DeepSeek. User approved optimizing the EXISTING Blender version and comparing the SAME 10-second clip before/after. Keep existing uncommitted changes, only edit ball3d source/tests and relevant README. Baseline source snapshot and benchmark are in out/perf_20261010/baseline; DO NOT alter that snapshot or out/* evidence. Baseline is running via snapshot independently now.

### Fixed acceptance conditions
Input D:/Downloads/10_notes.json, first 10 seconds incl existing lead-in, 720x1280, 30 fps, 16 EEVEE samples, 300 frames. Same camera, geometry dimensions, light/shadow settings, colors, motion, timing, synth audio and encoding quality. NO performance claims through lowering quality, frame count or resolution. Actual wall-clock and image comparison are required by reviewer. Current 66 tests pass outside Windows sandbox; do not change score.py or audio.py unless demonstrated necessity (none expected).

### Optimize the measured structure, keep it simple
- Main likely cost: current loop calls bpy.ops.render.render(write_still=True) for EACH frame, reconstructing render state. Use a single animation render call with frame_change_pre/post handler updating analytic state t=(frame-1)/fps, persistent renderer across frames, proper handler removal in finally, exact output filenames frame_000001.png..frame_000300.png. Verify actual Blender 4.5 behavior, don't assume render result equivalence. Keep PNG validation in CLI.
- Reuse immutable star materials by palette, possibly idle board materials where safe; DO NOT make unrelated boards glow together by sharing mutable emissions. Static shader updates should be avoided.
- Bounded spatial window for nearby boards, posts and particles can help full-song scaling, but avoid complex speculative pool rewrite. Be conservative about offscreen shadow casters and point/sun shadows; do not pop objects or change visible shadows. If uncertain, implement only well-supported optimizations first and report deferred pooling. A preview-only prune that helps 10s but not full songs must not be presented as full-song speedup.
- PNG compression can be reduced without image quality change; do not remove debug frames or change CLI contracts unnecessarily. Encoding is a smaller contributor; no gratuitous dependencies or renderer migration.
- Add small explicit render timing/object/material stats to log (build and rendering wall seconds). Preserve nonzero failure exit and exact frame completeness checks.
- Tests should protect frame/time mapping, material independence if sharing, and any culling margin/boundary logic. Avoid mock tests that merely assert constants or code structure.
- Keep functions simple, no new version abstraction, no generalized render backend framework, no unrelated cleanup.

Implement directly; Codex will execute tests, compare 10sec before/after at identical settings and visually inspect frames (also later-song positions if culling). You have Read/Write/Edit/Glob/Grep tools, no shell. Do NOT claim execution. Blender installed at D:/apps/Blender/blender-4.5.3-windows-x64/blender.exe. Don't inspect credentials or provider settings. Finish with changed files, rationale and precise risks to check. Only change source in current ball3d, never snapshot in out.

---

<a id="doc-performance-report"></a>

## 渲染性能优化审核报告

<p><sub>原文件：<code>ball3d/PERFORMANCE_REPORT.md</code></sub></p>


日期：2026-10-10。实现：Claude Code / DeepSeek；策划、独立测试与审核：Codex。

### 结论

现有 Blender 管线优化通过本轮验收。同设置的 10 秒视频由 233.67 秒降至 107.33 秒，速度约为原来的 2.18 倍，耗时减少 54.07%。没有降低分辨率、帧率、采样数、阴影质量或视频编码质量。

### 基准条件与结果

| 项目 | 优化前 | 优化后 |
| --- | --- | --- |
| 输入 | D:/Downloads/10_notes.json | 相同 |
| 视频区间 | 前 10 秒，含原有片头 | 相同 |
| 分辨率 | 720x1280 | 相同 |
| 帧率 / 帧数 | 30 fps / 300 帧 | 相同 |
| EEVEE 采样 | 16 | 相同 |
| 总墙钟耗时 | 233.668 秒 | 107.334 秒 |
| 速度比 | 1 | 2.177 |

计时覆盖完整 CLI 调用、音频生成、Blender 启动与渲染、PNG 保存、MP4 编码。两次顺序执行，没有同时进行其它本任务渲染。测试是一次前后对照，硬件负载和驱动缓存仍可能影响重复测量结果。原始代码在 out/perf_20261010/baseline，修改前后源码哈希均已保存。

### 已实施

1. 将每帧独立调用渲染，改为一次连续动画渲染；每帧通过回调应用同一绝对时间的运动状态。
2. 星光粒子使用相同颜色时共享不可变材质，本曲实际使用 4 个；琴板保持独立材质，防止发光串联。
3. PNG 无损压缩级别从默认 15 调整到 10，减少压缩耗时，不减少图像位深。
4. 增加场景数量、建场耗时、逐帧平均耗时日志。
5. 审核补充动画回调失败和漏调用检查：发生错误后不能误判成功或继续合成过期画面。

没有修改 score.py 或 audio.py；相机、模型尺寸、灯光、阴影和编码设置保持不变。本轮保留全部 678 个对象，不做空间裁减，因此不声称已实现可视区域对象池，也不声称消除了长曲目的场景规模开销。

### 画质与正确性

- 最终测试：73 passed，0 failed。
- 相同 JSON 生成的计划完全相同；WAV 文件逐字节相同。
- 比较全部 300 帧原始 PNG 像素：284 帧完全一致；其它 16 帧合计只有 58 个 RGB 分量不同，最大差异为 2/255，整段平均绝对差为 7.23e-8（以 0..255 为尺度）。未观察到可见差异，不宣称所有帧位级一致。
- 人工视觉检查了 0、1.2、1.57、3.97、6.97、9.97 秒的前后对照，落点、镜头、阴影和发光一致。
- 两个 MP4 都完整解码成功：720x1280、30 fps、300 帧。
- 新增故障注入回归检查，模拟 Blender 吞掉回调异常时仍须报告渲染失败，并确保移除本次回调。

### 产物

- [优化前 10 秒视频](out/perf_20261010/before.mp4)
- [优化后 10 秒视频](out/perf_20261010/after.mp4)
- [画面对比](out/perf_20261010/comparison.jpg)
- [完整逐帧数据](out/perf_20261010/comparison.json)
- [优化前耗时](out/perf_20261010/before_timing.json)
- [优化后耗时](out/perf_20261010/after_timing.json)
- [优化后渲染日志](out/perf_20261010/after.log)

### 使用与边界

无需新增参数，原来的命令会自动走优化管线。例如：

```powershell
cd "D:/Letter piano jk"
python ball3d/make_ball_video.py --input "D:/Downloads/10_notes.json" --width 720 --height 1280 --fps 30 --samples 16 --output "D:/Letter piano jk/ball3d/out/孤勇者_优化版.mp4"
```

按本次 10 秒成绩线性外推，约 176 秒整曲可能在 31 分钟左右；这是估算，尚未重新执行整曲高清渲染，不能当作保证。若追求几分钟内批量出片，还需要下一轮针对实际 GPU 渲染负担和场景规模做测量；本轮没有通过牺牲画质来追求该目标。

---

<a id="doc-review-1"></a>

## Reviewer findings — must fix before acceptance

<p><sub>原文件：<code>ball3d/REVIEW_1.md</code></sub></p>


Independent pytest: 26 passed, 3 failed. Do not weaken tests to hide actual motion errors.

1. BLOCKER score.build_plan creates gaps between landing and next hop (dwell has no hold segment). sample_ball/sample_track fall through to final board. Repro with real fixture: t=1.315384615 returns x=350.7 instead of x=0. Insert explicit holds covering every dwell, ensure contiguous segments and exact landing endpoints. Add regression for all dwell intervals and near boundaries.
2. BLOCKER scene mixes Y-up plan with Z-up Blender ground/posts. Convert all plan coordinates consistently to Blender Z-up at renderer boundary (x,y,z -> x,z,y), including board dimensions, ball, support bases, particles, camera offsets/targets/fill. Or fully use Y-up renderer, but don't mix. Ground must cover entire track, including last board x=350.7. Factory-startup scene must be cleared of default cube/light/camera before build.
3. Tests: third note onset is lead+2*step, NOT lead+3*step; end is lead+3*step. Rest endpoint comparison suffers floating error: use an absolute tolerance <=1e-9 or quarter-beat positions; do not exclude a genuinely interior strike.
4. CLI reuses fixed .work directory, so rerunning a shorter video will encode stale extra frames; --clean may delete unrelated pre-existing files. Use tempfile.mkdtemp under output parent per run. Verify resolved cleanup path remains under intended output parent and is the exact newly created directory. Bound encoded frame count explicitly and consistent ceil(duration*fps). --seconds should cap preview at total duration.
5. Validate finite positive seconds, nonnegative finite lead/tail, positive samples, even output dimensions for yuv420p before writes. Validate input/output aliases using normalized resolved paths; restrict output suffix to .mp4. Batch same-basename inputs must not silently overwrite each other's output. Reject collisions before rendering or generate unique deterministic names.
6. Blender script errors may still exit 0: add --python-exit-code 1, fail before mux if frames are missing. Make samples actually apply to Blender 4.5; don't silently claim a setting worked.
7. Camera should follow sample_track for both position and target to avoid aiming up/down with every hop. First note should have a visible arriving hop, not sit there throughout lead-in and just flash.
8. Support CJK lyrics remains optional for first version; clearly document omission. No invented sampled-piano claims.

Blender is now installed and verified at D:/apps/Blender/blender-4.5.3-windows-x64/blender.exe. Add this path to discovery and README examples. Reviewer will run tests and render, so do not claim they passed without execution. Keep changes within ball3d.

---

<a id="doc-review-2"></a>

## Visual review and final integration corrections

<p><sub>原文件：<code>ball3d/REVIEW_2.md</code></sub></p>


Actual smoke render succeeded: 60 frames at 360x640, 2-second MP4 with audio. 60 tests passed at review time. Reviewer inspected frame 1 and frame 37 at the first landing. Current visual result is not acceptable yet: overly close camera, ball and active board pushed to lower right, nearly white low-contrast scene, white-clipped emission rather than colored glow. Reference has a small pearl ball, multiple suspended boards, neutral gray background and saturated cyan/yellow/orange contact light.

Make a focused final visual correction, preserve fixed timing and passing tests:
1. Camera: wider oblique side view with 4-6 boards readable and ball around center, entire ball visible through hop. Suggested orthographic camera scale 7.8-8.4 (portrait), offset approx (-3,-6,5.5), target lookahead around (0.6,0,0). Avoid distant horizon line and giant foreground board. Use track for smooth follow.
2. Neutral medium-gray floor/world, substantially less ambient and sun energy so shadows and color have contrast. Idle boards dark charcoal/blue or muted teal. Use saturated hue palette (cyan, green, yellow, orange, magenta by note/event), moderate emission rather than overexposing to white. Subtle colored point light near current landing can give the floor a colored halo (EEVEE material emission alone won't illuminate it). Ball remains glossy pearl, not a glowing white disk. Star bursts visible but sparse.
3. Replace legacy Glare socket property assignment if it causes RNA_float_set warning; use Blender 4.5 supported node inputs verified through introspection, avoid ignored errors.
4. Ground coverage currently uses fixed 500 units, rejecting longer valid songs; size the ground from board extents plus margin. Add test with >600 notes, no arbitrary valid-song length cap.
5. README: add Chinese quickstart with actual D:/apps/Blender path and clearly distinguish tested preview from untested full-song render. Keep synthesis/lyrics limitations honest. Do not claim finished reference matching.

Only edit ball3d. Reviewer will render a 12-second sample and small batch after fixes. Do not execute shell commands, do not edit previous review documents. No web UI, extra architecture, or new libraries needed.

---

<a id="doc-review-3"></a>

## Final narrow corrections

<p><sub>原文件：<code>ball3d/REVIEW_3.md</code></sub></p>


Actual visual frame after REVIEW_2 is substantially improved; keep camera/light layout. 12-second render is running successfully. Independent pytest now reports 68 passed, 3 failed:
- TestGlareHelper.test_a_value_that_does_not_stick_is_an_error: Ignoring.__setattr__ prevents default_value from existing even in __init__, so the test double itself is malformed. Initialize the value with object.__setattr__, then ignore subsequent changes, or remove these implementation-mirroring mock tests entirely in favor of the actual Blender smoke evidence.
- TestGlareHelper.test_missing_input_and_property_is_an_error: bpy is None outside Blender, but error formatting accesses bpy.app.version_string. Do not introduce general version compatibility abstraction for fixed Blender 4.5; simplest direct supported settings are preferred.
- TestPalette.test_idle_boards_stay_dark: IDLE_BOARD[i] is float, not iterable. This is a trivial implementation-mirroring test and should be removed (visual evidence is authoritative), or correctly sum IDLE_BOARD[:3] once.

Blender introspection verified Glare inputs in FOG_GLOW: Threshold default 1.0 and Size default 0.5 (normalized socket semantics differs from legacy integer size=7); socket accepts 7 but use 0.5 for predictable normalized size. Prefer direct Blender 4.5 node setup instead of speculative compatibility wrappers. Remove only helper tests made obsolete by simplifying that wrapper; retain meaningful geometry/timing/CLI regressions. Do not weaken actual behavioral tests.

Do not alter timeline, camera, or light layout now. Update Chinese quickstart/test report honestly. Restrict modifications to this directory. Reviewer will rerun final tests and batch. No claims of executed tests by implementer.

---

<a id="doc-review-report"></a>

## ball3d 独立审核报告

<p><sub>原文件：<code>ball3d/REVIEW_REPORT.md</code></sub></p>


日期：2026-10-09。策划与审核：Codex。实现：Claude Code，后端为用户 CC Switch 配置的 DeepSeek。

### 结论

通过原型验收：现有 jianpu2letter-notes-v1 JSON 可自动生成真正的 3D 小球踏板动画、合成旋律和竖屏 MP4；支持顺序批量输入。未宣称达到参考视频的美术完成度或成熟批量生产系统的稳定性。

### 本机环境

Blender 4.5.3 LTS 免安装版位于 D:/apps/Blender/blender-4.5.3-windows-x64/blender.exe，来自官方下载地址，SHA256 与官方校验文件一致。Python 使用 D:/python/python11/python.exe。未更改 CC Switch 供应商配置；凭证仅通过子进程环境传递，没有写入本目录。新增功能在 ball3d 目录，原项目已有的未提交修改未由本任务编辑。

### 已执行的验证

- 最终 pytest：66 passed，0 failed。覆盖音高与调号、八度、休止、重复音、绝对时间累计、非法输入、运动连续性、坐标转换、长曲目地面覆盖、输出路径和批量冲突。
- 最终样片：out/guyongzhe_final_preview.mp4，360x640，30fps，360 帧，12.000 秒，H.264/yuv420p + AAC。FFmpeg 全片解码成功。
- 批量验证：两份不同调号和速度的合成测试简谱，含休止与重复音；输出位于 out/qa_batch。分别为 46 帧与 48 帧，12fps，约 3.833 秒与 4.000 秒；均含 AAC 且完整解码成功。这不是多首真实歌曲的大规模验证。
- 整曲数据：D:/Downloads/10_notes.json；13 行，377 事件，335 发声音符，42 休止符，188 四分音符拍，65 QPM。谱面时长 173.538461538 秒；含 1.2 秒片头与 1.1 秒尾部，计划时长 175.838461538 秒。
- 整曲独立运动检查：335 个落点全部核对；最大位置误差约 1.39e-17，区间边界位置差为 0。生成完整 44.1kHz 单声道 WAV，7754476 个采样，时长 175.838458050 秒。
- 视觉检查：核对最终版本的落点、跳跃中间画面及 0.8、1.2、4、7、10、11.9 秒抽帧。确认 3D 踏板、支架、投影、跟随镜头和落点彩色光。见 out/final_contact.jpg。

### 审核发现并修复

1. 停留区间缺失导致小球瞬移到最后一块踏板，已补连续 hold 区间及回归验证。
2. 计划 Y 轴向上与 Blender Z 轴向上混用，已统一渲染边界坐标转换，并清空默认场景。
3. 固定工作目录可能使短视频编码混入旧帧，改为每次独立临时目录并核对帧数和帧名。
4. Blender 脚本失败可能被当作成功，添加非零脚本退出码及编码前帧完整性检查。
5. 增补数值参数、输出别名与批量重名冲突检查；地面改为随曲目范围计算。
6. 首版镜头太近、曝光过白，已调整为较宽的正交镜头和中性灰背景、彩色接触光。
7. 发光节点按实际 Blender 4.5 接口直接设置，删除不必要的版本兼容封装和对应模拟测试。

### 边界

- 未渲染完整约 176 秒的 720x1280 成片；整曲时间轴和音频已验证，高清完整渲染耗时与运行稳定性尚未验证。
- 批量为有上限的顺序 CLI 任务，不含后台服务、任务恢复或图形界面。
- 音频为合成旋律，不含原唱、伴奏，也不是钢琴采样音源；本次未做主观听感验收。
- 不显示歌词；不识别图片；直接消费已有 JSON。OCR 正确性、反复记号、连音与变速不在本轮支持范围。
- 画面仍是初版：支架与琴板造型较简单，低采样阴影可见噪点，美术效果需要用户确认。

### 复现

在 D:/Letter piano jk 下运行：

```powershell
python -m pytest ball3d/tests -q
python ball3d/make_ball_video.py --input "D:/Downloads/10_notes.json" --seconds 12 --samples 16 --output "D:/Letter piano jk/ball3d/out/my_preview.mp4"
```

批量：把同格式简谱 JSON 放入单独目录，使用 --batch "D:/你的简谱目录" --limit 3 --seconds 12。去掉 --seconds 可请求整曲；使用 --width 720 --height 1280 请求高清。更多参数见 README.md 和 --help。

机器可读证据：out/video_audit.json、out/full_score_audit.json；运行日志：out/final_render.log、out/batch_render.log；开发任务与返工要求：TASK.md、REVIEW_1.md、REVIEW_2.md、REVIEW_3.md。

---

<a id="doc-web-editor-requirements"></a>

## 网页 3D 调节与同场景视频导出：实施需求

<p><sub>原文件：<code>ball3d/WEB_EDITOR_REQUIREMENTS.md</code></sub></p>

2026-10-12。策划/审核 Codex，实现外部 Claude Code（DeepSeek-V4.1-Flash）。用户已明确授权开始。开发者负责实际代码、测试、样片。

### 范围与现状
项目 D:/Letter piano jk，进程 cwd=ball3d。修改 ../webapp.py、../web/library.html、必要 ../web/ 新页和 ball3d 源/测试/模型/构建。根目录有既有未提交用户改动：先备份涉及文件到 out/web_editor/before/，不覆盖旧视频、歌词/OCR逻辑。不安装、不读凭证/全局配置、不发布。
先读 NATURAL_FALL_SPACING_REQUIREMENTS.md 和 out/natural_fall_spacing/NATURAL_FALL_SPACING_HANDOFF.md；当前生产已是窄板自然下降且整曲通过，保留默认回归。
Blender 资产 assets/music_machine_compact.blend/glb 与 assets/build_music_machine.py 复用；允许额外 reference/editor GLB 不覆盖旧 compact。实际模型、碰撞尺寸、球、支架与接触点一致，禁止只缩碰撞盒。

### 已观察参考
D:/微信文件存储/xwechat_files/wxid_m81o5g1ycsde22_7a76/msg/video/2026-09/30751dd7dbf219c0245ecd2a378b2219.mp4
7.87s720x1280，抽帧 out/web_editor/reference_0..3.jpg/reference_contact.jpg。
参考长条圆角木板、细暗金属支架、深灰暖色墙面、彩色板与击中彩色光晕、反光球、柔和阴影。不复制手机/抖音界面、歌词，不承诺像素级复刻。按实际画面供用户审核。

### 第一版流程与真实可用控制
- 曲库添加“3D 调节/小球视频编辑”入口，直接生成按钮和原视频保留。中文独立编辑页，竖屏实时3D预览+面板，桌面能看全。
- 选择曲库已有歌，也可导入 jianpu2letter-notes-v1 JSON；从当前曲库选歌进入带入选择，清晰空态。图片识谱用原入口。
- 播放/暂停/从头、时间轴拖动/时间显示、试听开关。试听相同合成旋律；seek 和暂停调参后同时间显示确定状态，音频同步且不重复播放。
- 几何：板宽、板深（长条比例）、球大小、间距偏好、长音弹跳高度偏好；全部必须实质改变真实布局/碰撞/采样，可行范围实测。不只改变展示比例或tempo。高度调节至少用一个长音用例证明不同apex、onset不变。
- 视觉：板色/色彩强度、木纹强度、支架颜色、墙色、主光强度、曝光、击中光晕/辉光、阴影、相机缩放与斜视角；控件真实生效且全部影响导出。
- 几何变化防抖重新求解，视觉无需求物理。不每帧求布局。每页面/任务配置隔离，禁止可变模块全局常量导致串参数。轨迹求解不通过要说明，禁用导出，保留最近有效预览；不能假装调成功，参数联动要可见。
- 恢复默认、保存/载入设置JSON（简单复用），安全默认保持已通过335音的布局。给参考外观起点，几何不通过先保持安全尺寸。
- “导出10秒样片”（从当前时间起，范围明确）和“导出整曲”，MP4带音轨；720x1280/1080x1920、30/60fps、匹配码率可选。本机后台生成，非录屏，显示生成/耗时/真实日志/完成播放下载；失败可再试。
- 点击导出冻结歌曲+全部参数快照；预览与导出共用同一布局、GLB、场景、相机、灯光、绝对时间采样。报告保留配置/时间范围/几何。不得丢设置转默认CLI，不得含控制面板/歌词。
- 不做逐音手工拖动、不新换物理引擎、不做账号云端。

### 必须保留与验证
自然连续下降，斜板引导水平反射，空中恒定重力与水平匀速，长音真实高弹/明确接触停留，准确在下一音onset落板。无右端跨行到左端/空中转向/Z绕行。音高、tempo、onset、休止不改，滑槽只合理长休止，无歌词。
几何/间距/弹跳配置重求并检查forced/clearance/板重叠/全路径，失败配置不能导出。小球与板可辨、支架相连。实例池与材质复用；配置变化清理旧场景，不积累WebGLcontext/RAF/音频，旧异步结果不覆盖新操作。
输入/设置必须验证非有限数、尺寸、码率、时间范围、路径穿越、不支持格式；单导出任务互斥与唯一目录；失败不能返回旧视频。原 classic/wood-drop 与根网页回归保留。

### 本机工具
Python D:/python/python11/python.exe
Node D:/node/node.exe
Blender D:/apps/Blender/blender-4.5.3-windows-x64/blender.exe
Edge C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe
realtime/node_modules 有 three/playwright-core/esbuild/canvas-record，不另安装。
Flask 默认8010，测试可独立8011，不强杀占端口未知进程。后台进程必须隐藏窗口。只清理自己启动的进程。
ffmpeg用已有Python imageio_ffmpeg。不要 Bash 里裸python指向错误版本。

### 必须交付实际可审结果
1. 真实unit/API回归：非法配置、隔离、参数改变、尺寸一致、长音apex不同但onset不变、任务忙冲突、冻结设置与选歌真正进导出、失败不下载旧视频。
2. Playwright真正访问编辑页，选真实歌/导入JSON、播放暂停seek、调视觉与几何、重置/保存加载，断言实际布局/渲染变而非只文字变化，无控制台错误。
3. 由网页发起非默认配置的1080p30样片、真实《孤勇者》密接段，以及完整默认720p30整曲端到端5276帧；确认音轨/可播放/尺寸/帧数、记录本轮真实耗时。
4. 同设置同绝对时间同分辨率预览PNG与导出QA PNG，给Codex独立比较（压缩视频不要求逐像素一致）。
5. out/web_editor/ 实际产物：preview_editor.png、preview_frame.png/export_frame.png、edited_sample.mp4、dense_sample.mp4、full_song.mp4、editor_settings.json、delivery.json、WEB_EDITOR_HANDOFF.md。
交接含绝对路径、页面地址、真实测试结果、精确命令、控制范围与局限。不抄旧统计/耗时，不造假/弱化物理测试，不只交命令或计划。实施完整功能后实际生成并交回。

---

<a id="doc-web-editor-codex-review"></a>

## 网页小球视频编辑器：Codex 最终审核

<p><sub>原文件：<code>ball3d/WEB_EDITOR_CODEX_REVIEW.md</code></sub></p>


审核日期：2026-10-12。实现由实际外部 Claude Code 子进程完成，模型参数 deepseek-flash（DeepSeek-V4.1-Flash）；Codex 编写需求、复核并退回修改，未用内部代理冒充外部模型。
外部会话：d031ef09-5415-4b17-99d8-0b381642e019。最后一轮运行记录：out/natural_fall/revision_1791771774.jsonl，正常退出。

### 使用入口与交付

本机服务已启动：http://127.0.0.1:8010/editor?base=10 。曲库新增「3D 调节」入口。
可选曲库歌曲或导入音符 JSON，实时调板宽、板长、球大小、间距、长音弹跳偏好、板色、木纹、支架色、墙色、灯光、发光和镜头；可保存、下载、导入单套参数。
复用 Blender 导出的 GLB 资产，预览与视频导出共用场景、模型、时间和参数。没有输出歌词，音频为曲谱合成旋律。
导出支持当前播放位置的最多 10 秒样片或整曲，720p/1080p、30/60 fps。配置和曲谱在任务开始时冻结。

最终文件位于 D:/Letter piano jk/ball3d/out/web_editor/：
- edited_sample.mp4：1080×1920、30 fps、10 秒，最终修复版本。
- dense_sample.mp4：720×1280、30 fps、密集中段 10 秒，最终修复版本。
- full_song.mp4：《孤勇者》175.84 秒、720×1280、30 fps、5276 帧，本机任务记录耗时 39.5 秒。默认轨迹与发光未受最终修复影响，外部保存了旧视频帧与当前代码渲染帧的对照证据。
- edited_settings.json：可直接导入网页的编辑样片参数。editor_settings.json 是多套配置的交付汇总，不能整体导入。

### 独立审核发现及修复

1. 原音频每帧 seek 导致播放不连续，已改为读取音频时钟。实际浏览器测量 2 秒内 currentTime 只写入 1 次，画面与声音同步。
2. 非默认几何原扫描遗漏浅穿板：32.714 秒、56 号板、球半径 0.1 米，检测距离仅 0.09843 米。外部提高候选扫描密度并加入整曲扫描/极值细化，保留几何重新求解；Codex 对默认和编辑参数重新独立扫描，未发现穿板采样，335 个音的落点误差低于 2e-13 秒。
3. 改板色后命中光仍用旧调色板，已统一漫反射与发光的最终颜色。Codex 读取实际 GPU 实例属性核验：发光 = 最终板色 × 1.6，误差低于 1e-8。
4. 审核还推动修复：旧构建包造成空白页面、非法几何提交旧结果、并发临时目录冲突、未冻结源 JSON、帧数舍入不一致、畸形请求未拒绝、导出超时预算不足等。详见 CODEX_REVIEW_1.md 与 CODEX_REVIEW_2.md。

### 最终验证

- Python：138 passed，29 subtests passed。
- JavaScript：118 passed。
- 本机实际使用入口 8010：真实 Edge 浏览器 35/35 检查通过，无页面错误，证据 codex_browser_final.json、codex_editor_final.png。
- Codex 独立完整解码 5 个视频，解码帧数分别 300、300、5276、170、600，与交付元数据及文件哈希一致；均有 AAC 音轨。证据 codex_final_media_check.json。
- Codex 对两组独立获取的 PNG 作像素比较：edited_preview_frame vs edited_export_frame、dense_preview_frame vs dense_export_frame 均完全一致。H.264 压缩视频仍存在正常量化差异。

### 实际边界

这是完成可用流程的编辑版，不代表外观已完全还原参考视频，板形、支架可见度、构图、光照仍需用户看样片共同审美验收。
曲库默认几何下目前只确认 10、4、47 能通过排版，其余歌曲或参数组合可能失败；页面明确报告并禁用导出，尚未达到任意歌曲长期批量制作的目标。
弹道使用重力分段抛物线，并允许木板在命中时补充能量以匹配节奏；不是纯被动的物理仿真。数值轨迹检查不能作为所有连续路径的数学证明。
长期反复调整几何会累积浏览器动态模块，刷新页面可释放；1080p60 已验证 10 秒样片，未测试整曲。一次资源请求中断会导致导出失败，失败不会提供旧视频，可重新尝试。
实测耗时来自本机 RX 6500 XT、当前歌曲与指定规格，其他机器/歌曲/分辨率不能沿用此速度保证。

---

<a id="doc-track-rules-handoff"></a>

## 小球音乐视频：长音／滑音轨道规则交接

<p><sub>原文件：<code>ball3d/TRACK_RULES_HANDOFF.md</code></sub></p>


更新日期：2026-10-12。项目：`D:/Letter piano jk`。用户要求新开对话并交接，下一位请继续完成下面的代码修改和验收。

> 后续执行结果（2026-10-12）：本交接已完成。当前代码使用长音/滑音分类、能量积分轨道、休止滞空、逐音参考金珠及轨道尾光；最终结果见 `out/expressive_rails/ACCEPTANCE.md`。下文“当前状态”“尚未实现”保留为接手时的历史记录，不再代表当前实现。旧基线未覆盖。

> 最新执行结果（2026-10-13）：已按新综合指令切换为带 seed 的 3D 样条错落布局、逐跳固定顶点和极少轨道。30 秒 720×1280 / 60fps 验收通过，见 [spatial_course/ACCEPTANCE.md](out/spatial_course/ACCEPTANCE.md)。下文统一 g、长音自动轨道、七板宽构图等是历史规则，已被本轮用户指令覆盖。

> 本轮后续（2026-10-13）：用户又明确要求沿墙从上向下掉落、长轴垂直墙面、原比例长板、未击打黑色及 1–7 七色光晕。当前默认已切换为 `spatial.wallMounted=true`，最终视频和验收见 [wall_course/ACCEPTANCE.md](out/wall_course/ACCEPTANCE.md)。自由空间版本保留作历史对照。

> 歌词位置修正（2026-10-13）：按用户要求取消逐帧搜索空位，歌词始终居中位于对应木板投影下方，固定 8 px 间距。新视频：`out/wall_course/wall_drop_fixed_lyrics_30s.mp4`；720×1280 / 60fps / 1800 帧，11 个倒序寻帧截图一致。文字与文字、木板重叠均为 0；176 帧检测到文字矩形与经过的小球重叠，因此旧版“全部文字零重叠”验收未通过，不能标记为全项通过。未为躲避小球而移动文字。

### 0. 当前状态与授权

> 当前分组布局恢复滑道（2026-10-16）：用户要求先接回滑道，未调整转折落差或镜头。只在 `gap >= max(1 秒, 3.5 × median interval)` 的安全间隔插入原 Blender 双轨、金件及墙支架，整曲最多 3 条、起点至少隔 8 秒；采用水平平直轨道以保留木板世界 Z 长轴，接触点/高度/同高/对撞组不变，只局部重算进出板侧斜。整曲球路对固定滑道及支架避碰，轨道全程存在。164/215/335 音分别 3/3/2 条。相关 JS 212 项、Python 41 项通过；实际 8010 50 项检查、968 处球位和 24 张倒序截图通过。335 音 128–158 秒 1800 实帧板遮/挡球/出框/歌词相叠全 0；含滑道的网页后台 10 秒导出 `aba42bd83c33` 成功，300 帧编码解码一致、下载 HTTP 200。网页/Worker/导出 bundle 已更新，内部测试视频不交付。详见 [restore_rails/ACCEPTANCE.md](out/web_editor/restore_rails/ACCEPTANCE.md)。

> 导出统计兼容修复（2026-10-16）：当前分层布局包含 `gap:0`，但没有 `gap_threshold`；CLI 误选旧滑道日志导致编码前 KeyError。仅将日志分支条件改为检查 `gap_threshold`，不修改布局和画面。新增 4 项回归，相关 Python 共 38 项通过。使用失败任务 `af554cf78567` 的相同歌曲/设置/配置/窗口，经 8010 网页后台重试任务 `a88b8718cbad` 成功：10 秒 720×1280 / 30fps，300 帧编码解码一致，进度 100%，下载 HTTP 200。既有视觉标准未变，未向用户输出测试视频。详见 [export_stats_fix/ACCEPTANCE.md](out/web_editor/export_stats_fix/ACCEPTANCE.md)。

> 镜头急拉修复（2026-10-16，最新）：用户确认修复镜头强制快速重构图。已撤掉 layered 墙面镜头按“可容纳前方板前缀”硬切换 lens shift；复用同一 97 点球路采样，X/Y/Z Gaussian sigma 为原参数的 0.35/0.5/1，连续提前跟随。传真实球位置，用精确球轮廓和 C2 软边界做少量安全修正，保持纯时间/任意寻帧一致。原摆板投影守卫显式走 legacyWallFraming，三曲原板布局 JSON 精确不变。205 项相关 JS、37 项 Python 通过。实际 8010 三曲共 27181 个 60Hz 相机样本、13 项检查通过，球出框 0，横向构图补偿全 0，最大额外纵向补偿变化约 0.712px/帧。335 音 20–50 秒 1800 实帧构图补偿跳变从原最大 153.237px/帧降为 0，板相遮/挡球/出框/固定歌词重叠均 0，9 次倒序截图一致。镜头不强求远处木板全部入镜；该片段未来完整板数 1–6。网页/Worker/导出 bundle 已重建，未输出视频。详见 [smooth_camera/ACCEPTANCE.md](out/web_editor/smooth_camera/ACCEPTANCE.md)。下述错落板面、少量同高/对撞等布局保持。

> 回退后按新参考图修改（2026-10-16，最新）：用户再次要求下落/同高板朝上、少量相向对撞和错落下落。当前在昨日回退基线上修正：原 Blender 长板和 25°镜头不改，静止及击后最大倾角 25°，长轴仍为世界 Z、回弹绕 Z；同高入口/内部/出口横向恒速，静止严格水平且实际板顶同高；节奏不稳定或曲尾候选被排除。普通下落步高/横距按 seed 变化，下降组内少量对撞用真实前后速度反解约 ±20°。三曲 164/215/335 音保留 1/2/4 个同高组与 2/5/9 对相向板，下降占 94.6%–98.2%，滑道保留回退版的 0 条。200 项相关 JS、37 项 Python 通过；最终布局修改后的 7 项布局检查重跑通过。实际网页 35 项通过，Worker 0.98–1.79 秒；335 音 20–50 秒 1800 实帧板相遮/挡球/出框/固定歌词重叠均 0，9 次倒序一致，6450 点真实支架抽查无碰撞。网页与 Worker/导出 bundle 已更新，无视频输出。详见 [staggered_faces/ACCEPTANCE.md](out/web_editor/staggered_faces/ACCEPTANCE.md)。本条覆盖下述回退状态；更早的缩短木板/改变镜头/随机 yaw 试验仍未启用。

> 用户要求回退（2026-10-16，最新）：已恢复到 2026-10-15 18:26 最后的 `sparse_layers` 版。布局核心、分组规则和 GUI 的 SHA 与昨日记录完全一致；其余今日修改的源码/测试从原始历史读取或反向补丁恢复，完整配置取昨日浏览器报告，17 文件恢复、3 个今日新增文件退出生产。三首 164/215/335 音的 JSON 序列化布局与昨日保存数据精确一致，同高组 5/6/9、轨道 0；恢复原长板、25°镜头俯角、40°倾角上限，下落为主，仅少量 4–6 块同高。194 项 JS 与 37 项 Python 检查通过，网页/Worker/导出 bundle 已重建，8010 服务继续运行。今日回退前源码及构建已备份到 `out/web_editor/rollback_20261015/before_20261016/`，详见 [回退记录](out/web_editor/rollback_20261015/RESTORE.md)。下面两条今日倾斜修改保留为历史，已不代表当前版本；不要未经用户要求重新启用。

> 板面侧倾含义修正（2026-10-16，后续）：用户明确要求“长轴仍垂直墙面，板面绕该长轴侧倾”，否定上一条随机 yaw 让木板斜着插墙。当前 `wall-normal-roll` 模式取消逐板 yaw 和随机接触深度，静止及回弹都只绕世界 Z；法线仍由真实 v_out−v_in 求得，碰撞与渲染共用姿态，对应两个 GUI 参数已删除。保留原板拓扑/嵌墙支撑、2.6 长宽比、相机参数、seeded XY 错落及少量同高/对撞/回升；三首真实 API 曲谱各 3 条长间隔轨道。实际网页 Worker 约 7.26/8.13/11.39 秒，17 项网页检查、199 项相关 JS 和 48 项 Python 通过。335 音 20–50 秒 720×1280/60fps/1800 实帧的实际长轴误差 <5e-17，法线 z≈0，板间遮挡/挡球/出画均 0，球宽 7.392%–7.997%；9 次倒序截图一致，三首支架 95,202 点无碰撞。仍有 21 次球与固定歌词矩形重叠、未来完整板 3–10，旧视觉标准未全过。网页 bundle 已最终重建，8010 继续运行，没有输出视频。最新记录见 [wall_axis_roll/ACCEPTANCE.md](out/web_editor/wall_axis_roll/ACCEPTANCE.md)，下条 `upward_faces` 为被本次方向修正覆盖的历史结果。

> 板面向上与混合错落布局（2026-10-16）：按用户四张对照图修正，默认最大倾角 25°、全部法线 y≥0.9，同高板真实顶面同高且静止水平，对撞板 15°–25°，法线由实际 v_out−v_in 求得。保留 Blender 拓扑和嵌墙支架，板长/宽改为 2.6，镜头俯角 45°、yaw 25°以显示上表面。短组 2–4 音，下降为主，少量同高/对撞/回升，seed=20261013 可调；普通相邻高度差/横距变化至少 15%，特殊节奏组单独记录。三首 164/215/335 音实际网页 Worker 约 7.94/10.27/12.24 秒，各 3 条长间隔滑道，14 项网页检查通过。199 项相关 JS、最后采样修改后的 5 项布局检查、46 项 Python 检查通过；三首支架 95,202 点抽样无碰撞。335 音 20–50 秒、720×1280/60fps/1800 实帧板间遮挡、挡球、球出画均 0，球宽 7.392%–7.996%，9 次倒序截图一致。仍有 21 次球与固定歌词矩形重叠，前方完整板数 3–10，旧视觉验收并非全项通过。网页与 Worker bundle 已更新、8010 已启动，没有输出视频。详见 [upward_faces/ACCEPTANCE.md](out/web_editor/upward_faces/ACCEPTANCE.md)。下条 4–6 音同高版本及更早镜头/倾角/原板比例规则已被本轮覆盖。

> 同高改为少量点缀（2026-10-15）：用户否定全同高分层，要求仍以下落为主。当前 `layeredPhrases=true` 分支已改为普通组逐板下降，仅偶尔选择 4–6 块同高；至少先经过 4 个下降组，同高组之间至少隔 4 个完整下降组，平跳总数硬上限 20%。优先同音较多、节奏稳定的候选，seed 可复现，GUI 名称为「下落为主，少量同高横跳」。164 / 215 / 335 音保留 5 / 6 / 9 个同高组，平跳占 13.50% / 11.21% / 10.48%，其余全下降；最新实际网页 Worker 0.109–0.145 秒，14 项网页检查通过，35 项 JS、37 项 Python 检查通过。增加乐句间落差消除初测转折交叠后，30 秒 1800 帧板遮板／挡球／球出画均 0，9 次倒序截图一致。固定歌词仍有 25 帧重叠，未来完整板数 4–9，旧视觉标准仍非全项通过。网页和 Worker bundle 已更新，无视频输出。详见 [sparse_layers/ACCEPTANCE.md](out/web_editor/sparse_layers/ACCEPTANCE.md)。下条全同高试版已被本次覆盖。

> 乐句分层试版（2026-10-15）：按用户“每组 4–8 块同高、组间降一级”的最新要求，默认开启 `spatial.layeredPhrases=true`，GUI「乐句分层（每层 4–8 块）」可切回旧模式。当前采用直线层、同层连续横跳、换层反向下降；并非同一行内来回折返。保证实际板顶中心同高，转向保留真实斜面，最大约 39.52°，不是整层无倾斜。32 轮整层有限修正代替此模式逐板回溯，保留原 Blender 长板、嵌墙支撑和固定歌词。164 / 215 / 335 音分别为 29 / 38 / 60 层，组长全为 4–8；真实网页 Worker 最新约 1.9–3.5 秒（此前空闲时约 0.4–0.6 秒），进度、播放、CLI 一致性及缓存 14 项通过。最新定向 JS 26 项、Python 34 项通过；全套初跑 206 项中 205 过，1 项旧滑道测试的模式已修正，所在文件 6 项重跑通过。30 秒 1800 帧板遮板／挡球／球出画为零，9 次倒序截图一致；歌词仍有 13 帧重叠，未来完整板数 4–10，不能宣称旧视觉标准全部通过。8010 网页已更新，不输出视频。详见 [phrase_layers/ACCEPTANCE.md](out/web_editor/phrase_layers/ACCEPTANCE.md)。

> 335 音第 282 块失败修复（2026-10-15）：已用用户 8010 网页的完整曲目复现。三板同高组后接长间隔，原预检只看组内跨度，匀速出口被推至约 23 个板宽；后续恢复范围又未覆盖第 282 块。现同时预检入口/出口跨度，恢复识别与计数重置覆盖末板后第 4 块，预算与碰撞规则不放宽。完整 335 音通过，保留 5 组三板水平同高组；194 项 JS、25 项 Python 回归通过。实际 8010 Worker 90.755 秒到 100%，141.5 秒处可播放，切歌否/是与缓存通过。126–156 秒网页 1800 帧板间遮挡、遮球、出画面均为零，未输出视频；首次计算仍需约 1.5–2 分钟。详见 [stall282/ACCEPTANCE.md](out/web_editor/stall282/ACCEPTANCE.md)。


> 水平同高组（2026-10-15）：按用户最新要求，同高组改为 3–6 块相邻实际同音，板面静止时严格水平朝上（四元数 identity、法线向上、倾角 0°），击中回弹保留；不足 3 块不生成，安全回退不得缩为两块。入口/出口横向速度与整段横跳一致，转向由前后过渡板真实斜面承担，前后共享深度并预留横向转向空间。`levelMaxNotes=6`，前后端整数范围 3–6；`levelPhraseGap=4` 继续保持 3–5 个下降节奏段的间隔。实测 4 号曲 54.662–55.815 秒三板、45 号曲 28.500–28.950 秒三板；六连候选避碰后保留四板（不能宣称已经渲染六板整组）。192 项 JS、25 项 Python 全部通过；实际网页 Worker 与 CLI 一致，换歌取消与缓存通过。真实 30 秒 / 1800 帧木板相遮、木板遮球、球出框均 0，球宽 7.188%–7.846%，固定歌词矩形重叠计数 22 单独记录。网页 bundle 已更新，不输出视频。详见 [horizontal_levels/ACCEPTANCE.md](out/web_editor/horizontal_levels/ACCEPTANCE.md)。此前两板组的规则和 16.6 秒示例已被本次要求覆盖。


> 稀疏同音横跳（2026-10-14）：按用户最新要求改为先下降数段，等待 3–5 个完整节奏组后寻找连续实际同音，再安排 2–3 块同高横跳，随后继续下降；无合适音符则延后。整组共用尺寸／深度／高度，按时刻同向匀速横移，整组及出口一起预判并复用，困难组有限重排后缩短或放弃。配置新增 levelPhraseGap=4、levelMaxNotes=3，GUI、前后端验证与缓存同步。164 / 215 / 335 音符分别保留 4 / 7 / 10 组（这些真实曲子最终均为两板组）；不带歌词的 42 音符夹具通过三板连跳。190 项 JS、25 项接口回归通过，三首整曲碰撞／板重叠均为零。实际网页 164 音符 Worker 90.803 秒完成，进度、切歌否／是和缓存复用通过；4 号曲 16.6 秒可查看第一组。30 秒 1800 帧无板遮板／板挡球／球出画，同高组画面高度差最大 0.282 px，9 次倒序截图一致；固定歌词仍有 78 次重叠记录，不标记全项视觉通过。首次求解仍慢：命令行 106.872 / 343.730 / 463.912 秒（同时运行回归），本轮没有性能改善结论。网页和 8011 服务已更新，无视频输出。见 [稀疏同音横跳验收](out/web_editor/level_groups/ACCEPTANCE.md)。

> 排版反复回退修复（2026-10-14）：按用户要求修复 335 块曲子的局部反复搜索。预判保留并复用具体下一跳落点，检查多档间距及完整碰撞/投影；带 seed 连续采样，取消至少保留 3 组同高板的下限。跨索引停滞 24 次后重排局部节奏，最多 3 次，回退同步清理预判数据。335 / 215 / 164 音符整曲均排完，碰撞与间距门禁为零失败；实际网页 335 音符 Worker 52.399 秒完成并显示 100%，切歌否/是和缓存复用通过。保留同高对、明显侧斜与滑道，随机种子布局随搜索实现更新；2 处滑道测试夹具更新为有实体轨道的 seed=26，碰撞标准不变。186 项 JS 检查经针对性修正重跑通过，22 项接口回归通过；原卡住区间 30 秒 1800 帧板遮板/挡球/球出画均为零，9 次倒序一致，歌词重叠仍有 4 次记录，未声称全项视觉通过。网页 bundle 和 Worker 已更新，无视频输出。见 [搜索修复验收](out/web_editor/search_fix/ACCEPTANCE.md)。

> 两处百分比进度条（2026-10-14）：用户明确排版与视频渲染都要。实时预览区显示 Worker 阶段和木板处理进度，取消后不收旧消息，门禁通过后显示 100%；导出区按真实 frame n/N 日志更新，全部帧完成后以 99% 显示合成校验，后台任务成功才到 100%。失败保留本次进度并标红，新任务重置 0%。21 项 JS、22 项接口回归通过，四种布局带/不带进度回调结果一致；真实曲谱片段网页导入和内部 2 秒 60 帧导出验证通过，模拟失败重置通过，无页面错误。前端与 8011 服务已更新；内部测试视频不向用户输出。阶段权重不代表剩余时间，原 215 音符曲子求解很慢的限制未解决。见 [进度条验收](out/web_editor/progress_check/ACCEPTANCE.md)。

> 后台排版与切歌确认（2026-10-14）：按用户要求将网页 CPU 求解移至独立 Worker；排版期间切歌弹出“是否打断当前歌曲排版并切歌”，是=终止旧线程并加载新曲，否/Esc=继续旧任务并恢复原歌曲选择。尺寸变化在防抖前取消旧任务，参数快照、旧结果失效和最多 8 份结果缓存均保留。16 项 JS、21 项接口回归通过；223 音符原曲在拒绝切歌后完整完成，215 音符任务可被取消并由 164 音符新曲成功接管，后者 36.951 秒完成、计算期主线程定时器最大间隔 69.3ms。同配置缓存 10.6ms，无页面错误；8 音符 Worker 与原算法逐项相同。215 音符曲本身 240 秒内未完整排完，仍属求解耗时问题，不能声称已通过该曲完整验收。网页和 8011 服务已更新，无视频输出。见 [后台排版验收](out/web_editor/worker_check/ACCEPTANCE.md)。

> 未识别曲谱项兼容（2026-10-14）：按用户要求忽略 OCR 未识别项。仅对 n 缺失/null 且 unknown=true 的条目按原 q 时长作静音占位，不生成木板或音频起音，不前移后续事件；归一化事件保留 unknown=true，网页曲名处显示数量。其他格式错误仍拒绝，原曲谱文件不改写。58 项读谱/网页接口回归通过，包含静音与正常休止音频一致、后续起音不前移、原文件不变、有效音高不因陈旧 unknown 标记被吞掉。实际 out/52_notes.json 已通过运行中网页接口读取（HTTP 200）：223 个有效音符，L1 N13、L3 N28 分别占位 0.3/0.6 秒，总曲长 83.9 秒。前端 bundle 已更新，8011 服务已重载。记录：out/web_editor/unknown_52_check.json；本轮仅验收读谱与占位，没有声称该曲整曲排版/画面已通过。

> “千”板外观修复（2026-10-14）：用户指出上一版前后反向侧斜使“千”板像细长黑棍。本轮将转折段球路深度改为平滑变化，让明显倾斜主要来自左右冲量，局部前后坡度 ≤8°，并新增静止/回弹投影长度 0.75–1.35 倍门禁。“千”板前后坡度 16.26°→0.24°，对比投影长度最大 2.03→1.25 倍，模型尺寸保持原值。当前 164 音符曲子在 10.046 秒、106.008 秒有 29.42° / 28.83° 真实左右反向侧斜；保留 4 组同高板、114 次同侧跳跃、2 条常驻滑道。176 项回归通过，52–82 秒 1800 帧无板遮板、板遮球或球出画，9 次倒序截图一致，真实滑道/支架碰撞抽样通过。歌词重叠仍有记录，未标记全项视觉通过。网页已更新，无视频输出。见 [NATURAL_SLOPES_ACCEPTANCE.md](out/wall_course/NATURAL_SLOPES_ACCEPTANCE.md)。下列前后坡向反转方案已被本修复替代。

> 反向板含义修正（2026-10-14）：用户明确否定上一轮板面内 yaw 偏转，要求参考图中板面本身明显侧斜。本轮已撤回 yaw，改为在少量节奏边界局部重算接触点与抛物线，再由真实速度差计算板面法线；普通板仍 ≤15°，选定转折组允许使用 config.boards.maxTilt（默认 40°）。当前 164 音符曲子在 14.662 秒、59.277 秒生成两段反向侧斜，中心板实际 25.86° / 25.97°，共 10 块板超过 15°，相邻板深度坡向相反；原 4 组同高、114 次同侧跳跃和 2 条常驻滑道保留。175 项测试通过；30 秒网页帧检查无板遮板、板遮球或球出画，两段转折截图通过，实际滑道/支架碰撞检查通过。歌词矩形仍有重叠，未标记全项视觉通过。网页已更新，无视频输出。见 [SURFACE_ACCENTS_ACCEPTANCE.md](out/wall_course/SURFACE_ACCENTS_ACCEPTANCE.md)。上一条反向板验收为被撤回的历史方案。

> 节奏转折反向板（2026-10-14）：按用户要求在少量节奏组交界处刻意加入长轴反向的木板。先解原球路，再在真实板面内偏转朝向，接触点、时刻和反射法线保持一致；候选需通过墙面、完整飞行碰撞及投影检查，避开同高组合。当前网页 4 号曲子 164 块中 8 块反向板，4 组同高板，整曲约 46 秒；175 项测试通过，30 秒网页检查无板互相遮挡、板遮球或球出画，全部 8 块反向板各两张截图均方向相反。网页已更新，无视频输出；歌词矩形仍有重叠记录，不标记全项视觉通过。见 [PHRASE_ACCENTS_ACCEPTANCE.md](out/wall_course/PHRASE_ACCENTS_ACCEPTANCE.md)。

> 网页导出异常修复（2026-10-14）：墙面滑道统计使用 `t/flight_in`，旧验收脚本在轨道间距检查中误读自由空间版的 `t0`，导致有两条及以上滑道时在视频生成后抛出 `KeyError`，网页判定失败。现按布局模式还原离板时间，兼容两种统计格式；5 项 Python 回归测试通过，覆盖 0–3 条轨道和不足 8 秒的间距。原失败任务 `1e5e7f527ea4` 的真实报告已成功重算；用相同曲子、设置和 118.589728 秒起点，通过网页后台重试 10 秒 720×1280 / 30fps，任务 `006958d89fed` 正常完成，300 帧编码/解码一致，下载 HTTP 200。导出功能通过；既有视觉验收未全部通过，未修改其判定。核验记录：`out/web_editor/export_fix_check.json`。

> 固定滑道显示修正（2026-10-14）：按用户要求去掉墙面滑道的时间窗口隐藏，滑道、金色附件和嵌墙支架始终存在，由镜头视野决定是否可见；极少轨道生成条件不变。碰撞检查同步取消时间窗口过滤。8 项针对性测试通过，整曲实际网格碰撞抽样通过；42.5–54.5 秒网页 720 帧无报错、木板遮挡球或球出画，5 次倒序截图一致，原显示边界前后均可见滑道。网页 bundle 已更新，没有输出视频。验收数据：`out/wall_course/persistent_rail_web/browser_report.json`、`out/wall_course/persistent_rail_clearance.json`。

> 可见同高板修正（2026-10-14）：旧版只有球心同高，用户画面中看不见同高板。本轮改为提前成对预留、统一深度和尺寸、预判同高出口，普通相邻板投影留白加倍；有限重试后放弃个别困难组合。真实曲子生成 5 组同高板，击打前画面高度差均 <0.5 px，跳跃中与落板抽查最大约 1.82 px，横向空隙 66–141 px。172 项测试通过，30 秒网页帧检查及 15 张逐对截图完成；没有输出视频。见 [VISIBLE_LEVELS_ACCEPTANCE.md](out/wall_course/VISIBLE_LEVELS_ACCEPTANCE.md)。

> 同侧节奏分组（2026-10-13）：按用户确认改为短节奏内同侧局部往返、节奏组之间自然换侧，并为少量相邻同音尝试同高连接。新增独立 seed 派生的分组计划，回退搜索不会改变计划；所有实际板面仍满足真实法线、15° 倾角及碰撞要求。335 音符真实曲子生成 86 组、249 次同侧跳跃、136 对组内反向倾斜板、1 组同音同高连接。172 项测试通过，两段 30 秒网页帧检查完成，不输出视频。当前首次整曲求解约 134 秒，较上轮慢。见 [PHRASE_ACCEPTANCE.md](out/wall_course/PHRASE_ACCEPTANCE.md)。

> 滑道模型与排版性能（2026-10-13）：墙面模式改用 `reference_slide.blend` 已导出的真实双轨和金珠网格，并增加两组嵌墙固定支架；新增离轨飞行与滑道实体/支架检查，拒绝一段原有穿模轨道。缓存候选搜索中的重复投影、去掉冗余凸包计算，335 音符命令行实测约 99 秒降至 58 秒，首次排版仍非即时。171 项 JS 测试通过，网页 1020 帧验收，不输出视频。见 [SLIDE_SUPPORT_ACCEPTANCE.md](out/wall_course/SLIDE_SUPPORT_ACCEPTANCE.md)。

> 网页参考风格改进（2026-10-13）：用户已授权执行自然随机编排、板头回弹、支撑结构、墙面七色照明、球材质对照和极少轨道；明确无需输出视频。已完成并更新网页 bundle，记录见 [REFERENCE_STYLE_ACCEPTANCE.md](out/wall_course/REFERENCE_STYLE_ACCEPTANCE.md)。当前默认为该版；下文任务状态与先前视频均为历史记录。

> 转向修正（2026-10-13）：用户指出小球左右转向缺少板面倾斜依据。当前墙面版已将真实顶面法线与击球速度变化绑定，静止倾角 ≤15°，超限候选重选，球心与真实板面保持半径距离；轨道替换飞行后也重新计算两端法线。默认板宽改为 1.05D，下降基线为 2 板宽，保持紧凑的随机排布。网页 bundle 已更新，不输出视频；验收记录见 [TURNING_ACCEPTANCE.md](out/wall_course/TURNING_ACCEPTANCE.md)。历史独立随机倾角的描述已被此修正覆盖。

- 用户已明确要求开始改代码；最新任务是“轨道只用于长音和滑音，不用于休止”。不要停在方案阶段。
- 最新任务尚未开始写代码：此前只检查了输入、代码和旧验收，提出了兼容性问题；用户回答后要求换对话。
- 用户已确认：旧 `10_notes.json` 按 `q × 60 / tempo` 推算持续时间，兼容新增可选 `duration_sec` 和 `pitch_bend` 字段。推算值必须标为谱面时值，不冒充真实 MIDI note-off。不要再次询问这项。
- 此交接仅新建本文件，未修改业务源码。现有代码仍按上一版规则生成大量快速段、换行和休止跨越轨道，尚不符合最新要求。
- 本会话没有 `create_thread` / `handoff_thread` 工具；交接通过本文件及官方新建对话深链接完成准备，打开链接只预填消息，需要用户发送。不要声称已经有另一个代理接手。

### 1. 最新需求（优先于历史冲突规则）

#### 输入和分类

1. 输入支持音符持续时间（真实 note-off 对应的时长）及滑音信息；旧文件按已确认的 q 时值兼容。保留现有数据结构、音符起始时间，不重写用户 JSON。
2. `Δ0` 为全曲音符间隔中位数。所有阈值放 `ball3d/realtime/config.json`，并通过 lil-gui 暴露。
3. 长音：持续时间 `>= max(2 × Δ0, 0.5 秒)`，生成一段平缓轨道。
4. 滑音：有 pitch bend，或者连续至少 4 个单调音，且相邻间隔 `<= 0.5 × Δ0`、音高步长 `<= 2 个半音`。用一整条弯曲轨道替代这组木板；坡向跟随音高方向；轨道金珠随各个音依次亮起。
5. 其余情况不生成轨道；休止通过滞空处理。旧“快速间隔自动轨道”“长起音间隔自动轨道”“换行自动轨道”都被最新规则取代。不能把长休止误当长音，尾音之后的休止也不能延长轨道。

#### 时长与能量

1. 轨道时长 `min(持续时间, Δt - T_fly_min)`，`T_fly_min = 0.2 秒`。轨道结束后起跳，滞空到下一个音。
2. 轨道运动满足 `v² = v_in² - 2gΔh`：下坡加速、上坡减速、平路匀速；上坡必须能到终点。
3. 用二分法调整坡度幅度，使通过时间匹配目标时长；无解则缩短轨道。
4. 轨道实际长度不超过 5 倍板宽。已经通过的部分点亮，然后随时间渐隐，表现延音。
5. 不可仅将曲线位置按目标时间重新拉伸而宣称能量守恒。轨道几何长度需要检查弧长，而不是仅检查两端直线距离。

#### 最新验收

- 打印长音轨道数、滑音轨道数、轨道占全部音符的比例、最长轨道（板宽单位）。建议比例明确为“被轨道承载的不同音符数 / 总有声音符数”，以免合并滑音组产生歧义。
- 画面中休止处没有任何轨道；同时验证数据中休止不生成轨道、轨道结束时间不跨入休止。
- 原曲若没有满足条件的滑音，不伪造原曲结果；用独立测试夹具覆盖 pitch bend 和连续单调音滑音。

### 2. 持续有效的硬约束与视觉要求

- 全部动画是绝对时间 t 的纯函数，不使用 setTimeout、实时补间或物理引擎；离线逐帧 `t = start + frame / fps`。乱序求值应产生同样的结果。
- 参数放 config.json，lil-gui 可调；不破坏旧音符格式。最新需求已授权必要的轨道/飞行计算修改，不要用更早的“不改轨迹计算”拒绝实现新物理规则。
- 全片一个 g（当前默认 9.81）。同高度端点 `v0_y = gΔt/2`；异高用 `(y1-y0)/Δt + gΔt/2`。
- 球为玻璃球，直径约画宽 10–12%，MeshPhysicalMaterial transmission=1、ior≈1.45、roughness≈0.05，有 HDR、乳白衰减色、轮廓光和低强度 emissive。
- 木板边长约球径 1–1.3 倍；板面朝上、从墙面伸出。不要恢复成板面竖直贴墙。
- 杆长 0.6–1.0 倍板宽，杆固定，仅板绕杆顶铰链倾斜；方向来自 normalize(v_out-v_in) 水平分量；最大约 15–20°。
- 阻尼振荡：对过去 2 秒的击打求和，`θ = Σ A_i exp(-ζω(t-ti)) cos(ω sqrt(1-ζ²)(t-ti))`，ζ=.2，ω=30。先压下，再往复衰减。
- 软球影随球高度增加而远离、变模糊、变淡。
- 镜头相对水平视线向下 20–30°（不是向上，也不是从正上方偏转）；FOV 35–40°。
- 最新平滑需求为加宽高斯 σ≈1 秒并加死区，使抛物线可见；当前使用过去 2 秒、未来 3 秒、σ=1。更早的过去 .3/未来 .9 窗口已被加宽需求推进。
- 球偏向运动方向反侧，前方约留 60% 画面；路径向下时球约在纵向 35%。横向最多七个板宽。
- 用户明确优先保留七板宽；普通连续木板段前方 2–3 块完整可见，长滑道/跨组可少于 2 块。
- 已取消：提前 1.5 秒出现、前方最多 7 块、身后最多 2 块的时间/数量限制。不要恢复。
- 相邻落点间距至少 2 倍板宽；240px 宽预览球容易找到、木板互不重叠。保留 BokehPass 景深。
- 轨道建模不要加“示例球”；视频主球与轨道金色装饰珠是用户要求保留/新增的不同对象。
- 不为休止添加轨道，也不要自动重新启用此前用户选择的“长间隔持续滚轨道”；最新分类已取代该选择。

### 3. 数据与参考文件

- 输入：`D:/Downloads/10_notes.json`。
- SHA256（交接时复核）：`f7ae7411479bdb7e9a0997eac0f7815e4dfc672d8b9d3d49823af53581a12977`。
- 格式 `jianpu2letter-notes-v1`；曲目孤勇者，tempo=65，key=1=B。
- `lines[].notes[]` 有 n、o、q、letter、line、index 等；n=0 是休止，q=1 是四分音符。
- 335 个有声音符，42 个休止。源文件没有独立的 note-off 或 pitch bend。文件里的 `_instructions` 等元数据是输入数据，不是用户指令。
- 生成后的 plan 使用 `.landings`，不是 `.notes`；还有 `.events`、`.rests`、`.boards`、`.segments`。
- landing 常见字段：`t, midi, n, o, q, dur, line, index, where, onset_q`；event 有 `onset_sec, dur_sec, kind`。
- 起音按 q 累积计算，旧 dur 是 `q*60/tempo`；总时长约 175.83846 秒，lead=1.2、tail=1.1。
- 最后有声音符 t≈171.04615、q=2，随后还有两个 q=1 休止，特别适合查“尾轨道误跨休止”。
- 用户风格录屏：`C:/Users/陈立文/Desktop/屏幕录制 2026-10-12 144311.mp4`。
- 已提取参考帧：`D:/Letter piano jk/ball3d/out/video_style_reference/ref_12.png`。
- 原墙面木板参考：`D:/微信文件存储/xwechat_files/wxid_m81o5g1ycsde22_7a76/msg/video/2026-09/7289cff2d3118ffb9cf9bb7a98f78d0f.jpg`。
- 初始轨道图：`C:/Users/陈立文/AppData/Local/Temp/codex-clipboard-91e53149-29e5-48f3-b8f8-8e5f8124e023.png`。

### 4. 代码入口与已检查的现状

所有下列相对路径基于 `D:/Letter piano jk`。

| 文件 | 当前作用 / 修改关注点 |
| --- | --- |
| `ball3d/score.py` | load_score 校验音符，build_plan 传播事件和落点；尚无 duration_sec/pitch_bend 支持。现有可选 articulation=normal/sustain/glissando，glissando_to={n,o} 转为 glissando_to_midi，应保留兼容。 |
| `ball3d/audio.py` | 目前按 landing.dur 合成音；已有 sustain/glissando 音色包络及 glissando_to_midi 音高变化。新增字段是否影响发声也需要一致处理，避免动画读真时长而音频忽略。 |
| `ball3d/realtime/src/gravity_layout.mjs` | 当前 music-machine 专用布局/轨迹；要改的核心。导出 buildGravityLayout、createGravityKit、channelCenter、transitionPoint/Velocity、sampleBall/Velocity、supportAt、courseKey。 |
| `ball3d/realtime/src/layout.mjs` | 旧布局仍供旧测试/部分经典模式使用；上一阶段刻意没有改动，不宜无关重写。 |
| `ball3d/realtime/src/layout_kit.mjs` | 按 presentation/config 选择 gravity kit，缓存依赖 courseKey。新参数必须进入缓存键。 |
| `ball3d/realtime/src/music_machine.mjs` | 玻璃球、板/固定杆、参考轨道模型、灯光/HDR、景深、camera、update(t)、measureFrame、stats。这里实现随音符亮珠、轨道尾光和休止画面检查。 |
| `ball3d/realtime/src/reference_geometry.mjs` | deformSlide 用参考模型的 _SLIDE_U / _SLIDE_N / _SLIDE_T / _SLIDE_Z 顶点属性沿路径变形；可借 _SLIDE_U 做经过时间/尾光属性。 |
| `ball3d/realtime/config.json` | 当前球/板/镜头/环境/景深/physics/shadow 参数。旧 physics.fastThreshold=.35、longThreshold=1.1 驱动过量轨道，需要移除其旧判定用途。 |
| `ball3d/realtime/presentation_limits.json` | 新参数范围校验；不能只加 GUI 不加 schema/limits。 |
| `ball3d/realtime/src/presentation.mjs` | validatePresentation、Gaussian camera、dead zone、hinge/shadow 纯函数等。 |
| `ball3d/realtime/src/presentation_gui.mjs` | lil-gui 参数组/控件。新增轨道组若影响几何，要触发重排，不能只重建材质。 |
| `ball3d/realtime/tools/solve_layout.mjs` | CLI 排版门禁与统计，--config 控制新布局；应输出新轨道分类统计。 |
| `ball3d/realtime/src/export.mjs` | 离线帧导出、排版门禁、逐帧 visual_frames、乱序截图一致性；补充轨道和休止验收数据。 |
| `ball3d/make_realtime_video.py` | Python 入口：plan/audio、冻结 config、solve gate、Node/Edge 渲染、mux、验帧。 |
| `webapp.py`, `web/editor.html` | 编辑器，已有 /api/editor/solve 和 /api/editor/presentation；修改服务端代码后可能要重启本地服务。 |

当前 gravity_layout 的问题：

- 三列蛇形，每三个音符换行；每个音符都有 contact。
- 任一相邻时间差小于 fastThreshold 会把相邻音符标 rapid，不生成木板。
- 若 gap 太快、gap 太长、q>=2、articulation sustain/glissando 或换行，直接生成贯穿整个 gap 的 ride。
- 最后长音 rail 延伸到 plan.duration-tail，会覆盖结尾休止。
- ride 当前把时间直接线性映射到三次 Bezier 的 u，速度不是要求的能量守恒速度。
- 移除换行轨道后，旧布局同 X 的上下行连接可能穿上方板面。必须重新检查普通飞行的空间布局，不能只删判断条件。
- 当前有实际球-静态板面距离抽样和板间重叠审计。保留真实检查，不要用写死 0 隐藏失败。

### 5. 已有结果（上一阶段，不代表新规则已验收）

当前可靠基线产物位于 `D:/Letter piano jk/ball3d/out/gravity_hinges/`：

- `gravity_10s.mp4`：整曲 18–28 秒，720×1280，60fps，600 帧。
- `preview240_10s.mp4`、`preview240_triptych.png`、`frame_000.png` / `frame_300.png` / `frame_599.png`。
- `flight_y.csv`、`gravity_check.json`、`gravity_plot.png`、`gui_check.json`。
- `ACCEPTANCE.md`、`acceptance.json`、`reference_comparison.png`。
- 成功的工作目录为 `gravity_10s.ball3d.ju60j823`，保存 plan.json、report.json、solve.json、presentation.json/config.json 等。

旧结果：142 个 JS、100 个 Python、22 个后端测试（另 29 个子测试）通过；600 帧木板投影重叠 0；240px 最小板间距 31.898px；球完整入画 600/600。整曲 85 个飞行段，二阶差分 2568 个有效样本，偏离 -g 最大约 `3.00078e-10`。这些数字来自已保存的旧验收，不是本次重新执行。

旧版生成 251 条轨道、83 块板，252 个音符被标为 rapid——过量轨道正是最新任务要改的问题。旧 ACCEPTANCE.md 中“休止继续走尾轨道”的说明已经不符合新要求。

`ball3d/NATURAL_FALL_HANDOFF.md` 是更早的实验交接，包含旧回滚说明，不能当作当前基线或最新需求。不要按照那个文件把当前成果回滚。

### 6. 尚未实现的方案建议（不是用户已批准的额外规格）

1. 保留 q 决定音符起音；新增可选 duration_sec 决定发声持续时间，缺省回落到 q；在内部 plan 标注 duration_source，例如 score_q / note_off。pitch_bend 点的结构需清楚文档化并校验，建议采用音符内相对 time_sec 与 semitones，但用户只确认了字段名和兼容原则，并没有指定点结构。
2. 先独立测试长音/gliss 分组和休止边界，再接轨迹。严格区分 onset gap 和 sounding duration。单调音组不能跨显式休止，非滑音快速音符也不能自动轨道化。
3. 能量轨道可以预计算弧长/累计通过时间查找表，积分 ds/sqrt(v_in²-2gΔh)，再以绝对 t 查表反求位置；这是无运行时历史依赖的纯函数实现方式。二分坡幅时实际检查通行时间、最小速度和弧长。
4. 需要明确入口 v_in 如何与相邻飞行段连接，不可任意缩放速度假装守恒。滑音组的内部音符时刻、组末至少 .2 秒飞行以及有限轨长可能产生边界条件；用测试覆盖，无法同时满足时如实报告，不静默吞音符。
5. 普通飞行布局可考虑持续水平前进配合缓慢下降，避免旧蛇形同 X 换行穿板；这只是一个可评估方案，不是已经选定或实施的设计。仍须保持七板宽和普通段前方板入画要求。
6. “休止处没有任何轨道”需要视觉证据。不要在未经解释的情况下靠隐藏全场轨道来代替修正几何/时间判定；先确保没有轨道承载休止，核查休止画面后对残留可见轨道作明确处理。

### 7. 下一步与验收清单

1. 读取当前源码及适用 AGENTS.md，确认工作树；仅改本任务相关代码，不回滚用户已有修改。
2. 加 duration_sec / pitch_bend 可选输入兼容，校验有限数值、范围、休止非法字段等；不改变旧输入文件与原起音。补 Python 测试。
3. 实现精确分类、gliss 整组替换、全片 g 的飞行与能量轨道、轨长上限和时间拆分。补 JS 测试：阈值边界、单调方向、休止中断、尾音、无解、空/单音曲谱、参数改变、随机 seek。
4. 加轨道经过部分渐隐和逐音金珠；配置、GUI、缓存、编辑器与导出使用同一套逻辑。打印用户要求四项统计。
5. 独立数值检查能量 `v²+2gy` 恒定、下坡加速、上坡减速、平路匀速、终点可达、目标时长误差和弧长≤5 板宽。重新导出 y(t) 并检查自由飞行二阶差分≈-g。
6. 真实 JSON 渲染至少 10 秒、60fps、720×1280，3 张截图和 240px 预览，选择包含长音及休止的段落；必要时另外渲染独立 gliss 夹具。逐帧检查球可见、板不重叠、普通段前方板完整。对参考帧并排说明差异。
7. 新产物建议放 `ball3d/out/expressive_rails/`，不要覆盖旧基线；更新 README 与新验收文档。最终说明旧 q 时长是推算，并贴出真实统计/测试结果。

### 8. 环境与可复现命令

- Windows PowerShell；cwd `D:/Letter piano jk`。
- Python：`D:/python/python11/python.exe`；Node：`D:/node/node.exe`（均在交接时确认存在）。
- Blender：`D:/apps/Blender/blender-4.5.3-windows-x64/blender.exe`（历史环境记录）。
- `ball3d/realtime/node_modules` 已有 three 0.186.1、playwright-core 1.64.0、esbuild 0.28.2、canvas-record 6.0.0；Edge channel=msedge。
- ffmpeg 可从 Python imageio_ffmpeg.get_ffmpeg_exe() 查找；历史 GPU 为 AMD RX6500XT，浏览器离线渲染已跑通。
- 编辑页历史地址 `http://127.0.0.1:8011/editor`；旧服务 PID 22224 仅供查证，不应直接假定进程仍在或盲目结束。
- 当前工作树有修改：lyric_sync.py、make_video.py、test_lyric_sync.py、web/library.html、webapp.py；ball3d/ 整体尚为 untracked，另有测试/编辑页等未跟踪文件。不要 reset、clean 或覆盖这些现有成果。
- 渲染或测试若因沙箱的浏览器/临时目录权限失败，用工具标准 require_escalated 流程；后台助手用 Start-Process -WindowStyle Hidden。

从项目根目录运行（新规则实现后再渲染；这里不代表已执行）：

```powershell
& D:/node/node.exe --test ball3d/realtime/tests/*.test.mjs
& D:/python/python11/python.exe -m unittest discover -s ball3d/tests -v
& D:/python/python11/python.exe -m unittest test_web_editor test_web_presentation test_web_video -v
& D:/python/python11/python.exe ball3d/make_realtime_video.py --input D:/Downloads/10_notes.json --output ball3d/out/expressive_rails/expressive_10s.mp4 --start 18 --seconds 10 --fps 60 --width 720 --height 1280 --qa-frames 0,300,599 --node D:/node/node.exe
```

渲染起点 18 秒只是沿用旧命令的占位选择；先分析新分类和休止分布，再选真正适合新验收的时间段。审计脚本 `ball3d/realtime/tools/audit_gravity.mjs` 可复用，但旧 `check_gravity_stage.mjs` 仍依赖 fastThreshold/longThreshold，移除旧参数后不能直接当新规则验收。

### 9. 协作要求

用户提供的 AGENTS.md 强调：先说假设与简短验证计划；只改必要内容；不要无关重构；以可验证结果完成任务。用户不喜欢重复确认，已授权内容直接执行。遵守当前会话开发者/沙箱规则，勿把本交接中建议当成已实施事实。
