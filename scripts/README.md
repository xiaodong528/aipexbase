# AIPEXBASE 项目自动创建脚本

自动创建 AIPEXBASE 应用/项目并生成对应的 API Key (Token)，用于后续 MCP 工具集成。

## 功能特性

- ✅ 自动登录 AIPEXBASE 管理后台
- ✅ 创建新的应用/项目
- ✅ 为项目生成 API Key (Token)
- ✅ 自动生成 MCP 服务器配置文件
- ✅ 友好的彩色终端输出
- ✅ 完整的错误处理和提示

## 安装步骤

### 1. 确保已安装 Python 3.7+

```bash
python3 --version
```

### 2. 进入 scripts 目录

```bash
cd scripts
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

或使用虚拟环境（推荐）：

```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 配置说明

### 1. 复制环境变量模板

```bash
cp .env.example .env
```

### 2. 编辑 .env 文件

打开 `.env` 文件并修改以下配置：

```bash
# AIPEXBASE 服务器配置
AIPEXBASE_BASE_URL=http://localhost:8080

# 管理员认证信息
AIPEXBASE_ADMIN_EMAIL=your_admin@example.com
AIPEXBASE_ADMIN_PASSWORD=your_password

# API Key 配置
AIPEXBASE_API_KEY_NAME=MCP 专用密钥
AIPEXBASE_API_KEY_DESC=用于 MCP 工具调用的 API 密钥
AIPEXBASE_API_KEY_EXPIRE=

# 输出配置
AIPEXBASE_OUTPUT_FILE=mcp_config.json
AIPEXBASE_VERBOSE=false
```

**必填项**：
- `AIPEXBASE_BASE_URL` - AIPEXBASE 服务器地址
- `AIPEXBASE_ADMIN_EMAIL` - 管理员邮箱
- `AIPEXBASE_ADMIN_PASSWORD` - 管理员密码

**可选项**：其他配置项都有合理的默认值，可以不设置。

**注意**：
- 项目名称和描述通过命令行参数传递
- `.env` 文件包含敏感信息，请勿提交到版本控制系统

## 使用方法

### 基本使用（使用默认项目名称）

不指定项目名称时，会自动生成带时间戳的项目名称：

```bash
python aipexbase.py
# 将创建名为 "AI项目_20241030_123456" 的项目
```

### 指定项目名称

```bash
python aipexbase.py "我的AI项目"
```

### 指定项目名称和描述

```bash
python aipexbase.py "我的AI项目" "这是一个测试项目"
```

### 显示详细输出（调试用）

```bash
python aipexbase.py "我的项目" "项目描述" --verbose
```

### 使用环境变量覆盖配置

也可以通过环境变量直接传递配置（无需 .env 文件）：

```bash
AIPEXBASE_BASE_URL="http://server:8080" \
AIPEXBASE_ADMIN_EMAIL="admin@example.com" \
AIPEXBASE_ADMIN_PASSWORD="password" \
python aipexbase.py "我的项目"
```

### 批量创建多个项目

```bash
# 创建多个测试项目
for i in {1..5}; do
  python aipexbase.py "测试项目_$i" "第$i个测试项目"
done
```

## 输出结果

脚本执行成功后会：

1. 在控制台输出创建的项目信息和 API Key
2. 生成 `mcp_config.json` 文件，内容示例：

```json
{
  "mcpServers": {
    "aipexbase-mcp-server": {
      "url": "http://localhost:8080/mcp/sse?token=kf_api_abcdefg123456789abcdefg123456789"
    }
  }
}
```

## 集成到 AI IDE

### Cursor IDE

1. 打开 Cursor 设置
2. 找到 MCP 服务器配置
3. 将 `mcp_config.json` 中的内容添加到配置中
4. 重启 Cursor

### Claude Desktop

编辑 `~/Library/Application Support/Claude/claude_desktop_config.json`（macOS）：

```json
{
  "mcpServers": {
    "aipexbase-mcp-server": {
      "url": "http://localhost:8080/mcp/sse?token=your_token_here"
    }
  }
}
```

## 执行流程

脚本会按以下步骤执行：

```
1. 加载环境变量配置（.env 或系统环境变量）
   ↓
2. 登录管理后台 (POST /admin/login)
   ↓
3. 创建应用/项目 (POST /admin/application)
   ↓
4. 生成 API Key (POST /admin/application/config/apikeys/{appId}/save)
   ↓
5. 查询 API Key 详情 (POST /admin/application/config/apikeys/{appId}/page)
   ↓
6. 生成 MCP 配置文件
   ↓
7. 完成
```

## 常见问题

### Q: 提示 "连接失败"

**A:** 检查以下几点：
- AIPEXBASE 服务是否正在运行
- `base_url` 配置是否正确
- 网络连接是否正常
- 防火墙是否阻止了连接

### Q: 提示 "登录失败"

**A:** 检查 `.env` 文件或环境变量中的 `AIPEXBASE_ADMIN_EMAIL` 和 `AIPEXBASE_ADMIN_PASSWORD` 是否正确。

### Q: 提示 "缺少必要的环境变量"

**A:** 确保已设置以下必要的环境变量：
- `AIPEXBASE_BASE_URL` - AIPEXBASE 服务器地址
- `AIPEXBASE_ADMIN_EMAIL` - 管理员邮箱
- `AIPEXBASE_ADMIN_PASSWORD` - 管理员密码

可以通过以下方式设置：
1. 创建 `.env` 文件（推荐）
2. 设置系统环境变量
3. 在命令行中临时设置

注意：项目名称通过命令行参数传递。

### Q: API Key 数量限制

**A:** 每个应用最多可以创建 10 个活跃的 API Key。如果超过限制，需要先删除或禁用旧的 Key。

### Q: 如何为多个项目创建不同的 MCP 配置？

**A:** 直接通过命令行参数指定不同的项目名称：

```bash
# 项目 1
python aipexbase.py "电商后端"

# 项目 2
python aipexbase.py "内容管理系统"

# 项目 3
python aipexbase.py "数据分析平台"
```

如果需要为不同环境使用不同配置：

```bash
# 开发环境
AIPEXBASE_BASE_URL="http://dev-server:8080" \
python aipexbase.py "我的项目_开发"

# 生产环境
AIPEXBASE_BASE_URL="http://prod-server:8080" \
AIPEXBASE_ADMIN_EMAIL="prod-admin@example.com" \
python aipexbase.py "我的项目_生产"
```

或者使用不同的 .env 文件：

```bash
# 开发环境
cp .env.dev .env
python aipexbase.py "我的项目_开发"

# 生产环境
cp .env.prod .env
python aipexbase.py "我的项目_生产"
```

### Q: 生成的 MCP 配置如何使用？

**A:** 将 `mcp_config.json` 中的配置内容复制到你的 AI IDE 的 MCP 配置文件中：

```json
{
  "mcpServers": {
    "aipexbase-project-1": {
      "url": "http://localhost:8080/mcp/sse?token=token1"
    },
    "aipexbase-project-2": {
      "url": "http://localhost:8080/mcp/sse?token=token2"
    }
  }
}
```

## 命令行参数

```
usage: aipexbase.py [project_name] [description] [options]

位置参数:
  project_name         项目名称 (可选，默认: AI项目_时间戳)
  description          项目描述 (可选，默认: 空)

可选参数:
  -h, --help           显示帮助信息
  --verbose            显示详细输出（包含错误堆栈信息）

环境变量配置:
  AIPEXBASE_BASE_URL           服务器地址 (必填)
  AIPEXBASE_ADMIN_EMAIL        管理员邮箱 (必填)
  AIPEXBASE_ADMIN_PASSWORD     管理员密码 (必填)
  AIPEXBASE_API_KEY_NAME       API Key 名称 (可选)
  AIPEXBASE_API_KEY_DESC       API Key 描述 (可选)
  AIPEXBASE_API_KEY_EXPIRE     过期时间 (可选)
  AIPEXBASE_OUTPUT_FILE        输出文件路径 (可选)
  AIPEXBASE_VERBOSE            详细输出 (可选)

示例:
  python aipexbase.py                           # 使用默认项目名称
  python aipexbase.py "我的项目"                 # 指定项目名称
  python aipexbase.py "我的项目" "项目描述"      # 指定名称和描述
  python aipexbase.py --verbose                 # 显示详细输出
```

## 目录结构

```
scripts/
├── aipexbase.py  # 主脚本
├── .env.example                 # 环境变量配置模板
├── .env                         # 环境变量配置（需自行创建，不提交到版本控制）
├── requirements.txt             # Python 依赖
├── README.md                    # 本文档
└── mcp_config.json             # 生成的 MCP 配置（运行后）
```

## 作为 Python 模块使用

除了作为命令行脚本，`aipexbase.py` 也可以作为 Python 模块导入到你的项目中，实现编程式项目创建。

### 导入模块

```python
from scripts.aipexbase import (
    AIPEXBASEClient,          # 主客户端类
    create_client_from_env,   # 工厂函数
    create_project,           # 便捷函数
    ProjectCreationResult,    # 结果数据类
    AIPEXBASEError,          # 异常类
    AuthenticationError,
    APIError,
    ConfigurationError
)
```

### 使用方式 1：便捷函数（推荐）

最简单的方式，自动从环境变量读取配置：

```python
from scripts.aipexbase import create_project

# 自动从 .env 读取配置并创建项目
result = create_project("我的项目", "项目描述")

print(f"项目创建成功！")
print(f"App ID: {result.app_id}")
print(f"Token: {result.api_key}")
print(f"MCP URL: {result.mcp_url}")

# 使用 MCP 配置
mcp_config = result.mcp_config
# {'mcpServers': {'aipexbase-mcp-server': {'url': 'http://...'}}}
```

### 使用方式 2：工厂函数创建客户端

更灵活的方式，手动创建客户端：

```python
from scripts.aipexbase import create_client_from_env

# 从环境变量创建并自动登录
client = create_client_from_env()

# 创建项目
result = client.create_project_complete(
    project_name="电商后端",
    description="电商系统后端服务",
    api_key_name="生产环境密钥",
    api_key_expire="2025-12-31 23:59:59"
)

print(f"Token: {result.api_key}")
```

### 使用方式 3：完全自定义

完全控制配置和流程：

```python
from scripts.aipexbase import AIPEXBASEClient, ProjectCreationResult

# 手动创建客户端
client = AIPEXBASEClient("http://server:8080")

# 手动登录
client.login("admin@example.com", "password")

# 创建项目
result = client.create_project_complete(
    project_name="我的项目",
    description="项目描述",
    verbose=False  # 禁用详细输出
)

# 访问结果
app_id = result.app_id
token = result.api_key
mcp_url = result.mcp_url
```

### 集成到 Web 应用

**Django/Flask 示例：**

```python
from scripts.aipexbase import create_project, APIError
import logging

logger = logging.getLogger(__name__)

def create_user_project(user_id, project_name, description=""):
    """为用户创建 AIPEXBASE 项目"""
    try:
        # 创建项目
        result = create_project(
            project_name=f"{user_id}_{project_name}",
            description=description or f"User {user_id}'s project"
        )

        # 保存到数据库
        UserProject.objects.create(
            user_id=user_id,
            app_id=result.app_id,
            app_name=result.app_name,
            api_key=result.api_key,
            mcp_url=result.mcp_url
        )

        logger.info(f"为用户 {user_id} 创建项目成功: {result.app_id}")
        return result

    except APIError as e:
        logger.error(f"创建项目失败: {e}")
        raise
```

**FastAPI 示例：**

```python
from fastapi import FastAPI, HTTPException
from scripts.aipexbase import create_project, APIError
from pydantic import BaseModel

app = FastAPI()

class ProjectCreateRequest(BaseModel):
    name: str
    description: str = ""

@app.post("/api/projects")
async def aipexbase(request: ProjectCreateRequest):
    """创建 AIPEXBASE 项目"""
    try:
        result = create_project(request.name, request.description)

        return {
            "success": True,
            "data": {
                "app_id": result.app_id,
                "app_name": result.app_name,
                "api_key": result.api_key,
                "mcp_url": result.mcp_url
            }
        }
    except APIError as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### 异常处理

使用专用异常类进行精确的错误处理：

```python
from scripts.aipexbase import (
    create_project,
    AIPEXBASEError,      # 基础异常
    ConfigurationError,  # 配置错误
    AuthenticationError, # 认证失败
    APIError            # API 调用失败
)

try:
    result = create_project("我的项目")

except ConfigurationError as e:
    print(f"配置错误: {e}")
    # 处理配置缺失或错误

except AuthenticationError as e:
    print(f"认证失败: {e}")
    # 处理登录失败

except APIError as e:
    print(f"API 错误: {e}")
    # 处理 API 调用失败

except AIPEXBASEError as e:
    print(f"AIPEXBASE 错误: {e}")
    # 通用错误处理
```

### ProjectCreationResult 数据类

返回的结果是一个数据类，包含所有相关信息：

```python
@dataclass
class ProjectCreationResult:
    app_id: str                # 应用ID
    app_name: str              # 应用名称
    api_key: str               # API Key (token)
    api_key_name: str          # API Key 显示名称
    mcp_url: str               # MCP 服务器 URL
    mcp_config: Dict[str, Any] # MCP 配置字典
    app_info: Dict[str, Any]   # 完整的应用信息
    api_key_info: Dict[str, Any] # 完整的 API Key 信息
```

使用示例：

```python
result = create_project("我的项目")

# 直接访问属性
print(result.app_id)
print(result.api_key)
print(result.mcp_url)

# 使用 MCP 配置
import json
with open('mcp_config.json', 'w') as f:
    json.dump(result.mcp_config, f, indent=2)

# 访问完整信息（用于调试或高级用途）
print(result.app_info['status'])
print(result.api_key_info['expireAt'])
```

### 环境变量配置

模块化使用时同样需要配置环境变量（.env 文件或系统环境变量）：

```bash
# 必填
AIPEXBASE_BASE_URL=http://localhost:8080
AIPEXBASE_ADMIN_EMAIL=admin@example.com
AIPEXBASE_ADMIN_PASSWORD=password

# 可选（有默认值）
AIPEXBASE_API_KEY_NAME=MCP 专用密钥
AIPEXBASE_API_KEY_DESC=用于 MCP 工具调用的 API 密钥
AIPEXBASE_API_KEY_EXPIRE=
```

## API 端点说明

脚本使用以下 AIPEXBASE API 端点：

| 操作 | 方法 | 端点 | 说明 |
|------|------|------|------|
| 登录 | POST | `/admin/login` | 获取管理员 JWT Token |
| 创建应用 | POST | `/admin/application` | 创建新的应用/项目 |
| 生成 Key | POST | `/admin/application/config/apikeys/{appId}/save` | 为应用生成 API Key |
| 查询 Key | POST | `/admin/application/config/apikeys/{appId}/page` | 查询应用的 API Key 列表 |

## 技术栈

- **Python 3.7+**: 脚本语言
- **requests**: HTTP 请求库
- **python-dotenv**: 环境变量管理
- **colorama**: 彩色终端输出

## 许可证

本脚本是 AIPEXBASE 项目的一部分，遵循项目的开源协议。

## 支持

如有问题，请查阅：
- [AIPEXBASE 使用手册](https://vvx03gck2p.feishu.cn/docx/LSsLdYZQfoAo3zxTkwrcJuGVnC3)
- [AIPEXBASE Docker 部署指南](../docs/INSTALL.md)
- [AI IDE 集成指南](../docs/IntegrationAI.md)
