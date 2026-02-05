# NewAPI Keeper

NewAPI 接口保活工具 - 通过定期发送轻量级请求保持 API 活跃状态，避免浪费 token。

## 功能特点

- **Web 管理界面**：实时日志查看、手动触发任务、定时任务状态
- **支持多个 API**：可配置多个 OpenAI 兼容接口，每次运行对所有 API 发送请求
- **Docker Compose 一键部署**：开箱即用，无需配置环境
- 支持多种请求策略（新闻、网页、随机问题）
- 策略优先级和降级机制
- 详细的日志记录（控制台 + 文件），每个 API 单独记录
- 灵活的配置文件
- 内置定时任务（每 12 小时自动执行）

## 项目结构

```
test-newapi/
├── strategies/                # 请求策略模块
│   ├── __init__.py
│   ├── base_strategy.py       # 策略基类
│   ├── news_strategy.py       # 新闻策略
│   ├── webpage_strategy.py    # 网页策略
│   └── random_question_strategy.py  # 随机问题策略
├── templates/                 # Web 界面模板
│   └── index.html             # 管理界面
├── logs/                      # 日志目录
│   ├── newapi_keeper.log      # 主日志
│   └── request_details.jsonl  # 详细请求记录
├── config.yaml                # 配置文件（需手动创建）
├── config.yaml.example        # 配置文件示例
├── config_loader.py           # 配置加载器
├── newapi_client.py           # NewAPI 客户端
├── logger.py                  # 日志模块
├── log_broadcaster.py         # 日志广播（实时推送）
├── app.py                     # Web 服务入口（推荐）
├── main.py                    # 命令行入口（单次执行）
├── Dockerfile                 # Docker 镜像配置
├── docker-compose.yml         # Docker Compose 配置
├── requirements.txt           # Python 依赖
└── README.md                  # 本文件
```

## 快速开始（Docker Compose 推荐）

### 1. 准备配置文件

```bash
cp config.yaml.example config.yaml
```

编辑 `config.yaml`，填写 API 配置：

```yaml
apis:
  - name: "API-1"
    enabled: true
    url: "https://your-api-endpoint-1.com/v1"
    api_key: "your-api-key-1"
    model: "gpt-3.5-turbo"
  
  - name: "API-2"
    enabled: true
    url: "https://your-api-endpoint-2.com/v1"
    api_key: "your-api-key-2"
    model: "gpt-4"
```

### 2. 启动服务

```bash
docker-compose up -d
```

### 3. 浏览器访问

打开浏览器访问 Web 管理界面：

```
http://localhost:5000
```

Web 界面功能：
- 实时查看运行日志
- 手动触发保活任务
- 查看下次定时执行时间
- 查看历史请求记录

---

## 本地开发运行

如果不使用 Docker，可以本地运行：

### 1. 安装依赖

```bash
cd /home/test-newapi
source venv/bin/activate
pip install -r requirements.txt
```

### 2. 配置文件

```bash
cp config.yaml.example config.yaml
# 编辑 config.yaml 填写配置
```

### 3. 运行 Web 服务（推荐）

```bash
python app.py --port 5000
```

然后访问 `http://localhost:5000`

### 4. 仅运行一次保活任务

```bash
python main.py
```

## 配置说明

### API 配置（支持多个）

程序会对所有 `enabled: true` 的 API 发送请求，并分别记录日志。

```yaml
apis:
  - name: "API-1"                     # API 名称（用于日志标识）
    enabled: true                     # 是否启用
    url: "https://api.example1.com/v1"
    api_key: "your-api-key-1"
    model: "gpt-3.5-turbo"
    max_tokens: 100                   # 最大 token 数（控制成本）
    temperature: 0.7                  # 温度参数
  
  - name: "API-2"
    enabled: true
    url: "https://api.example2.com/v1"
    api_key: "your-api-key-2"
    model: "gpt-4"
    max_tokens: 100
    temperature: 0.7
  
  - name: "API-3"
    enabled: false                    # 禁用此 API
    url: "https://api.example3.com/v1"
    api_key: "your-api-key-3"
    model: "gpt-3.5-turbo"
```

### 请求策略配置

策略按优先级顺序执行，失败则降级到下一个策略。

#### 策略 1: 新闻获取

从 RSS 源获取新闻标题，每次随机选择一条新闻。

```yaml
- type: "news"
  enabled: true
  priority: 1
  config:
    rss_urls:
      - "https://www.163.com/rss/"
      - "https://feedx.net/rss/people.xml"
      - "http://www.people.com.cn/rss/politics.xml"
    prompt_template: "用一句话概括这条新闻的核心内容：{news_title}"
    max_news_length: 200
```

#### 策略 2: 网页内容获取

获取指定网页的标题。

```yaml
- type: "webpage"
  enabled: true
  priority: 2
  config:
    urls:
      - "https://www.baidu.com"
      - "https://news.sina.com.cn"
      - "https://www.163.com"
    prompt_template: "总结这个网页标题的主题：{page_title}"
    timeout: 10
```

#### 策略 3: 随机问题（降级方案）

生成随机问题，保证总能生成请求。

```yaml
- type: "random_question"
  enabled: true
  priority: 3
  config:
    question_templates:
      - "计算 {num1} + {num2} 的结果"
      - "将数字 {num} 转换为二进制"
      - "{year} 年是闰年吗？"
    variables:
      num1: [10, 50]      # 随机范围
      num2: [10, 50]
      num: [1, 255]
      year: [2020, 2030]
```

### 日志配置

```yaml
logging:
  path: "./logs"
  level: "INFO"
  max_file_size: 10485760  # 10MB
  backup_count: 5
```

## 定时任务设置

### 使用 crontab

编辑 crontab：

```bash
crontab -e
```

添加定时任务（例如每小时执行一次）：

```bash
0 * * * * cd /home/test-newapi && /home/test-newapi/venv/bin/python /home/test-newapi/main.py >> /home/test-newapi/logs/cron.log 2>&1
```

### 使用 systemd timer

创建服务文件 `/etc/systemd/system/newapi-keeper.service`：

```ini
[Unit]
Description=NewAPI Keeper Service
After=network.target

[Service]
Type=oneshot
User=your-username
WorkingDirectory=/home/test-newapi
ExecStart=/home/test-newapi/venv/bin/python /home/test-newapi/main.py
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

创建定时器文件 `/etc/systemd/system/newapi-keeper.timer`：

```ini
[Unit]
Description=NewAPI Keeper Timer
Requires=newapi-keeper.service

[Timer]
OnCalendar=hourly
Persistent=true

[Install]
WantedBy=timers.target
```

启用并启动定时器：

```bash
sudo systemctl daemon-reload
sudo systemctl enable newapi-keeper.timer
sudo systemctl start newapi-keeper.timer
```

## Docker 部署

项目已包含 `Dockerfile` 和 `docker-compose.yml`，可直接使用。

### docker-compose.yml 配置说明

```yaml
version: '3.8'

services:
  newapi-keeper:
    build: .
    container_name: newapi-keeper
    volumes:
      - ./config.yaml:/app/config.yaml:ro  # 配置文件（只读）
      - ./logs:/app/logs                    # 日志目录
    restart: unless-stopped
    environment:
      - TZ=Asia/Shanghai
      # 代理配置（可选，用于网络受限环境）
      - HTTP_PROXY=${HTTP_PROXY:-}
      - HTTPS_PROXY=${HTTPS_PROXY:-}
    network_mode: host  # 使用宿主机网络
```

### 启动服务

```bash
# 构建并启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 浏览器访问

服务启动后，访问 Web 管理界面：

```
http://localhost:5000
```

> **注意**：由于使用 `network_mode: host`，服务直接监听宿主机的 5000 端口。如需修改端口，可在启动时传入参数或修改 Dockerfile。

## 日志查看

### 主日志

```bash
tail -f logs/newapi_keeper.log
```

### 详细请求记录

```bash
tail -f logs/request_details.jsonl
```

每条记录包含：
- timestamp: 请求时间
- strategy: 使用的策略
- prompt: 发送的提示词
- response: API 响应
- usage: Token 使用情况
- model: 使用的模型

## 故障排查

### 配置文件不存在

```
Error: 配置文件不存在: config.yaml
请复制 config.yaml.example 为 config.yaml 并填写配置
```

解决：`cp config.yaml.example config.yaml` 并编辑配置。

### 所有策略失败

```
ERROR - All strategies failed, no prompt generated
```

检查：
1. 网络连接是否正常
2. RSS 源和网页 URL 是否可访问
3. 随机问题策略是否启用

### API 请求失败

检查日志中的错误信息，常见原因：
- API Key 错误
- API 地址错误
- 网络问题
- 余额不足

## 许可证

MIT License

