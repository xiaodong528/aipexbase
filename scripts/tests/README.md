# AIPEXBASE 测试套件

本测试套件用于验证 `aipexbase.py` 的核心功能，包括 API 调用、项目创建和配置管理。

## 📋 测试概述

测试采用**真实环境测试**策略，连接实际的 AIPEXBASE 后端服务进行端到端验证。

### 测试范围

- ✅ **核心 API 测试** (`test_core_api.py`)
  - 客户端初始化
  - 登录认证
  - 创建应用
  - 创建和查询 API Key

- ✅ **项目创建测试** (`test_project_creation.py`)
  - 完整的端到端项目创建流程
  - MCP 配置生成
  - 错误场景处理
  - 配置文件保存

- ✅ **工具函数测试** (`test_utils.py`)
  - 环境配置加载
  - URL 处理
  - MCP 配置生成
  - 客户端工厂函数

## 🚀 快速开始

### 1. 前置条件

确保以下条件满足：

- Python 3.7+
- AIPEXBASE 后端服务正在运行
- 有效的管理员账号

### 2. 安装依赖

```bash
cd scripts
pip install -r requirements.txt
```

### 3. 配置测试环境

复制 `.env.test` 为 `.env` 并填写实际配置：

```bash
cp .env.test .env
```

编辑 `.env` 文件：

```bash
# 必需配置
AIPEXBASE_BASE_URL=http://localhost:8080
AIPEXBASE_ADMIN_EMAIL=admin@example.com
AIPEXBASE_ADMIN_PASSWORD=your_password

# 可选配置
AIPEXBASE_API_KEY_NAME=MCP 专用密钥
AIPEXBASE_VERBOSE=false
```

### 4. 运行测试

```bash
# 运行所有测试
pytest

# 运行指定测试文件
pytest tests/test_core_api.py

# 显示详细输出
pytest -v

# 显示打印输出
pytest -s
```

## 📂 文件结构

```
scripts/
├── aipexbase.py              # 源代码
├── .env                      # 测试环境配置（需要创建）
├── .env.test                 # 配置示例
├── pytest.ini                # pytest 配置
└── tests/                    # 测试目录
    ├── __init__.py
    ├── conftest.py           # 共享 fixtures
    ├── test_core_api.py      # 核心 API 测试
    ├── test_project_creation.py  # 项目创建测试
    ├── test_utils.py         # 工具函数测试
    ├── fixtures/             # 测试数据
    │   ├── __init__.py
    │   └── test_data.py
    └── README.md             # 本文件
```

## 🔧 测试配置

### pytest.ini

测试套件通过 `pytest.ini` 配置，主要设置包括：

- 测试发现路径
- 日志级别和格式
- 超时设置（30秒）
- 测试标记（marks）

### 测试标记

可以使用标记选择性运行测试：

```bash
# 仅运行 API 测试
pytest -m api

# 仅运行集成测试
pytest -m integration

# 仅运行工具函数测试
pytest -m utils

# 跳过慢速测试
pytest -m "not slow"

# 仅运行需要后端的测试
pytest -m requires_backend
```

## 📝 测试用例说明

### test_core_api.py

**TestClientInitialization**
- `test_client_init_with_valid_url` - 测试客户端初始化
- `test_client_init_strips_trailing_slash` - 测试 URL 处理

**TestAuthentication**
- `test_login_success` - 测试成功登录
- `test_login_with_invalid_credentials` - 测试错误凭证登录
- `test_authenticated_requests_include_token` - 测试认证请求

**TestApplicationManagement**
- `test_create_application_success` - 测试创建应用
- `test_create_application_with_name_only` - 测试仅名称创建
- `test_create_application_without_authentication` - 测试未认证创建

**TestAPIKeyManagement**
- `test_create_api_key_success` - 测试创建 API Key
- `test_create_api_key_with_expiration` - 测试带过期时间的 Key
- `test_get_api_keys_success` - 测试查询 API Keys
- `test_get_api_keys_with_pagination` - 测试分页查询

### test_project_creation.py

**TestCompleteProjectCreation**
- `test_create_project_complete_flow` - 测试完整创建流程
- `test_create_project_with_custom_parameters` - 测试自定义参数
- `test_create_project_with_verbose_output` - 测试详细输出
- `test_create_project_without_authentication` - 测试未认证创建

**TestMCPConfigGeneration**
- `test_mcp_url_generation` - 测试 MCP URL 生成
- `test_mcp_config_structure` - 测试配置结构
- `test_mcp_config_json_serializable` - 测试 JSON 序列化

**TestErrorScenarios**
- `test_create_project_with_existing_name` - 测试重复名称
- `test_create_project_with_empty_name` - 测试空名称

### test_utils.py

**TestLoadEnvConfig**
- `test_load_from_existing_env_file` - 测试从文件加载
- `test_load_from_environment_variables` - 测试从环境变量加载
- `test_load_with_missing_required_config` - 测试缺少配置

**TestGetMCPBaseURL**
- `test_url_processing` - 测试各种 URL 格式
- `test_url_with_baas_api_suffix` - 测试后缀处理
- `test_url_with_trailing_slash` - 测试斜杠处理

**TestGenerateMCPConfig**
- `test_generate_config_with_default_server_name` - 测试默认名称
- `test_generate_config_with_custom_server_name` - 测试自定义名称
- `test_generated_url_format` - 测试 URL 格式

## 🎯 运行示例

### 基本运行

```bash
# 运行所有测试
pytest

# 运行并显示详细信息
pytest -v

# 运行特定测试类
pytest tests/test_core_api.py::TestAuthentication

# 运行特定测试方法
pytest tests/test_core_api.py::TestAuthentication::test_login_success
```

### 高级选项

```bash
# 在第一个失败时停止
pytest -x

# 显示最慢的 10 个测试
pytest --durations=10

# 生成 HTML 报告（需要安装 pytest-html）
pytest --html=report.html

# 并行运行测试（需要安装 pytest-xdist）
pytest -n auto
```

### 调试测试

```bash
# 显示打印输出
pytest -s

# 进入调试器（失败时）
pytest --pdb

# 详细的错误追踪
pytest --tb=long
```

## 🔍 故障排查

### 问题：后端服务不可用

**症状**：测试被跳过，显示 "后端服务不可用"

**解决方案**：
1. 确认 AIPEXBASE 后端服务正在运行
2. 检查 `.env` 中的 `AIPEXBASE_BASE_URL` 是否正确
3. 尝试手动访问：`curl http://localhost:8080/admin/login`

### 问题：登录失败

**症状**：`AuthenticationError: 认证失败`

**解决方案**：
1. 检查 `.env` 中的管理员邮箱和密码是否正确
2. 确认账号在后端系统中存在且可用
3. 查看后端日志获取详细错误信息

### 问题：配置加载失败

**症状**：`ConfigurationError: 配置加载失败`

**解决方案**：
1. 确认 `.env` 文件存在于 `scripts/` 目录
2. 检查必需配置项是否都已填写
3. 验证配置文件编码为 UTF-8

### 问题：测试超时

**症状**：测试运行超过 30 秒被终止

**解决方案**：
1. 检查网络连接是否正常
2. 确认后端服务响应速度
3. 如需调整超时，修改 `pytest.ini` 中的 `timeout` 值
4. 或在 `.env` 中设置 `TEST_TIMEOUT=60`

### 问题：测试数据未清理

**症状**：测试创建的项目残留在系统中

**解决方案**：
1. 当前版本需要手动清理测试项目
2. 测试结束时会显示创建的项目列表
3. 可以通过管理后台删除测试项目
4. 未来版本将支持自动清理

## 📊 测试覆盖率

查看测试覆盖率（需要安装 pytest-cov）：

```bash
# 运行测试并生成覆盖率报告
pytest --cov=aipexbase --cov-report=html

# 在浏览器中查看报告
open htmlcov/index.html
```

## 🤝 贡献指南

添加新测试时，请遵循以下规范：

1. **文件命名**：`test_*.py`
2. **类命名**：`Test*`（描述性名称）
3. **方法命名**：`test_*`（清晰说明测试内容）
4. **使用 fixtures**：复用 `conftest.py` 中的共享 fixtures
5. **添加标记**：使用 `@pytest.mark.*` 标记测试类型
6. **文档注释**：每个测试方法添加 docstring 说明

示例：

```python
@pytest.mark.api
@pytest.mark.requires_backend
class TestNewFeature:
    """测试新功能"""

    def test_new_feature_success(self, test_client, test_project_name):
        """测试新功能的成功场景"""
        # 测试代码
        pass
```

## 📚 相关资源

- [pytest 文档](https://docs.pytest.org/)
- [AIPEXBASE 文档](https://github.com/kuafuai/aipexbase)
- [项目 README](../../README.md)

## 📧 支持

如遇到问题，请：

1. 查看本文档的故障排查部分
2. 查看测试输出的详细错误信息
3. 查看后端服务日志
4. 提交 Issue 到项目仓库

---

**最后更新**：2024-01-01
