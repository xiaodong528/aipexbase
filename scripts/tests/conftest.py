"""
pytest 配置和共享 fixtures
"""
import os
import sys
import pytest
import requests
from pathlib import Path
from typing import Dict, Any

# 添加 scripts 目录到 Python 路径，以便导入 aipexbase 模块
sys.path.insert(0, str(Path(__file__).parent.parent))

from aipexbase import (
    AIPEXBASEClient,
    load_env_config,
    ConfigurationError,
    AuthenticationError
)


@pytest.fixture(scope="session")
def test_config() -> Dict[str, Any]:
    """
    加载测试环境配置

    从 .env 文件或环境变量加载配置。
    测试套件运行前会检查配置是否完整。
    """
    try:
        # 尝试从 .env 文件加载配置
        # load_env_config() 会自动查找 .env 文件
        raw_config = load_env_config()

        # 将嵌套结构转换为扁平结构以方便测试使用
        config = {
            "base_url": raw_config["server"]["base_url"],
            "admin_email": raw_config["admin"]["email"],
            "admin_password": raw_config["admin"]["password"],
            "api_key_name": raw_config["api_key"]["name"],
            "api_key_description": raw_config["api_key"]["description"],
            "api_key_expire_at": raw_config["api_key"]["expire_at"],
            "mcp_config_file": raw_config["output"]["mcp_config_file"],
            "verbose": raw_config["output"]["show_full_response"],
        }

        # 添加测试专用配置
        config["test_mode"] = os.getenv("TEST_MODE", "real")
        config["test_project_prefix"] = os.getenv("TEST_PROJECT_PREFIX", "test_")
        config["test_auto_cleanup"] = os.getenv("TEST_AUTO_CLEANUP", "true").lower() == "true"
        config["test_timeout"] = int(os.getenv("TEST_TIMEOUT", "30"))

        return config
    except (ValueError, ConfigurationError) as e:
        pytest.exit(f"配置加载失败：{e}\n请检查 .env 文件或环境变量配置。", returncode=1)


@pytest.fixture(scope="session")
def backend_available(test_config: Dict[str, Any]) -> bool:
    """
    检查后端服务是否可用

    尝试连接到 AIPEXBASE 后端服务。
    如果后端不可用，将跳过需要后端的测试。
    """
    base_url = test_config["base_url"]
    try:
        # 尝试访问健康检查端点（如果有）或管理员登录端点
        response = requests.get(f"{base_url}/admin/login", timeout=5)
        # 只要能连接上（即使返回错误状态码），也认为后端可用
        return True
    except (requests.ConnectionError, requests.Timeout):
        return False


@pytest.fixture
def skip_if_no_backend(backend_available: bool):
    """
    如果后端不可用，跳过测试

    用法：
        def test_something(skip_if_no_backend):
            # 测试代码
    """
    if not backend_available:
        pytest.skip("后端服务不可用，跳过测试")


@pytest.fixture(scope="session")
def test_client(test_config: Dict[str, Any], backend_available: bool) -> AIPEXBASEClient:
    """
    创建并登录的测试客户端

    返回一个已认证的 AIPEXBASEClient 实例。
    session 级别的 fixture，整个测试会话共享同一个客户端实例。
    """
    if not backend_available:
        pytest.skip("后端服务不可用，跳过测试")

    client = AIPEXBASEClient(test_config["base_url"])

    try:
        # 登录获取 token
        client.login(
            email=test_config["admin_email"],
            password=test_config["admin_password"]
        )
        return client
    except AuthenticationError as e:
        pytest.exit(f"登录失败：{e}\n请检查管理员凭证是否正确。", returncode=1)


@pytest.fixture
def unauthenticated_client(test_config: Dict[str, Any]) -> AIPEXBASEClient:
    """
    创建未认证的测试客户端

    用于测试需要认证的操作在未认证时的行为。
    """
    return AIPEXBASEClient(test_config["base_url"])


@pytest.fixture
def test_project_name(test_config: Dict[str, Any]) -> str:
    """
    生成测试项目名称

    使用前缀 + 时间戳确保唯一性。
    """
    import time
    prefix = test_config.get("test_project_prefix", "test_")
    timestamp = int(time.time())
    return f"{prefix}project_{timestamp}"


@pytest.fixture
def created_projects(test_config: Dict[str, Any]) -> list:
    """
    跟踪测试中创建的项目

    用于测试结束后清理。
    """
    projects = []
    yield projects

    # 测试结束后清理（如果配置了自动清理）
    if test_config.get("test_auto_cleanup", True) and projects:
        # 注意：当前版本的 aipexbase.py 没有提供删除应用的 API
        # 这里仅记录创建的项目，需要手动清理或等待后续版本支持
        print(f"\n创建了以下测试项目，可能需要手动清理：{projects}")


@pytest.fixture
def temp_env_file(tmp_path: Path, test_config: Dict[str, Any]):
    """
    创建临时的 .env 文件用于测试

    用于测试环境配置加载相关的功能。
    """
    env_content = f"""
AIPEXBASE_BASE_URL={test_config['base_url']}
AIPEXBASE_ADMIN_EMAIL={test_config['admin_email']}
AIPEXBASE_ADMIN_PASSWORD={test_config['admin_password']}
AIPEXBASE_API_KEY_NAME={test_config.get('api_key_name', 'MCP 专用密钥')}
AIPEXBASE_VERBOSE=false
"""
    env_file = tmp_path / ".env"
    env_file.write_text(env_content.strip())
    return env_file


@pytest.fixture(autouse=True)
def reset_colorama():
    """
    每个测试后重置 colorama

    防止颜色输出影响测试结果。
    """
    yield
    # 测试结束后的清理（如果需要）
    pass
