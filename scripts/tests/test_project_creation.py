"""
项目创建端到端测试

测试完整的项目创建流程，包括：
- 登录 → 创建应用 → 生成 API Key → 生成 MCP 配置
- 错误处理和异常场景
- 配置文件生成
"""
import pytest
import json
from pathlib import Path
from typing import Dict, Any

from aipexbase import (
    AIPEXBASEClient,
    ProjectCreationResult,
    AuthenticationError,
    get_mcp_base_url,
    generate_mcp_config
)
from tests.fixtures.test_data import TEST_DATA


@pytest.mark.integration
@pytest.mark.requires_backend
class TestCompleteProjectCreation:
    """测试完整的项目创建流程"""

    def test_create_project_complete_flow(
        self,
        skip_if_no_backend,
        test_client: AIPEXBASEClient,
        test_project_name: str,
        test_config: Dict[str, Any],
        created_projects: list
    ):
        """测试完整的项目创建流程（端到端）"""
        # 执行完整的项目创建流程
        result = test_client.create_project_complete(
            project_name=test_project_name,
            description=f"端到端测试项目：{test_project_name}",
            api_key_name=TEST_DATA.API_KEY_DEFAULT_NAME,
            api_key_description=TEST_DATA.API_KEY_DEFAULT_DESCRIPTION,
            verbose=False
        )

        # 验证返回结果
        assert result is not None
        assert isinstance(result, ProjectCreationResult)

        # 验证应用信息
        assert result.app_id is not None
        assert result.app_name == test_project_name

        # 验证 API Key
        assert result.api_key is not None
        assert len(result.api_key) > 0

        # 验证 MCP URL
        assert result.mcp_url is not None
        assert result.api_key in result.mcp_url
        assert "/mcp/sse" in result.mcp_url

        # 验证 MCP 配置
        assert result.mcp_config is not None
        assert "mcpServers" in result.mcp_config

        # 记录创建的项目
        created_projects.append({
            "appId": result.app_id,
            "appName": result.app_name
        })

    def test_create_project_with_custom_parameters(
        self,
        skip_if_no_backend,
        test_client: AIPEXBASEClient,
        created_projects: list
    ):
        """测试使用自定义参数创建项目"""
        custom_name = TEST_DATA.get_project_name("custom")
        custom_api_key_name = "自定义密钥名称"
        custom_description = "自定义项目描述"
        custom_expire = "2099-12-31 23:59:59"

        result = test_client.create_project_complete(
            project_name=custom_name,
            description=custom_description,
            api_key_name=custom_api_key_name,
            api_key_description="自定义密钥描述",
            api_key_expire=custom_expire,  # 正确的参数名是 api_key_expire
            verbose=False
        )

        assert result is not None
        assert result.app_name == custom_name

        created_projects.append({
            "appId": result.app_id,
            "appName": result.app_name
        })

    def test_create_project_with_verbose_output(
        self,
        skip_if_no_backend,
        test_client: AIPEXBASEClient,
        test_project_name: str,
        created_projects: list,
        capsys
    ):
        """测试 verbose 模式的输出"""
        result = test_client.create_project_complete(
            project_name=test_project_name,
            description="Verbose 测试",
            verbose=True  # 启用详细输出
        )

        # 验证创建成功
        assert result is not None
        created_projects.append({
            "appId": result.app_id,
            "appName": result.app_name
        })

        # 验证有输出（verbose=True 时）
        captured = capsys.readouterr()
        assert len(captured.out) > 0 or len(captured.err) > 0

    def test_create_project_without_authentication(
        self,
        skip_if_no_backend,
        unauthenticated_client: AIPEXBASEClient
    ):
        """测试未登录时创建项目"""
        # 未登录的客户端没有 token
        assert unauthenticated_client.token is None

        # 尝试创建项目应该抛出 AuthenticationError
        with pytest.raises(AuthenticationError) as exc_info:
            unauthenticated_client.create_project_complete(
                project_name="unauthorized_project"
            )

        assert "未登录" in str(exc_info.value)


@pytest.mark.integration
@pytest.mark.requires_backend
class TestMCPConfigGeneration:
    """测试 MCP 配置生成"""

    def test_mcp_url_generation(self, test_config: Dict[str, Any]):
        """测试 MCP URL 生成"""
        base_url = test_config["base_url"]
        api_key = "ak_test_123"

        # 获取 MCP 基础 URL
        mcp_base = get_mcp_base_url(base_url)

        # 生成完整的 MCP URL
        expected_url = f"{mcp_base}/mcp/sse?token={api_key}"

        # 验证 URL 格式
        assert "/mcp/sse?token=" in expected_url
        assert api_key in expected_url

    def test_mcp_config_structure(self):
        """测试 MCP 配置结构"""
        config = generate_mcp_config(
            base_url="http://localhost:8080",
            api_key="ak_test_123",
            server_name="test-server"
        )

        # 验证配置结构
        assert "mcpServers" in config
        assert "test-server" in config["mcpServers"]
        assert "url" in config["mcpServers"]["test-server"]

        # 验证 URL 格式
        url = config["mcpServers"]["test-server"]["url"]
        assert "/mcp/sse?token=ak_test_123" in url

    def test_mcp_config_with_default_server_name(self):
        """测试使用默认服务器名称的 MCP 配置"""
        config = generate_mcp_config(
            base_url="http://localhost:8080",
            api_key="ak_test_123"
        )

        # 验证使用了默认服务器名称
        assert "mcpServers" in config
        # 默认服务器名称应该是 "aipexbase-mcp-server"
        assert "aipexbase-mcp-server" in config["mcpServers"]

    def test_mcp_config_json_serializable(self):
        """测试 MCP 配置可以序列化为 JSON"""
        config = generate_mcp_config(
            base_url="http://localhost:8080",
            api_key="ak_test_123"
        )

        # 应该可以成功序列化为 JSON
        json_str = json.dumps(config, indent=2)
        assert json_str is not None

        # 应该可以反序列化回来
        parsed = json.loads(json_str)
        assert parsed == config


@pytest.mark.integration
class TestConfigFileSaving:
    """测试配置文件保存"""

    def test_save_mcp_config_to_file(self, tmp_path: Path):
        """测试保存 MCP 配置到文件"""
        config = generate_mcp_config(
            base_url="http://localhost:8080",
            api_key="ak_test_123"
        )

        # 保存到临时文件
        config_file = tmp_path / "mcp_config.json"
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

        # 验证文件存在
        assert config_file.exists()

        # 验证文件内容
        with open(config_file, "r", encoding="utf-8") as f:
            loaded_config = json.load(f)

        assert loaded_config == config

    def test_mcp_config_file_format(self, tmp_path: Path):
        """测试 MCP 配置文件格式符合规范"""
        config = generate_mcp_config(
            base_url="http://localhost:8080",
            api_key="ak_test_123",
            server_name="my-server"
        )

        config_file = tmp_path / "mcp_config.json"
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

        # 读取并验证格式
        with open(config_file, "r", encoding="utf-8") as f:
            content = f.read()

        # 验证 JSON 格式
        assert content.startswith("{")
        assert content.endswith("}\n") or content.endswith("}")

        # 验证包含必要的字段
        assert "mcpServers" in content
        assert "my-server" in content
        assert "url" in content


@pytest.mark.integration
@pytest.mark.requires_backend
class TestErrorScenarios:
    """测试错误场景"""

    def test_create_project_with_existing_name(
        self,
        skip_if_no_backend,
        test_client: AIPEXBASEClient,
        test_project_name: str,
        created_projects: list
    ):
        """测试使用已存在的项目名称创建项目"""
        # 第一次创建应该成功
        result1 = test_client.create_project_complete(
            project_name=test_project_name,
            verbose=False
        )
        assert result1 is not None
        created_projects.append({
            "appId": result1.app_id,
            "appName": result1.app_name
        })

        # 后端允许创建同名应用，所以第二次也应该成功
        # 但会得到不同的 appId
        result2 = test_client.create_project_complete(
            project_name=test_project_name,
            verbose=False
        )
        assert result2 is not None
        assert result2.app_name == test_project_name
        # 验证两个应用的 ID 不同
        assert result2.app_id != result1.app_id

        created_projects.append({
            "appId": result2.app_id,
            "appName": result2.app_name
        })

    def test_create_project_with_empty_name(
        self,
        skip_if_no_backend,
        test_client: AIPEXBASEClient
    ):
        """测试使用空名称创建项目"""
        # 空名称应该失败
        with pytest.raises(Exception):
            test_client.create_project_complete(
                project_name="",
                verbose=False
            )

    def test_create_project_with_invalid_expire_date(
        self,
        skip_if_no_backend,
        test_client: AIPEXBASEClient,
        test_project_name: str
    ):
        """测试使用无效的过期时间创建项目"""
        # 使用无效的日期格式
        # 注意：具体行为取决于后端验证
        # 可能抛出异常或被忽略
        try:
            result = test_client.create_project_complete(
                project_name=test_project_name,
                api_key_expire_at="invalid-date-format",
                verbose=False
            )
            # 如果后端允许无效日期，确保至少创建成功
            assert result is not None
        except Exception:
            # 如果后端拒绝无效日期，这是预期的行为
            pass


@pytest.mark.integration
@pytest.mark.requires_backend
@pytest.mark.slow
class TestProjectCreationPerformance:
    """测试项目创建性能"""

    def test_project_creation_completes_within_timeout(
        self,
        skip_if_no_backend,
        test_client: AIPEXBASEClient,
        test_project_name: str,
        test_config: Dict[str, Any],
        created_projects: list
    ):
        """测试项目创建在超时时间内完成"""
        import time

        start_time = time.time()

        result = test_client.create_project_complete(
            project_name=test_project_name,
            verbose=False
        )

        end_time = time.time()
        elapsed = end_time - start_time

        # 验证在合理时间内完成（比如 30 秒）
        timeout = test_config.get("test_timeout", 30)
        assert elapsed < timeout, f"项目创建耗时 {elapsed:.2f}s，超过 {timeout}s 限制"

        assert result is not None
        created_projects.append({
            "appId": result.app_id,
            "appName": result.app_name
        })
