# MoneyPrinterPlus 优化版

AI 短视频生成 + 混剪 + 多平台自动发布。

本仓库是优化版：补全了 **Stable Diffusion 生图成片**，成片后可直接导出发布素材，并一键发到抖音 / 快手 / 小红书 / 视频号 / B 站。

仓库地址：https://github.com/leohux/MoneyPrinterPlus

---

## 能做什么

| 功能 | 说明 |
|------|------|
| AI 一键成片 | 主题 → 大模型写文案 → 配音 → 配素材 → 合成短视频 |
| SD 生图成片 | 文案分段 → 自动写 SD prompt → WebUI 生图 → 按配音时长合成 |
| 批量混剪 | 本地素材文件夹 + 文案，批量产出不重复短视频 |
| 视频合并 | 多段素材直接拼接，可加字幕和背景音乐 |
| 多平台发布 | Selenium 自动上传（需浏览器已登录） |

支持的配音：Azure / 阿里云 / 腾讯云，以及本地 ChatTTS、GPT-SoVITS、CosyVoice。  
支持的大模型：OpenAI、Azure、Kimi、通义、DeepSeek、Ollama 等。

---

## 环境要求

- Windows 10+（也可用 Linux / macOS）
- Python 3.10 或 3.11
- [ffmpeg 6.0+](https://ffmpeg.org/)，并加入系统 PATH
- Windows 需安装 [VC++ 运行库](https://aka.ms/vs/17/release/vc_redist.x64.exe)
- 至少一个 LLM API Key（或本地 Ollama）
- 配音：云服务密钥，或本地 TTS 服务
- 生图：本机已启动 Automatic1111 WebUI（开启 API）

---

## 安装与启动

```bash
git clone https://github.com/leohux/MoneyPrinterPlus.git
cd MoneyPrinterPlus
pip install -r requirements.txt
```

把 `config/config.example.yml` 复制为 `config/config.yml`（首次启动也会自动复制），填入自己的 Key。

启动：

```bash
# Windows
start.bat

# 或
streamlit run gui.py
```

浏览器打开界面后，先在 **基本配置** 里选好大模型、配音、素材来源。

---

## 使用说明

### 1. AI 成片（素材库）

1. 素材来源选 `pexels` 或 `pixabay`，填 API Key  
2. 进入 **自动短视频生成器**，填写主题，生成文案  
3. 选配音、字幕、背景音乐、分辨率  
4. 点击生成视频  

成片会保存在 `final/`，并自动写出同名 `.txt`（第一行标题，后面是正文），给发布页使用。

### 2. Stable Diffusion 生图成片

1. 启动 WebUI，并打开 API（例如 `--api`）  
2. 基本配置 → 素材来源选 `stableDiffusion`  
3. 地址填 `http://127.0.0.1:7860`（不必手写 `/sdapi/v1`）  
4. 回到生成页，设置模型、宽高、步数、CFG（建议 7 左右）  
5. 生成文案后点生成：会按句子分段生图，再按配音时长合成短视频  

建议竖屏：宽 720、高 1280。Seed 填 `-1` 为随机。

### 3. 多平台自动发布

成片页可以直接：

- 勾选 **生成完成后自动发布到多平台**，或  
- 成片结束后点 **一键发布到多平台**

也可以去 **批量视频自动发布** 页，手动选 `final/` 里的视频和文案。

发布前准备：

1. Chrome 开启远程调试并登录各平台：

```bash
chrome.exe --remote-debugging-port=9222 --user-data-dir="C:\chrome-publish-profile"
```

2. 在发布页填写 ChromeDriver 路径、调试地址 `127.0.0.1:9222`  
3. 勾选要发的平台（抖音 / 快手 / 小红书 / 视频号 / B 站）

> 平台网页改版可能导致选择器失效。发布属于自动化操作，请自行承担账号风险。

---

## 目录结构（常用）

```
gui.py                 # 基本配置
pages/
  01_auto_video.py     # AI / SD 成片
  02_mix_video.py      # 混剪
  02_merge_video.py    # 合并
  03_auto_publish.py   # 多平台发布
services/
  sd/                  # Stable Diffusion
  video/               # 合成与转场
  publisher/           # 各平台上传
config/config.example.yml
work/                  # 中间文件
final/                 # 成片与发布文案
```

---

## 优化版改动

- 打通 SD：文案分段生图 → 配音对齐 → 成片 → 字幕  
- 成片自动导出发布用 `.mp4` + `.txt`  
- 生成页一键多平台发布  
- 修正 CFG 范围、WebUI 地址自动补全、图片转视频像素格式  
- 音频时长改为浮点，减少声画对不齐  
- 修复合并视频时 FFmpeg 滤镜参数粘连导致失败  
- SD 未启动时页面不再直接崩溃  

---

## 常见问题

**ffmpeg 报 `No such filter`**  
升级到 ffmpeg 6.0 以上，并确认 PATH 生效。

**SD 连不上**  
WebUI 要开 API；地址用 `http://127.0.0.1:7860`。防火墙不要拦 7860。

**一键发布没反应**  
先打开过发布页、填好 ChromeDriver、浏览器调试模式已开，并至少勾选一个平台。

**阿里云配音 `list index out of range`**  
录音文件识别（极速版）需要开通商用。

**生成很慢**  
SD 按文案分段逐张出图。文案越长、步数越多越慢，可先用 60 字、20 步试跑。

---

## License

见仓库内 `LICENSE`。请勿把 API Key、`config/config.yml` 提交到 Git。
