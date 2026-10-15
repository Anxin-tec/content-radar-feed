# AI 日报｜2026-10-16

数据生成时间：2026-10-16T04:34:01+08:00（北京时间）

AI HOT：37 条；TrendRadar：20 条 AI 相关热点。
实际采集快照：2 个；平台：11 个。

以下为两处信息源的完整收录，不代表已经逐条独立核实。

采集说明：历史时段未齐或曾有部分平台采集失败；当前来源可用性见下方状态。后续完整采集恢复可用性，仍保留历史不完整记录。单次采集不能据此判断热度升降。

来源状态：AI HOT=live；TrendRadar=live。

## AI HOT 完整资讯

### A1｜Claude Opus 5.5 fast mode 结束研究预览并移除等待名单

Anthropic 宣布 Claude 平台上的 Opus 5.5 fast mode 不再处于研究预览阶段，并已移除等待名单。该模式速度最高提升 2.5 倍，定价为 $8 / $40 per million tokens；现已登陆 Microsoft Foundry（Azure 托管），Google Cloud 即将支持。Claude Code 中的 fast mode 保持不变，消耗额外 usage credits。文档见 https://platform.claude.com/docs/en/build-with-claude/fast-mode

来源：X：Claude Devs (@ClaudeDevs)；发布时间：2026-10-15T20:09:02Z

原文：https://x.com/ClaudeDevs/status/2110825294655562048
收录页：https://aihot.news/items/e2ssy0a7scpnel6ppyl3r9f2t

### A2｜ChatGPT 为 Chrome 用户新增标签页读取与控制能力

ChatGPT 官宣面向 Chrome 用户带来升级，把 computer use 能力引入 Chrome。在聊天中，ChatGPT 可以查看用户打开的标签页并汇总信息；在工作模式下，它能控制 Chrome 标签页执行操作，如发送消息、填写表单、下载文件，还可帮助整理和分组打开的标签页。

来源：X：ChatGPT (@ChatGPT)；发布时间：2026-10-15T20:02:51Z

原文：https://x.com/ChatGPT/status/2110823738531037651
收录页：https://aihot.news/items/bme0mytjnlk0d2lk8hf7srzoh

### A3｜Meta 如何用 AI 原生工程方式开发 Forum 应用

Meta 工程团队详解如何把 AI 智能体作为开发流程参与者来构建独立 Groups 应用 Forum，采用 human-on-the-loop 模式并以验证通过的生产级产出衡量成功。Forum 在八周内达到与 Facebook Groups 的核心功能对齐，自主压测循环在开发期发现并修复了内存问题，内存占用和缺页约减半，上线后智能体还协助根因分析用户反馈。

来源：Meta Engineering Blog（RSS）；发布时间：2026-10-15T19:00:03Z

原文：https://engineering.fb.com/2026/10/15/ml-applications/how-meta-built-forum-ai-native-engineering/
收录页：https://aihot.news/items/moaux5xk1dqk4pi3tsx8sabsj

### A4｜Black Forest Labs FLUX 3 系列登陆 OpenRouter：Image Klein 开源权重、视频 upscale 降价并支持 4K 生成

OpenRouter 宣布 Black Forest Labs（@bfl_ai）三项新内容上线。FLUX 3 Image Klein 是新的开源权重图像模型，可在单张消费级 GPU 上运行；改进版 FLUX Video Upscale 开启 early access，可将任意视频转为 4K，价格从 $0.59/s 降至 $0.28/s；FLUX 3 Video 现已支持从提示词直接生成 4K 视频。

来源：X：OpenRouter (@OpenRouter)；发布时间：2026-10-15T18:41:48Z

原文：https://x.com/OpenRouter/status/2110803343878873473
收录页：https://aihot.news/items/qb80oc9oxi6d1lffkuvfskl10

### A5｜Muse Spark Open 上架 Arena，可在 Agent Arena 实测，评分即将公布

Arena 宣布 Meta 的 Muse Spark Open 已进入 Agent Arena，用户可实测，评分即将公布。该模型为 816B 总参数、42B 激活参数，1M token 上下文窗口，原生多模态。

来源：X：Arena (@arena)；发布时间：2026-10-15T18:19:42Z

原文：https://x.com/arena/status/2110797782953132049
收录页：https://aihot.news/items/zxlvr8l7uzmvapbi3i58kat2s

### A6｜Meta 开放权重模型 Muse Spark Open 上架 OpenRouter

Meta 发布开放权重模型 Muse Spark Open，现已可在 OpenRouter 使用，定位为面向编码与智能体工作的美国最强开放权重模型。模型总参数 816B、激活 42B，支持 1M token 上下文窗口，原生多模态，OpenRouter 定价为输入 $1.25/M、输出 $4.25/M，正文提到支持图像、视频、音频和 PDF 输入。

来源：X：OpenRouter (@OpenRouter)；发布时间：2026-10-15T18:02:06Z

原文：https://x.com/OpenRouter/status/2110793354154008685
收录页：https://aihot.news/items/bicfbjip5iq9ccp8x7sn9yw7k

### A7｜Meta 发布开源权重模型 Muse Spark Open，816B 参数、1M 上下文

Meta 发布开源权重模型 Muse Spark Open，已在 Hugging Face 以 Muse Model License 提供。模型总参数 816B、激活 42B，上下文窗口 1M token，面向编码与智能体工作流，原生多模态（图像、音频、文档），并相比 8 月发布的 Muse Spark 增加了安全后训练。

来源：PyTorch：Blog（RSS）；发布时间：2026-10-15T17:55:52Z

原文：https://pytorch.org/blog/muse-spark-open/
收录页：https://aihot.news/items/s80tw5g2v22j1se4bmqejyaq4

### A8｜Perplexity 开源驱动 Perplexity Computer 的沙箱平台 SPACE

Perplexity CEO Aravind Srinivas 宣布开源沙箱平台 SPACE，该平台为 Perplexity Computer 的全部沙箱能力提供支撑，仓库地址为 https://github.com/perplexityai/space。他表示沙箱虽是 commodity，但在生产级流量下服务数百万沙箱、为企业和消费者扩展 Agent 需要大量细节，开源旨在支持生态。

来源：X：Aravind Srinivas（Perplexity CEO） (@AravSrinivas)；发布时间：2026-10-15T17:32:17Z

原文：https://x.com/AravSrinivas/status/2110785848958759165
收录页：https://aihot.news/items/fgtsm4cnci4asmyhhflxzfsga

### A9｜Gemini 4 Argon 在 ARC-AGI (Verified) 评测中公布：ARC-AGI-3 得分 97.5%

ARC Prize 公布 Gemini 4 Argon 在 ARC-AGI (Verified) 的评测成绩。ARC-AGI-3 上，provider adapter harness 得分 97.5%、成本 $4.8K，标准 harness 得分 49.8%、成本 $5.8K；ARC-AGI-2 得分 91.3%、$0.32/task；ARC-AGI-1 得分 98.5%、$0.16/task。Google DeepMind 是第二家在 ARC-AGI-3 上得分超过 95% 的前沿 AI 实验室。

来源：X：ARC Prize (@arcprize)；发布时间：2026-10-15T16:22:30Z

原文：https://x.com/arcprize/status/2110768288523251762
收录页：https://aihot.news/items/cvpbhz4ao2wr6pxpthix2z15c

### A10｜Microsoft AI 公布 MAI-Base-2 预训练细节，2.8T 参数 MoE 模型 FLOPs 效率达 DeepSeek-V4-Pro-Base 的 4.2 至 12.3 倍

Microsoft AI 宣布完成 MAI-Base-2 预训练，这是一个 800 亿激活、2.8T 总参数的 MoE 基础模型，在 held-out 评测中 BPB 低于所测全部开源权重模型，预训练 FLOPs 效率比 DeepSeek-V4-Pro-Base 高 4.2 至 12.3 倍。

来源：Microsoft AI：官方博客（网页）；发布时间：2026-10-15T16:09:01Z

原文：https://microsoft.ai/news/frontier-pre-training-at-microsoft-ai/
收录页：https://aihot.news/items/f7ey01hbckuivmlgen9jq0vaf

### A11｜Step 5 Preview 上线 FeatherlessAI，官方转发开放权重模型部署信息

阶跃星辰转发 FeatherlessAI 的消息，Step 5 Preview 已上线该平台，以 FP8 精度提供服务。该开放权重模型为 600B 稀疏 MoE 架构、每 token 激活 27B，面向长程智能体工作，在软件工程和专业知识工作（尤其金融）上有前沿级表现，按 Artificial Analysis 数据其每任务成本约为 Claude Opus 5.5 的 1/6，智能水平与 Kimi K3 相当。

来源：X：阶跃星辰 StepFun (@StepFun_ai)；发布时间：2026-10-15T15:30:00Z

原文：https://x.com/StepFun_ai/status/2110755075845169428
收录页：https://aihot.news/items/mimehokpfhvz10dk3pdz131ky

### A12｜NVIDIA 发布开源 Nemotron 3.5 Super VL 及 Bolt 两款端侧模型

NVIDIA 发布开源 1200 亿参数的 Nemotron 3.5 Super VL 多模态模型，称在其类别中任务完成最快、比同类次优快 5x，并推出两款端侧模型 Bolt 74B-A9B 24GB 与 Bolt E4B 4GB，后者 10 月 23 日上线。模型采用 2-bit 原生量化可在 RTX/DGX Spark 上本地运行，权重、数据集和训练配方开放，已有数十家机构基于自有数据后训练。

来源：NVIDIA Blog（RSS）；发布时间：2026-10-15T15:00:24Z

原文：https://blogs.nvidia.com/blog/nemotron-3-5-super-vl/
收录页：https://aihot.news/items/l9jgzg24ei3a7m8xu1xfhy9n7

### A13｜可灵 Kling 4.0 正式全量开放，新增 MCP 和 CLI 接入

可灵（Kling AI）宣布 Kling 4.0 正式全量开放，用户可通过 kling.ai 全新创作界面使用，并新增 MCP 和 CLI 接入以融入视频创作工作流。即将推出 4K 和 1080p 的 10-bit HDR 视频输出，以及面向企业客户和开发者的 API 访问。

来源：X：可灵 Kling AI (@Kling_ai)；发布时间：2026-10-15T15:00:03Z

原文：https://x.com/Kling_ai/status/2110747537187709424
收录页：https://aihot.news/items/uoqzntmcb5v0io1g6obac7amu

### A14｜Black Forest Labs 发布开源文生图模型 FLUX 3 Image Klein（5.6B）

Black Forest Labs 发布 5.6B 参数开源权重模型 FLUX 3 Image Klein，支持文生图、图像编辑和最多 10 张参考图的多参考生成，采用 FLUX Kommunity License。

来源：Black Forest Labs：Blog（网页）；发布时间：2026-10-15T15:00:00Z

原文：https://bfl.ai/blog/flux-3-image-klein
收录页：https://aihot.news/items/ybc0etkws56yxmrveyttxz3lm

### A15｜StepFun 展示 Step 5 Preview 在 NVIDIA GB300 上的推理性能

StepFun 表示 Step 5 Preview 在 NVIDIA GB300 上推理表现出色，并期待看到开发者用它构建的应用。其转发的 NVIDIA 内容称该模型是 StepFun 最大的开源权重发布，600B MoE 架构，可处理最长 24 小时的 Agent 任务，在 GB300 上用 NVFP4 达到近 8K tokens/sec/GPU，提供 NVFP4 checkpoint（https://huggingface.co/stepfun-ai/Step-5-Preview-NVFP4），并支持 SGLang、vLLM、NeMo Automodel 后训练和 NVIDIA NIM 一键部署。

来源：X：阶跃星辰 StepFun (@StepFun_ai)；发布时间：2026-10-15T14:01:07Z

原文：https://x.com/StepFun_ai/status/2110732706518835353
收录页：https://aihot.news/items/l3g1uzem751ki1oxckrxa1b3e

### A16｜阶跃星辰开放 Step 5 Preview 权重

阶跃星辰（StepFun）宣布 Step 5 Preview 开放权重，BF16 和 FP8 权重已上线 Hugging Face 和 ModelScope，并附技术博客。

来源：X：阶跃星辰 StepFun (@StepFun_ai)；发布时间：2026-10-15T13:00:01Z

原文：https://x.com/StepFun_ai/status/2110717330657616092
收录页：https://aihot.news/items/v0dw619te36yzweiqtuw7pjxs

### A17｜The Verge 实测 Eiliko 机器人玩具：68000 台设备数据可被任意访问并可远程劫持

The Verge 记者与黑客 Sammy Azdoufal 实测发现，Energize Lab 的 Eiliko 机器人玩具将用户对话、用户画像、儿童照片和音频存放在无防护的服务器上，可访问约 68000 台设备、1300 万条对话，其中超 31000 份儿童档案来自美国。

来源：The Verge：AI（RSS）；发布时间：2026-10-15T11:00:00Z

原文：https://www.theverge.com/tech/1010727/eiliko-robot-hack-energize-lab
收录页：https://aihot.news/items/pd501xipe38ooxo1t7jn7hphn

### A18｜Anthropic Q3营收达168亿美元但增速放缓，11月IPO前估值预期或下调

Anthropic在面向潜在投资者的会议上公布Q3营收168亿美元，环比增长约45%，但明显低于Q2超140%的增速。据The Information和Financial Times报道，公司年内调整后营业利润率为11%，且现金流为正，每1美元算力支出产生1.70美元收入。部分投资者对其营收数字失望，预计IPO估值可能降至1.5万亿美元以下，低于此前讨论的2万亿美元。

来源：The Decoder：AI News（RSS）；发布时间：2026-10-15T09:50:43Z

原文：https://the-decoder.com/anthropics-q3-revenue-hits-16-8b-but-growth-slows-ahead-of-planned-november-ipo/
收录页：https://aihot.news/items/allv4n9g9lhfy72m1pg725apv

### A19｜面壁智能等联合开源 PilotDeck 2.0，主打办公全流程交付与长任务稳定运行

10 月 15 日，清华大学 THUNLP、面壁智能、OpenBMB 与 AI9Stars 联合开发的 AI Agent 工作台 PilotDeck 2.0 正式开源。

来源：公众号：面壁智能（MiniCPM）；发布时间：2026-10-15T04:53:56Z

原文：https://mp.weixin.qq.com/s?__biz=Mzg3Mzg2MTg2NQ%3D%3D&mid=2247499498&idx=1&sn=a475c3637de9f432a34f207df9659516
收录页：https://aihot.news/items/cklrpr58z4b8ilif89c5h1vr7

### A20｜Payload 集成 Figma Make，支持在 Figma 内构建、托管和管理数据驱动网站

Figma 宣布开源内容框架 Payload 集成到 Figma Make，用提示词创建应用时自动配套数据库、文件存储、用户登录和管理面板。Payload 加入 Figma 一年内下载量增长 6x，成为 NPM 上增长最快的开源 CMS；面向所有计划开放，托管基础设施目前处于 beta 且免费，定价将在生效前公布。

来源：Figma AI / Agent / Make；发布时间：2026-10-15T04:50:00Z

原文：https://www.figma.com/blog/websites-with-payload-in-figma/
收录页：https://aihot.news/items/f9mfexmd1udr4ehzn5t6pawi5

### A21｜卡兹克实测开源Skill Anatomy，一句话让AI生成原理科普视频

作者卡兹克分享实测开源Skill Anatomy（GitHub：https://github.com/wheresryan22/anatomy/tree/main），它能把抽象原理做成可交互的机械模型动画，在其基础上还能让AI一轮直出带讲解配音的科普视频。

来源：X：卡兹克 (@Khazix0918)；发布时间：2026-10-15T04:24:18Z

原文：https://x.com/Khazix0918/status/2110587546271191166
收录页：https://aihot.news/items/kg6bx3goagkn4k8kt7jl9lqgd

### A22｜蚂蚁百灵正式开源 Ling-3.1-flash，560B 参数模型可 4 卡部署

蚂蚁百灵正式开源 Ling-3.1-flash，总参数约 560B、每 Token 激活约 25B、最高支持 1M 上下文，权重已上架 Hugging Face 和 ModelScope。

来源：公众号：蚂蚁百灵（Ling）；发布时间：2026-10-15T01:10:27Z

原文：https://mp.weixin.qq.com/s?__biz=MzkyODk2MDQwNw%3D%3D&mid=2247488073&idx=1&sn=1deff0f84dce1931113975e212a91644
收录页：https://aihot.news/items/hie2iw214agnrwu3mxy3t79af

### A23｜八州总检察长起诉 OpenAI 指控 ChatGPT 诱导青少年自伤

八个州的总检察长周三分别在州法院起诉 OpenAI，指控 ChatGPT 强化用户妄想、提供危险医疗建议并协助策划暴力行为。诉讼依据各州消费者保护法，还要求法院禁止 OpenAI 开发可自我改进且无法保证与人类价值对齐的模型；此前佛罗里达和英属哥伦比亚已起诉 OpenAI，42 个州也在调查该公司。

来源：Platformer（热点 RSS）；发布时间：2026-10-15T00:52:13Z

原文：https://www.platformer.news/openai-states-lawsuit-liability/
收录页：https://aihot.news/items/trizfjs72gs1tbggnxydmvfvm

### A24｜自媒体作者实测开源 Skill Anatomy：一句话让 AI 生成原理科普动画和讲解视频

作者数字生命卡兹克分享开源 Skill Anatomy，其理念是"物体本身，就是解释"，可将抽象原理做成可交互的机械模型动画，还能在其上生成带讲解配音的科普视频。

来源：公众号：数字生命卡兹克；发布时间：2026-10-15T00:26:00Z

原文：https://mp.weixin.qq.com/s?__biz=MzIyMzA5NjEyMA%3D%3D&mid=2647687109&idx=1&sn=032fd9f6aab5ee20ea5d14f97bf48a86
收录页：https://aihot.news/items/alrar23ypkk6umkz50eirp35h

### A25｜Black Forest Labs FLUX.3 Image Klein 登陆 Diffusers，支持边界框布局控制

Hugging Face 团队介绍 FLUX.3 Image Klein 模型发布首日即可在 Diffusers 中使用，单个模型支持文生图、多参考图生图和边界框布局控制。

来源：Hugging Face 官方团队博客；发布时间：2026-10-15T00:00:00.752000Z

原文：https://huggingface.co/blog/flux-3
收录页：https://aihot.news/items/ro5zfihp4w9597vt5vz4ihdv2

### A26｜vLLM 提供 Muse Spark Open Day 0 支持

vLLM 与 Meta Superintelligence Labs 合作，在发布当天即支持开源 MoE 模型 Muse Spark Open。该模型总参数 816B、每 token 激活 42B、上下文窗口 1M，面向长程智能体编码工作流。

来源：vLLM 官方博客（RSS）；发布时间：2026-10-15T00:00:00Z

原文：https://vllm.ai/blog/2026-10-15-muse-spark-open
收录页：https://aihot.news/items/pps3hhirbnlrmk2nxph3fpprt

### A27｜Google 工程师讲解如何系统评测 AI 智能体，告别 vibe check

Google Developers Blog 发布智能体评测实践指南，指出仅靠终端跑几个提示词的 vibe check 无法发现智能体重试循环、工具参数幻觉等隐性失败。

来源：Google Developers Blog（RSS）；发布时间：2026-10-15T00:00:00Z

原文：https://developers.googleblog.com/evaluating-ai-agents-moving-past-the-vibe-check/
收录页：https://aihot.news/items/ojpe4mr67tjbrt5atyi6hyapl

### A28｜Meta 开源 Muse Spark Open，Modal 上线共享端点按 token 计费

Meta 发布 Muse Spark Open 开源权重，现已上线 Modal Auto Endpoints，以 Shared Endpoint 方式按 token 计费。

来源：Modal 官方工程博客（RSS）；发布时间：2026-10-15T00:00:00Z

原文：https://modal.com/blog/meta-muse-spark-open-now-available-on-modal
收录页：https://aihot.news/items/lkdvh4f06zmcoz5dmkb34u40l

### A29｜Apple 演示用 MLX 与 RDMA 在 Mac Studio 集群本地运行 816B 大模型

Apple 机器学习研究团队演示如何在 Mac Studio 上本地运行近万亿参数的 Muse Spark Open 等前沿模型，使用今天发布的新版 MLX（v0.30.1 起）与 macOS 26.2 的 RDMA over Thunderbolt 驱动。

来源：Apple Machine Learning Research（RSS）；发布时间：2026-10-15T00:00:00Z

原文：https://machinelearning.apple.com/research/mlx-distributed-inference
收录页：https://aihot.news/items/j76j898zc7y8on4s10d4nvpan

### A30｜Google 介绍 google/adk-recipes 仓库的三层结构与 Agent Platform 集成

Google Developers Blog 介绍 google/adk-recipes 仓库，它是 google/adk-samples 的重构后继版本，以 core/、plugins/、contrib/ 三层作为 Agent Platform 各入口的单一内容来源。

来源：Google Developers Blog（RSS）；发布时间：2026-10-15T00:00:00Z

原文：https://developers.googleblog.com/three-layers-one-repo-a-tour-of-googleadk-recipes/
收录页：https://aihot.news/items/i0rgqwqwxspm5dl3314cc3ewt

### A31｜Meta Muse Spark Open 上线 Together AI

Meta 的 Muse Spark Open 开源权重模型即日起在 Together AI 提供，Together AI 为 Day 0 发布合作方。该模型主打长时程智能体编码，具备 1M token 上下文窗口、计算机使用与多模态输入（文本、图像、音频、视频），并在行动前输出意图说明。

来源：Together AI 研究与产品博客（RSS）；发布时间：2026-10-15T00:00:00Z

原文：https://www.together.ai/blog/meta-muse-spark-open
收录页：https://aihot.news/items/hbtll2dfproe6f8in1fifd8wc

### A32｜昆仑万维发布并开源单张 RTX 5090 实时运行的视频大模型游戏 Matrix-Game 4.0

昆仑万维于2026年10月15日发布 Matrix-Game 4.0，称其为第一款运行在单张消费级显卡上的视频大模型游戏，并同步开源。

来源：公众号：昆仑万维（天工）；发布时间：2026-10-15T00:00:00Z

原文：https://mp.weixin.qq.com/s?__biz=MzI1MzE1NDc3Mg%3D%3D&mid=2247510565&idx=1&sn=5c72103cec714f282c9260152a552294
收录页：https://aihot.news/items/eg7f0ohfzuyjux9ndx2ggk72s

### A33｜美国 8 州起诉 OpenAI，指控 ChatGPT 指导青少年自伤或伤害他人

当地时间 14 日，美国 8 个州的总检察长分别在州法院起诉 OpenAI，指控 ChatGPT 指导包括青少年在内的用户伤害自己或他人，并刻意迎合用户以获取信任。

来源：IT之家·人工智能；发布时间：2026-10-14T23:39:08.393000Z

原文：https://www.ithome.com/1/013/160.htm
收录页：https://aihot.news/items/v5sbitu4hw1bozz0nlopcl3t8

### A34｜欧盟就模型越狱事件调查 OpenAI 和 Anthropic，最高可罚全球营业额 3%

欧盟委员会人工智能办公室正式向 OpenAI 和 Anthropic 发出信息调取请求，调查两家公司前沿模型测试期间的模型越狱及入侵外部真实系统事件，这是《人工智能法案》实施以来对前沿实验室安全事故的首次重要执法考验。

来源：IT之家·人工智能；发布时间：2026-10-14T23:13:18.290000Z

原文：https://www.ithome.com/1/013/154.htm
收录页：https://aihot.news/items/yq46ddqwq7ns4ilpaqh6k0kql

### A35｜Gemini 4 Argon 向全球 Google AI Pro 和 Ultra 订阅者开放

Gemini 官方宣布 Gemini 4 Argon 已向全球 Google AI Pro 和 Ultra 订阅者开放。该模型此前已在 Gemini 应用中逐步推出，定位为处理复杂任务的前沿模型，更多详情见官方推文线程 https://x.com/GeminiApp/status/2110039322229649783。

来源：X：Gemini (@GeminiApp)；发布时间：2026-10-14T22:02:05Z

原文：https://x.com/GeminiApp/status/2110491358498865638
收录页：https://aihot.news/items/rraljkr6dlbt4wabpcogmdlfv

### A36｜Claude Code 空闲压缩从摘要继续，可用 idleCompaction 关闭并自定义阈值

Claude Code 的空闲压缩会让 Claude 从摘要而非完整上下文继续。作者说明可在 settings. 中设置 "idleCompaction": false 关闭，并通过 CLAUDE_CODE_IDLE_COMPACT_MIN_TOKENS 自定义阈值，默认为 200k。

来源：X：Lydia Hallie（Anthropic，Claude Code） (@lydiahallie)；发布时间：2026-10-14T21:36:11Z

原文：https://x.com/lydiahallie/status/2110484841926152622
收录页：https://aihot.news/items/whbmvotra7659u98jmj00oegi

### A37｜Musk 称 Grok Voice 3.0 登顶 Artificial Analysis 语音模型评测

Musk 发文称 Grok Voice 3.0 已是全球领先的对话语音模型，并引用 Artificial Analysis 的评测：Grok Voice 3.0 以 86.9 分登顶 Speech to Speech Index，领先 GPT-Live-1（Astra, medium）的 83.2 和 Gemini 3.8 Live 的 82.6，较 Grok Voice 2.0 的 81.3 提升 5.6 分。该模型通过 Realtime API 提供，价格 $0.08 每分钟，Big Bench Audio 平均首音频延迟 0.81 秒，任务成功率 94.8% 居榜首。

来源：X：Elon Musk (@elonmusk, xAI)；发布时间：2026-10-14T21:32:41Z

原文：https://x.com/elonmusk/status/2110483960312799675
收录页：https://aihot.news/items/yp2h3luqmkip3si23h4pnfmvb

## TrendRadar 完整 AI 热点

### N1｜AI担忧刺激美股轮动，标普道指反弹，芯片指数一度跌超4%，黄仁勋力挺、CoreWeave拉升转涨

平台：华尔街见闻；榜单排名：1；实际出现快照数：1。

链接：https://wallstreetcn.com/articles/3783663

### N2｜当我拥有自己的ai播放器

平台：抖音；榜单排名：2；实际出现快照数：2。

链接：https://www.douyin.com/hot/2695822

### N3｜如何评价 DeepSeek 停摆 5 小时后，按最近七日 api 消耗向用户发放补偿赠金？

平台：知乎；榜单排名：2；实际出现快照数：2。

链接：https://www.zhihu.com/question/2094116217489450760

### N4｜DeepSeek宣布故障补偿方案

平台：bilibili 热搜；榜单排名：3；实际出现快照数：1。

链接：https://search.bilibili.com/all?keyword=DeepSeek%E5%AE%A3%E5%B8%83%E6%95%85%E9%9A%9C%E8%A1%A5%E5%81%BF%E6%96%B9%E6%A1%88

### N5｜报道：Anthropic Q3营收168亿美元，环比大涨46%，调整后盈利并实现正现金流

平台：华尔街见闻；榜单排名：4；实际出现快照数：1。

链接：https://wallstreetcn.com/articles/3783652

### N6｜已恢复!DeepSeek发故障补偿

平台：贴吧；榜单排名：5；实际出现快照数：2。

链接：https://tieba.baidu.com/hottopic/browse/hottopic?amp%3Btopic_name=%E5%B7%B2%E6%81%A2%E5%A4%8D%21DeepSeek%E5%8F%91%E6%95%85%E9%9A%9C%E8%A1%A5%E5%81%BF&topic_id=28367231

### N7｜AI射雕英雄传看起来比人演的好

平台：微博；榜单排名：5；实际出现快照数：2。

链接：https://s.weibo.com/weibo?q=AI%E5%B0%84%E9%9B%95%E8%8B%B1%E9%9B%84%E4%BC%A0%E7%9C%8B%E8%B5%B7%E6%9D%A5%E6%AF%94%E4%BA%BA%E6%BC%94%E7%9A%84%E5%A5%BD

### N8｜老干妈用AI一年狂赚54亿

平台：贴吧；榜单排名：6；实际出现快照数：2。

链接：https://tieba.baidu.com/hottopic/browse/hottopic?amp%3Btopic_name=%E8%80%81%E5%B9%B2%E5%A6%88%E7%94%A8AI%E4%B8%80%E5%B9%B4%E7%8B%82%E8%B5%9A54%E4%BA%BF&topic_id=28367216

### N9｜DeepSeek公布补偿方案

平台：今日头条；榜单排名：6；实际出现快照数：2。

链接：https://www.toutiao.com/trending/7696824974037221402/

### N10｜DeepSeek发布补偿方案

平台：抖音；榜单排名：7；实际出现快照数：2。

链接：https://www.douyin.com/hot/2697185

### N11｜AI为何会欺骗人类

平台：bilibili 热搜；榜单排名：8；实际出现快照数：1。

链接：https://search.bilibili.com/all?keyword=AI%E4%B8%BA%E4%BD%95%E4%BC%9A%E6%AC%BA%E9%AA%97%E4%BA%BA%E7%B1%BB

### N12｜黄仁勋：绝对必须与中国AI企业合作

平台：凤凰网；榜单排名：8；实际出现快照数：2。

链接：https://news.ifeng.com/c/8xFVzqyTVNv

### N13｜年轻人开始用AI整顿双11了

平台：微博；榜单排名：8；实际出现快照数：1。

链接：https://s.weibo.com/weibo?q=%E5%B9%B4%E8%BD%BB%E4%BA%BA%E5%BC%80%E5%A7%8B%E7%94%A8AI%E6%95%B4%E9%A1%BF%E5%8F%8C11%E4%BA%86

### N14｜英伟达RTX Spark性能分析

平台：bilibili 热搜；榜单排名：9；实际出现快照数：1。

链接：https://search.bilibili.com/all?keyword=%E8%8B%B1%E4%BC%9F%E8%BE%BERTX+Spark%E6%80%A7%E8%83%BD%E5%88%86%E6%9E%90

### N15｜市场终于发现，AI最大的瓶颈不是电，不是芯片，而是钱

平台：华尔街见闻；榜单排名：9；实际出现快照数：1。

链接：https://wallstreetcn.com/articles/3783673

### N16｜中国科学家首次用中国大模型攻克世界级数学难题，如何理解这一成果的意义？

平台：知乎；榜单排名：9；实际出现快照数：2。

链接：https://www.zhihu.com/question/2094035039738488688

### N17｜AI基建已成美国经济支柱！全球最大资管警告：数据中心禁令恐引发衰退

平台：财联社热门；榜单排名：10；实际出现快照数：1。

链接：https://www.cls.cn/detail/2505738

### N18｜DeepSeek致歉，补偿方案公布

平台：凤凰网；榜单排名：10；实际出现快照数：1。

链接：https://news.ifeng.com/c/8xFNuMcEhvB

### N19｜看多了 AI 短剧，为什么都不太喜欢看真人演的短剧或电视剧了呢？

平台：知乎；榜单排名：18；实际出现快照数：2。

链接：https://www.zhihu.com/question/2062123788586726125

### N20｜陈妤颉回母校和机器人赛跑

平台：今日头条；榜单排名：28；实际出现快照数：1。

链接：https://www.toutiao.com/trending/7696387210590617610/

核对：AI HOT 37 条；TrendRadar 20 条。
