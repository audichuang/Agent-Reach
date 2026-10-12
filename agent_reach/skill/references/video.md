# 视频/播客

## YouTube (yt-dlp)

```bash
yt-dlp --dump-json "URL"                      # 元数据
yt-dlp --dump-json "ytsearch5:query"          # 搜索
yt-dlp --write-sub --write-auto-sub --sub-lang "zh-Hans,zh,en" --skip-download -o "/tmp/%(id)s" "URL"  # 字幕 → /tmp/ID.*.vtt
yt-dlp --write-comments --skip-download --write-info-json --extractor-args "youtube:max_comments=20" -o "/tmp/%(id)s" "URL"  # 评论在 .info.json 的 comments，网页抓取，不保证完整
```

自动字幕可能行间重复，需去重。

### 字幕失败重试链（按序，拿到实质内容即停）

`doctor` 只验证 yt-dlp 与 JS runtime 可执行，`active_backend: yt-dlp` 不代表目标视频字幕可取。

1. 上面的 `yt-dlp --write-sub --write-auto-sub`。
2. bot 校验、字幕为空或没生成文件，且 OpenCLI 已连接：`opencli youtube transcript "URL" -f yaml`。
3. 返回 `Caption URL returned empty response` 时最多重试 3 次（字幕 URL 过期偶发失效，不等于没有字幕）。
4. 仍失败或本无字幕：`agent-reach transcribe "URL"`（下载音频转写）。

成功标准是非空字幕/转录内容，不是退出码或 `doctor` 结果。

### agent-reach transcribe

```bash
agent-reach transcribe "https://www.youtube.com/watch?v=VIDEO_ID"
agent-reach transcribe ./local_audio.mp3 -o /tmp/transcript.txt
```

- 只接收公开 http(s) URL 或本地音频；`ytsearch5:` 结果需先选出具体视频 URL。
- key：`agent-reach configure groq-key`（隐藏输入，免费，console.groq.com）或 `agent-reach configure openai-key`。
- 默认只用第一个已配置服务商（优先 Groq），失败即停，不自动发给另一家。`--allow-provider-fallback` 才跨服务商降级（音频会被两家处理、可能产生 OpenAI 费用），须确认内容可分享给两家。

## B站（bili-cli 为主，OpenCLI 补字幕）

不要用 yt-dlp 读 B站：会被 412 风控拦截（带 Cookie/代理也无效）。

```bash
bili video BVxxx                          # 详情、互动数据、字幕可用性（只读免登录）
bili search "query" --type video -n 5
bili hot -n 10; bili rank -n 10
bili audio BVxxx                          # 下载并切分 ASR-ready WAV，再交给 agent-reach transcribe
opencli bilibili subtitle BVxxx           # 带时间轴字幕（需桌面 Chrome）
opencli bilibili search "query" -f yaml   # 备选
opencli bilibili video BVxxx -f yaml      # 备选
```

零配置兜底（搜索 API，需先取首页 Cookie）：

```bash
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
curl -s -c /tmp/bili_ck.txt -o /dev/null -A "$UA" "https://www.bilibili.com/"
curl -s -b /tmp/bili_ck.txt -A "$UA" -e "https://www.bilibili.com/" \
  "https://api.bilibili.com/x/web-interface/search/all/v2?keyword=QUERY&page=1"
```

未安装 bili-cli：`pipx install bilibili-cli`。

## 小宇宙播客

```bash
~/.agent-reach/tools/xiaoyuzhou/transcribe.sh [--polish] "https://www.xiaoyuzhoufm.com/episode/EPISODE_ID"
```

输出 Markdown 到 `/tmp/`。`--polish` 多一轮 Groq Llama 3.3 70B 补标点与分段，仅在标点不理想时用。
前置：ffmpeg、`agent-reach configure groq-key`；首次需 `agent-reach install --env=auto --system --channels=xiaoyuzhou`（需用户明确授权）。
