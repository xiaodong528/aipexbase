# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

AIPEXBASE 是一个 AI 原生的后端即服务(BaaS)基础设施,旨在让开发者在 AI 辅助下无需关注后端接口开发即可构建完整应用。

**核心特性:**

- 原生支持 MCP (Model Context Protocol),允许 AI 模型和智能体直接调用后端能力
- 提供开箱即用的数据存储、用户鉴权、文件管理等后端服务
- 前端开发者通过 aipexbase.js SDK 直接调用服务,无需编写后端 API

## 技术栈

**后端:**

- Java 1.8
- Spring Boot 2.5.0
- MyBatis Plus 3.5.1
- MySQL 8.0+
- Redis (可选)
- Maven

**前端管理后台:**

- Vue 3
- Vite 5
- Element Plus
- Tailwind CSS
- Node.js 18+

## 项目结构

```
aipexbase/
├── backend/                      # Spring Boot 后端服务
│   ├── src/main/java/com/kuafuai/
│   │   ├── BaasMainApplication.java    # 主应用入口
│   │   ├── api/                        # 公开 API 层(供前端 SDK 调用)
│   │   ├── manage/                     # 管理功能模块
│   │   │   └── mcp/                    # MCP 协议实现和工具
│   │   ├── dynamic/                    # 动态数据库操作核心
│   │   │   ├── orchestrator/           # 查询编排器
│   │   │   ├── service/                # 动态 CRUD 服务
│   │   │   └── validation/             # 数据验证
│   │   ├── login/                      # 登录认证模块
│   │   ├── system/                     # 系统管理(应用/密钥)
│   │   ├── pay/                        # 支付集成
│   │   ├── wx/                         # 微信集成
│   │   ├── common/                     # 通用工具和配置
│   │   │   ├── storage/                # 文件存储(本地/S3)
│   │   │   ├── cache/                  # 缓存抽象
│   │   │   ├── db/                     # 数据库工具
│   │   │   └── util/                   # 工具类
│   │   └── error_report/               # 错误上报
│   └── src/main/resources/
│       ├── application.yml             # 主配置文件
│       └── application-mysql.yml       # MySQL 配置
├── frontend/                     # Vue3 管理后台
│   ├── src/
│   │   ├── api/                        # API 请求封装
│   │   ├── components/                 # 通用组件
│   │   ├── views/                      # 页面视图
│   │   ├── router/                     # 路由配置
│   │   └── utils/                      # 工具函数
│   └── package.json
├── install/
│   ├── docker-compose.yaml             # Docker 部署配置
│   └── mysql/init.sql                  # 数据库初始化脚本
└── docs/                         # 文档
    ├── INSTALL.md                      # 安装指南
    └── IntegrationAI.md                # AI IDE 集成指南
```

## 核心架构理解

### 1. MCP 服务器实现

位于 `backend/src/main/java/com/kuafuai/manage/mcp/`,这是 AIPEXBASE 的核心特性,实现了 Model Context Protocol,使 AI 工具(如 Cursor/Trae)可以:

- 通过 SSE 端点 `/mcp/sse` 连接
- 调用预定义的 MCP 工具进行数据库操作
- 加载提示词模板辅助开发
- 工具扩展位置: `backend/src/main/java/com/kuafuai/manage/mcp/tool/`

### 2. 动态数据层

`com.kuafuai.dynamic` 包实现了核心的动态数据库能力:

- **动态表管理**: AI 可通过 MCP 工具自动创建/修改表结构
- **通用 CRUD**: 无需编写 mapper/controller,自动生成 CRUD 接口
- **查询编排**: `orchestrator` 包处理复杂查询和关联
- **数据验证**: `validation` 包确保数据完整性

### 3. 多租户应用隔离

- `system` 模块管理应用和 API Key
- 每个应用有独立的数据表空间
- 通过 token 参数识别应用上下文

### 4. 存储抽象

`common.storage` 包提供统一的文件存储接口,支持:

- 本地文件系统
- S3 兼容对象存储
- 通过 `application.yml` 中 `storage.type` 配置切换

## 常用开发命令

### 后端开发

**启动后端服务:**

```bash
cd backend
mvn spring-boot:run
```

服务将在 http://localhost:8080 启动

**构建 JAR 包:**

```bash
cd backend
mvn clean package
```

输出: `backend/target/aipexbase-0.0.1-SNAPSHOT.jar`

**运行测试:**

```bash
cd backend
mvn test
```

**修改数据库配置:**
编辑 `backend/src/main/resources/application-mysql.yml`,修改 JDBC 连接信息

### 前端开发

**安装依赖:**

```bash
cd frontend
npm install
```

**启动开发服务器:**

```bash
cd frontend
npm run dev
```

**构建生产版本:**

```bash
cd frontend
npm run build
# 或针对 H5
npm run build:h5
```

### Docker 部署

**完整部署(MySQL + 后端 + 前端):**

```bash
cd install
docker-compose up --build -d
```

**查看日志:**

```bash
cd install
docker-compose logs -f backend-new
```

**停止服务:**

```bash
cd install
docker-compose down
```

## 数据库初始化

**首次安装必须执行:**

1. 创建 MySQL 数据库
2. 导入 `install/mysql/init.sql`
3. 修改 `backend/src/main/resources/application-mysql.yml` 配置

## API 端点说明

**核心端点:**

- `/mcp/sse?token=xxx` - MCP 协议 SSE 连接(AI IDE 使用)
- `/mcp/message` - MCP 消息端点
- `/api/**` - 公开 API(供前端 SDK 调用)
- `/manage/**` - 管理后台 API
- `/doc.html` - Knife4j API 文档(开发环境)

**认证方式:**

- MCP 连接: URL 参数 `token`
- 管理后台: JWT Bearer Token
- 前端 SDK: API Key

## 环境变量配置

主要环境变量(在 `application.yml` 中定义,可通过环境变量覆盖):

```bash
PORT=8080                          # 服务端口
DB_TYPE=mysql                      # 数据库类型
CACHE_TYPE=local                   # 缓存类型: local|redis
STORAGE_TYPE=local                 # 存储类型: local|s3
UPLOAD_PATH=../uploadPath          # 文件上传路径
MCP_SERVER_NAME=baas-mcp-server    # MCP 服务器名称
```

## 扩展 MCP 工具

**添加新的 MCP 工具:**

1. 在 `backend/src/main/java/com/kuafuai/manage/mcp/tool/` 创建新的工具类
2. 实现工具注解和业务逻辑
3. 重启服务后工具会自动暴露给 AI IDE

**示例位置参考:**
`backend/src/main/java/com/kuafuai/manage/mcp/tool/`

## 日志和调试

**查看 MCP 调试日志:**
在 `application.yml` 中已配置:

```yaml
logging:
  level:
    com.kuafuai.manage.mcp: debug
```

**后端日志位置:**

- 开发环境: 控制台输出
- Docker 部署: 挂载目录(在 docker-compose.yaml 中配置)

## 相关文档

- [使用手册](https://vvx03gck2p.feishu.cn/docx/LSsLdYZQfoAo3zxTkwrcJuGVnC3)
- [Docker 部署指南](docs/INSTALL.md)
- [AI IDE 集成指南](docs/IntegrationAI.md)
- [Roadmap](docs/ROADMAP.md)

## 开发注意事项

**后端:**

- 使用 MyBatis Plus 作为 ORM,mapper 文件位于 `src/main/resources/mapper/`
- Spring Security 已启用,注意权限配置
- 事务管理已开启(`@EnableTransactionManagement`)
- 支持异步操作(`@EnableAsync`)和重试(`@EnableRetry`)

**前端:**

- 使用 Vue 3 Composition API
- Element Plus 组件库已自动导入(通过 unplugin-auto-import)
- API 基础地址通过环境变量 `VITE_APP_SERVICE_API` 配置
- 路由权限控制在 `src/permission.js` 中实现

**通用:**

- 项目使用 UTF-8 编码
- 时区设置为 GMT+8
- 代码风格遵循各自语言的标准约定

"""当你收到一个软件研发任务时，可以通过此工作流模版中的具体任务步骤与 LLM 交互并超高质量的完成一个软件的研发全流程

  ---
  📝 完整工作流步骤

  步骤 1: 前端项目初始化

  在任何应用研发任务开始前，如果当前项目目录下没有前端工程项目，务必帮助用户以当前目录作为工作目录初始化前端项目。

  【IMPORTANT】 在任何情况下都要使用 aipexbase-js 这个前端 SDK 进行前端编码。

  安装方式:
  npm install aipexbase-js

  使用示例:
  import { createClient } from "aipexbase-js";

  const client = createClient({
    baseUrl: "https://your-aipexbase.example.com",
    apiKey: "YOUR_API_KEY",
  });

  // 1) 登录
  await client.auth.login({ phone: "13800000000", password: "******" });

  // 2) 查询数据
  const list = await client.db
    .from("todos")
    .list()
    .eq("status", "open")
    .order("created_at", "desc");

  // 3) 创建数据
  const created = await client.db
    .from("todos")
    .insert()
    .values({ title: "Buy milk", status: "open" });

  // 4) 调用后端自定义 API
  const result = await client.api
    .call("send_sms")
    .param("to", "+8613800000000")
    .param("text", "Hello");

  ---
  步骤 2: 需求澄清和拆解

  【IMPORTANT】 你首先需要帮助用户澄清和拆解他的需求，给他的需求增加更多相关性的细节并询问是否按照你给出的细节进行开发。

  ---
  步骤 3: 查看和设计数据库表结构

  开发前，你需要先查看一下当前应用中的所有表结构信息，可以调用 list_tables 工具查询所有表结构信息。如果不满足，则设计新的表。

  表结构设计规范:

  表结构请转换为 JSON 数组，并严格参照以下示例：

  [{
    "tableName": "users",
    "description": "用户表",
    "columns": [
      {
        "tableName": "users",
        "columnName": "id",
        "columnComment": "用户ID",
        "columnType": "bigint",
        "dslType": "Long",
        "defaultValue": null,
        "isPrimary": true,
        "isNullable": false,
        "referenceTableName": null
      },
      {
        "tableName": "users",
        "columnName": "username",
        "columnComment": "用户名",
        "columnType": "varchar(50)",
        "dslType": "String",
        "defaultValue": "",
        "isPrimary": false,
        "isNullable": false,
        "referenceTableName": null
      },
      {
        "tableName": "users",
        "columnName": "phone",
        "columnComment": "手机号",
        "columnType": "varchar(20)",
        "dslType": "phone",
        "defaultValue": "",
        "isPrimary": false,
        "isNullable": true,
        "referenceTableName": null
      },
      {
        "tableName": "users",
        "columnName": "created_at",
        "columnComment": "创建时间",
        "columnType": "datetime",
        "dslType": "datetime",
        "defaultValue": null,
        "isPrimary": false,
        "isNullable": false,
        "referenceTableName": null
      }
    ]
  }]

  字段说明:
  - tableName: 表名
  - referenceTableName: 其他表的表名，表示当前字段是其他表的主键（外键关系）
  - isPrimary: 是否是主键
  - isNullable: 是否可为空
  - defaultValue: 默认值
  - dslType: 数据类型（见下方说明）
  - columnName: 字段名
  - columnComment: 字段含义说明
  - columnType: 字段类型（使用 MySQL 8.0 支持的字段类型）

  dslType 类型说明:

  | dslType  | 说明    | 适用场景                         |
  |----------|-------|------------------------------|
  | number   | 整数    | 计数等场景                        |
  | double   | 小数    | 分数、评分等场景                     |
  | decimal  | 高精度小数 | 金融计算等场景                      |
  | string   | 文本    | 文本输入（≤512字符），模糊查询            |
  | keyword  | 关键字   | 精确匹配（≤256字符），如分类、订单号、标签、状态码等 |
  | longtext | 长文本   | 长文本输入                        |
  | date     | 日期    | 格式 YYYY-MM-DD                |
  | datetime | 日期时间  | 格式 YYYY-MM-DD HH:mm:ss       |
  | time     | 时间    | 格式 HH:mm:ss                  |
  | password | 密码    | 密码输入                         |
  | phone    | 手机号   | 手机号输入                        |
  | email    | 邮箱    | 邮箱输入                         |
  | images   | 图片列表  | 图片上传（支持 max_size, min_size）  |
  | videos   | 视频列表  | 视频上传（支持 max_size, min_size）  |
  | files    | 文件列表  | 文件上传（支持 max_size, min_size）  |
  | boolean  | 布尔值   | 开关、选择等场景                     |

  ---
  步骤 4: 执行 SQL 创建表

  【IMPORTANT】 当你完成表结构 JSON 的设计时，请使用 execute_sql 执行 SQL 的创建：

  参数名: ddl_query参数值: JSON 数组字符串（如步骤 3 中的示例）

  ---
  步骤 5: 使用第三方 API（可选）

  【IMPORTANT】 这里有一些第三方服务的 API，你可以参照这些 API 的调用方式结合 aipexbase-js 制作你的应用。

  系统会根据当前应用配置动态注入可用的第三方 API 信息，包括：
  - 功能描述
  - 参数说明
  - 返回值示例

  ---
  步骤 6: 频繁查询表结构

  你最好频繁地使用 list_tables 工具查询当前应用的所有表结构信息，根据表结构信息高质量地完成你的开发任务。

  ---
  步骤 7: 简洁回复原则

  【IMPORTANT】 你的所有回复需要尽可能的简单，仅表达核心观点即可，请不要给用户任何建议和语气词。

  ---
  🛠️ 可用的 MCP 工具

  根据工作流，主要使用以下 MCP 工具：

  1. list_tables - 查询当前应用的所有表结构信息
  2. execute_sql - 执行 DDL 语句创建或修改表结构
  3. 其他数据操作工具（通过 aipexbase-js SDK 在前端调用）

  ---
  📚 aipexbase-js SDK 完整 API 参考

  认证模块 (auth)

  // 登录（三选一：user_name / phone / email）
  await client.auth.login({
    phone: "13800000000",
    password: "******"
  });

  // 注册
  await client.auth.register({
    username: "张三",
    phone: "13800000000",
    password: "******",
    email: "zhangsan@example.com"
  });

  // 获取当前用户信息
  const user = await client.auth.getUser();

  // 登出
  await client.auth.logout();

  数据库模块 (db)

  // 查询列表
  const list = await client.db
    .from("orders")
    .list()
    .eq("status", "paid")
    .or((q) => q.lt("amount", 100).gt("discount", 0))
    .order("created_at", { ascending: false })
    .page(1, 20);

  // 查询单条
  const item = await client.db
    .from("orders")
    .get()
    .eq("id", 123);

  // 插入数据
  const inserted = await client.db
    .from("orders")
    .insert()
    .values({ amount: 199, status: "paid" });

  // 更新数据
  const updated = await client.db
    .from("orders")
    .update()
    .set({ status: "closed" })
    .eq("id", 123);

  // 删除数据
  const removed = await client.db
    .from("orders")
    .delete()
    .eq("id", 123);

  过滤器:
  - eq(field, value) - 等于
  - neq(field, value) - 不等于
  - gt(field, value) - 大于
  - gte(field, value) - 大于等于
  - lt(field, value) - 小于
  - lte(field, value) - 小于等于
  - in(field, values) - 在集合中
  - between(field, min, max) - 在区间内
  - or(callback) - 组合或条件

  排序和分页:
  - order(field, direction) - direction: "asc" | "desc" | { ascending: boolean }
  - page(number, size) - 分页

  自定义 API 模块 (api)

  const data = await client.api
    .call("send_email")
    .params({ to: "a@b.com", subject: "Hi" })
    .header("X-Request-Id", "rid-001"); """