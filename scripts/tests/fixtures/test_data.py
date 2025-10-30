"""
测试数据定义

包含测试中使用的各种数据模板和预期响应。
"""
from typing import Dict, Any


class TestData:
    """测试数据集合"""

    # ============================================
    # 项目和应用相关
    # ============================================

    @staticmethod
    def get_project_name(suffix: str = "") -> str:
        """生成测试项目名称"""
        import time
        timestamp = int(time.time())
        if suffix:
            return f"test_project_{suffix}_{timestamp}"
        return f"test_project_{timestamp}"

    @staticmethod
    def get_application_data(name: str = None, description: str = None) -> Dict[str, str]:
        """生成应用创建数据"""
        if name is None:
            name = TestData.get_project_name()
        if description is None:
            description = f"测试应用：{name}"

        return {
            "name": name,
            "appName": name,
            "description": description
        }

    # ============================================
    # API Key 相关
    # ============================================

    API_KEY_DEFAULT_NAME = "MCP 专用密钥"
    API_KEY_DEFAULT_DESCRIPTION = "由测试自动生成的 API Key"

    @staticmethod
    def get_api_key_data(
        name: str = None,
        description: str = None,
        expire_at: str = None
    ) -> Dict[str, Any]:
        """生成 API Key 创建数据"""
        data = {
            "name": name or TestData.API_KEY_DEFAULT_NAME,
            "description": description or TestData.API_KEY_DEFAULT_DESCRIPTION
        }
        if expire_at:
            data["expireAt"] = expire_at
        return data

    # ============================================
    # 预期的 API 响应结构
    # ============================================

    @staticmethod
    def expected_login_response() -> Dict[str, Any]:
        """登录成功的预期响应结构"""
        return {
            "code": 0,
            "data": "jwt_token_placeholder",
            "message": "success"
        }

    @staticmethod
    def expected_create_app_response(app_id: str = "app_test_123") -> Dict[str, Any]:
        """创建应用成功的预期响应结构"""
        return {
            "code": 0,
            "data": {
                "appId": app_id,
                "appName": "测试应用",
                "status": "active",
                "createdAt": "2024-01-01 12:00:00"
            },
            "message": "success"
        }

    @staticmethod
    def expected_create_api_key_response(success: bool = True) -> Dict[str, Any]:
        """创建 API Key 的预期响应结构"""
        return {
            "code": 0,
            "data": success,
            "message": "success" if success else "创建失败"
        }

    @staticmethod
    def expected_get_api_keys_response(
        key_name: str = "ak_test_123",
        has_records: bool = True
    ) -> Dict[str, Any]:
        """查询 API Keys 的预期响应结构"""
        if has_records:
            return {
                "code": 0,
                "data": {
                    "records": [
                        {
                            "keyName": key_name,
                            "name": TestData.API_KEY_DEFAULT_NAME,
                            "description": TestData.API_KEY_DEFAULT_DESCRIPTION,
                            "status": "active",
                            "expireAt": "2099-12-31 23:59:59",
                            "createdAt": "2024-01-01 12:00:00"
                        }
                    ],
                    "total": 1,
                    "current": 1,
                    "size": 10
                },
                "message": "success"
            }
        else:
            return {
                "code": 0,
                "data": {
                    "records": [],
                    "total": 0,
                    "current": 1,
                    "size": 10
                },
                "message": "success"
            }

    # ============================================
    # 错误响应
    # ============================================

    @staticmethod
    def error_response(code: int = 400, message: str = "业务错误") -> Dict[str, Any]:
        """业务错误响应"""
        return {
            "code": code,
            "data": None,
            "message": message
        }

    @staticmethod
    def auth_error_response() -> Dict[str, Any]:
        """认证失败响应"""
        return TestData.error_response(401, "认证失败，请检查邮箱和密码")

    @staticmethod
    def duplicate_name_error_response() -> Dict[str, Any]:
        """应用名称重复错误"""
        return TestData.error_response(400, "应用名称已存在")

    # ============================================
    # MCP 配置相关
    # ============================================

    @staticmethod
    def expected_mcp_config(
        base_url: str = "http://localhost:8080",
        api_key: str = "ak_test_123",
        server_name: str = "baas-mcp-server"
    ) -> Dict[str, Any]:
        """预期的 MCP 配置结构"""
        return {
            "mcpServers": {
                server_name: {
                    "url": f"{base_url}/mcp/sse?token={api_key}"
                }
            }
        }

    # ============================================
    # URL 测试数据
    # ============================================

    URL_TEST_CASES = [
        ("http://localhost:8080/baas-api", "http://localhost:8080"),
        ("http://localhost:8080/baas-api/", "http://localhost:8080"),
        ("http://localhost:8080", "http://localhost:8080"),
        ("http://localhost:8080/", "http://localhost:8080"),
        ("http://example.com:8080/baas-api", "http://example.com:8080"),
        ("http://example.com/other", "http://example.com/other"),
    ]

    # ============================================
    # 环境配置测试数据
    # ============================================

    @staticmethod
    def valid_env_config() -> Dict[str, str]:
        """有效的环境配置"""
        return {
            "AIPEXBASE_BASE_URL": "http://localhost:8080",
            "AIPEXBASE_ADMIN_EMAIL": "admin@test.com",
            "AIPEXBASE_ADMIN_PASSWORD": "testpassword",
            "AIPEXBASE_API_KEY_NAME": "Test Key",
            "AIPEXBASE_VERBOSE": "false"
        }

    @staticmethod
    def incomplete_env_config() -> Dict[str, str]:
        """不完整的环境配置（缺少必需字段）"""
        return {
            "AIPEXBASE_BASE_URL": "http://localhost:8080"
            # 缺少 email 和 password
        }


# 常用测试数据实例
TEST_DATA = TestData()
