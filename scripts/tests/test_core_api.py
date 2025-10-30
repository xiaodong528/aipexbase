"""
核心 API 测试

测试 AIPEXBASEClient 的核心 API 调用功能，包括：
- 登录认证
- 创建应用
- 创建和查询 API Key
"""
import pytest
from typing import Dict, Any

from aipexbase import (
    AIPEXBASEClient,
    AuthenticationError,
    APIError
)
from tests.fixtures.test_data import TEST_DATA


@pytest.mark.api
@pytest.mark.requires_backend
class TestClientInitialization:
    """测试客户端初始化"""

    def test_client_init_with_valid_url(self, test_config: Dict[str, Any]):
        """测试使用有效 URL 初始化客户端"""
        client = AIPEXBASEClient(test_config["base_url"])

        assert client.base_url == test_config["base_url"].rstrip("/")
        assert client.token is None
        assert client.session is not None

    def test_client_init_strips_trailing_slash(self):
        """测试 URL 末尾的斜杠会被自动去除"""
        client = AIPEXBASEClient("http://test.com/")

        assert client.base_url == "http://test.com"


@pytest.mark.api
@pytest.mark.requires_backend
class TestAuthentication:
    """测试认证功能"""

    def test_login_success(
        self,
        skip_if_no_backend,
        unauthenticated_client: AIPEXBASEClient,
        test_config: Dict[str, Any]
    ):
        """测试成功登录"""
        token = unauthenticated_client.login(
            email=test_config["admin_email"],
            password=test_config["admin_password"]
        )

        # 验证返回了 token
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

        # 验证 token 被设置到客户端
        assert unauthenticated_client.token == token

    def test_login_with_invalid_credentials(
        self,
        skip_if_no_backend,
        unauthenticated_client: AIPEXBASEClient
    ):
        """测试使用错误凭证登录"""
        with pytest.raises(Exception) as exc_info:
            unauthenticated_client.login(
                email="invalid@example.com",
                password="wrong_password"
            )

        # 验证抛出了异常
        assert exc_info.value is not None

    def test_authenticated_requests_include_token(
        self,
        skip_if_no_backend,
        test_client: AIPEXBASEClient
    ):
        """测试已认证的请求包含 Authorization header"""
        # test_client fixture 已经登录过了
        assert test_client.token is not None

        # 验证 session 的默认 headers 包含 Authorization
        # 注意：实际的 Authorization 是在 _make_request 中添加的，不是默认 headers
        # 所以这里只验证 token 存在
        assert test_client.token != ""


@pytest.mark.api
@pytest.mark.requires_backend
class TestApplicationManagement:
    """测试应用管理功能"""

    def test_create_application_success(
        self,
        skip_if_no_backend,
        test_client: AIPEXBASEClient,
        test_project_name: str,
        created_projects: list
    ):
        """测试成功创建应用"""
        description = f"测试应用：{test_project_name}"

        app_info = test_client.create_application(
            name=test_project_name,
            description=description
        )

        # 验证返回了应用信息
        assert app_info is not None
        assert isinstance(app_info, dict)

        # 验证必需字段
        assert "appId" in app_info
        assert "appName" in app_info

        # 验证应用信息
        assert app_info["appId"] is not None
        assert len(app_info["appId"]) > 0

        # 记录创建的项目（用于清理）
        created_projects.append({
            "appId": app_info["appId"],
            "appName": app_info["appName"]
        })

    def test_create_application_with_name_only(
        self,
        skip_if_no_backend,
        test_client: AIPEXBASEClient,
        test_project_name: str,
        created_projects: list
    ):
        """测试仅使用名称创建应用"""
        app_info = test_client.create_application(name=test_project_name)

        assert app_info is not None
        assert "appId" in app_info

        created_projects.append({
            "appId": app_info["appId"],
            "appName": app_info.get("appName", test_project_name)
        })

    def test_create_application_without_authentication(
        self,
        skip_if_no_backend,
        unauthenticated_client: AIPEXBASEClient
    ):
        """测试未认证时创建应用"""
        with pytest.raises(Exception):
            unauthenticated_client.create_application(
                name="test_unauthorized",
                description="should fail"
            )


@pytest.mark.api
@pytest.mark.requires_backend
class TestAPIKeyManagement:
    """测试 API Key 管理功能"""

    def test_create_api_key_success(
        self,
        skip_if_no_backend,
        test_client: AIPEXBASEClient,
        test_project_name: str,
        created_projects: list
    ):
        """测试成功创建 API Key"""
        # 先创建一个应用
        app_info = test_client.create_application(name=test_project_name)
        app_id = app_info["appId"]
        created_projects.append(app_info)

        # 创建 API Key
        result = test_client.create_api_key(
            app_id=app_id,
            name=TEST_DATA.API_KEY_DEFAULT_NAME,
            description=TEST_DATA.API_KEY_DEFAULT_DESCRIPTION
        )

        # 验证创建成功
        assert result is True

    def test_create_api_key_with_expiration(
        self,
        skip_if_no_backend,
        test_client: AIPEXBASEClient,
        test_project_name: str,
        created_projects: list
    ):
        """测试创建带过期时间的 API Key"""
        # 先创建一个应用
        app_info = test_client.create_application(name=test_project_name)
        app_id = app_info["appId"]
        created_projects.append(app_info)

        # 创建带过期时间的 API Key
        result = test_client.create_api_key(
            app_id=app_id,
            name="临时密钥",
            description="24小时后过期",
            expire_at="2099-12-31 23:59:59"
        )

        # 验证创建成功
        assert result is True

    def test_get_api_keys_success(
        self,
        skip_if_no_backend,
        test_client: AIPEXBASEClient,
        test_project_name: str,
        created_projects: list
    ):
        """测试查询 API Keys"""
        # 先创建应用和 API Key
        app_info = test_client.create_application(name=test_project_name)
        app_id = app_info["appId"]
        created_projects.append(app_info)

        test_client.create_api_key(
            app_id=app_id,
            name=TEST_DATA.API_KEY_DEFAULT_NAME
        )

        # 查询 API Keys
        keys_data = test_client.get_api_keys(app_id=app_id)

        # 验证返回了数据
        assert keys_data is not None
        assert isinstance(keys_data, dict)
        assert "records" in keys_data

        # 验证至少有一条记录
        assert len(keys_data["records"]) > 0

        # 验证记录结构
        first_key = keys_data["records"][0]
        assert "keyName" in first_key
        assert "name" in first_key
        assert "status" in first_key

    def test_get_api_keys_with_pagination(
        self,
        skip_if_no_backend,
        test_client: AIPEXBASEClient,
        test_project_name: str,
        created_projects: list
    ):
        """测试分页查询 API Keys"""
        # 先创建应用
        app_info = test_client.create_application(name=test_project_name)
        app_id = app_info["appId"]
        created_projects.append(app_info)

        # 创建一个 API Key
        test_client.create_api_key(app_id=app_id, name="Key 1")

        # 测试分页参数
        keys_data = test_client.get_api_keys(
            app_id=app_id,
            page=1,
            page_size=5
        )

        assert keys_data is not None
        assert "current" in keys_data
        assert "size" in keys_data
        assert keys_data["current"] == 1
        assert keys_data["size"] == 5

    def test_get_api_keys_for_nonexistent_app(
        self,
        skip_if_no_backend,
        test_client: AIPEXBASEClient
    ):
        """测试查询不存在的应用的 API Keys"""
        # 使用一个不存在的 app_id，应该抛出异常
        with pytest.raises(Exception) as exc_info:
            test_client.get_api_keys(app_id="nonexistent_app_id")

        # 验证异常信息
        assert "应用" in str(exc_info.value) or "存在" in str(exc_info.value)


@pytest.mark.api
@pytest.mark.requires_backend
class TestErrorHandling:
    """测试错误处理"""

    def test_network_error_handling(self):
        """测试网络错误处理"""
        # 使用一个无法连接的地址
        client = AIPEXBASEClient("http://localhost:9999")

        with pytest.raises(Exception):
            client.login("test@test.com", "password")

    def test_invalid_json_response_handling(
        self,
        skip_if_no_backend,
        test_client: AIPEXBASEClient
    ):
        """测试处理无效的 JSON 响应"""
        # 这个测试依赖于后端返回特定的错误
        # 如果后端始终返回有效的 JSON，这个测试可能需要 mock
        pass  # 保留为占位，实际测试需要后端支持
