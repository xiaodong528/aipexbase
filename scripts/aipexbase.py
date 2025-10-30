#!/usr/bin/env python3
"""
AIPEXBASE 项目自动创建工具

可以作为命令行脚本运行，也可以作为 Python 模块导入使用。

=== 命令行使用 ===

1. 配置环境变量：
    cp .env.example .env
    # 编辑 .env 文件设置必要的配置项

2. 运行脚本：
    python aipexbase.py [项目名称] [项目描述]

示例：
    python aipexbase.py                          # 使用默认项目名称
    python aipexbase.py "我的项目"                # 指定项目名称
    python aipexbase.py "我的项目" "项目描述"      # 指定名称和描述

=== Python 模块使用 ===

导入：
    from scripts.aipexbase import (
        AIPEXBASEClient,          # 主客户端类
        create_client_from_env,   # 工厂函数：从环境变量创建客户端
        create_project,           # 便捷函数：快速创建项目
        ProjectCreationResult,    # 结果数据类
        AIPEXBASEError,           # 基础异常类
        AuthenticationError,      # 认证异常
        APIError,                 # API 异常
        ConfigurationError        # 配置异常
    )

方式 1: 使用便捷函数（最简单，推荐）
    result = create_project("我的项目", "项目描述")
    print(f"App ID: {result.app_id}")
    print(f"Token: {result.api_key}")
    print(f"MCP URL: {result.mcp_url}")

方式 2: 使用工厂函数创建客户端
    client = create_client_from_env()
    result = client.create_project_complete(
        project_name="我的项目",
        description="项目描述",
        api_key_name="生产环境密钥"
    )

方式 3: 完全自定义
    client = AIPEXBASEClient("http://server:8080")
    client.login("admin@example.com", "password")
    result = client.create_project_complete(
        project_name="我的项目",
        description="项目描述",
        api_key_expire="2025-12-31 23:59:59"
    )

集成到你的应用：
    from scripts.aipexbase import create_project, APIError

    try:
        result = create_project(f"user_{user_id}_project", "用户项目")

        # 保存到数据库
        save_to_db(user_id, {
            'app_id': result.app_id,
            'token': result.api_key,
            'mcp_url': result.mcp_url
        })

        return result.api_key
    except APIError as e:
        logger.error(f"创建项目失败: {e}")
        raise

=== 功能说明 ===

1. 从环境变量或 .env 文件读取配置
2. 自动登录获取 JWT token
3. 创建应用/项目
4. 生成 API Key (Token)
5. 构建 MCP 服务器配置
6. 返回结构化的结果数据类

=== 环境变量配置 ===

必填：
    AIPEXBASE_BASE_URL          - 服务器地址
    AIPEXBASE_ADMIN_EMAIL       - 管理员邮箱
    AIPEXBASE_ADMIN_PASSWORD    - 管理员密码

可选：
    AIPEXBASE_API_KEY_NAME      - API Key 名称（默认：MCP 专用密钥）
    AIPEXBASE_API_KEY_DESC      - API Key 描述
    AIPEXBASE_API_KEY_EXPIRE    - 过期时间（格式：YYYY-MM-DD HH:mm:ss）
    AIPEXBASE_OUTPUT_FILE       - 输出文件路径（默认：mcp_config.json）
    AIPEXBASE_VERBOSE           - 详细输出（默认：false）
"""

import sys
import os
import json
import argparse
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field

try:
    import requests
    from colorama import init, Fore, Style
    from dotenv import load_dotenv
except ImportError as e:
    print(f"错误: 缺少必要的依赖库 - {e}")
    print("请运行: pip install -r requirements.txt")
    sys.exit(1)

# 初始化 colorama
init(autoreset=True)


# ============================================================================
# 数据类定义
# ============================================================================

@dataclass
class ProjectCreationResult:
    """
    项目创建结果数据类

    Attributes:
        app_id: 应用ID
        app_name: 应用名称
        api_key: API Key (token)，用于 MCP 连接
        api_key_name: API Key 显示名称
        mcp_url: MCP 服务器连接 URL（完整的 SSE 端点）
        mcp_config: MCP 配置字典，可直接写入配置文件
        app_info: 完整的应用信息字典
        api_key_info: 完整的 API Key 信息字典

    Example:
        >>> result = client.create_project_complete("我的项目")
        >>> print(f"Token: {result.api_key}")
        >>> print(f"MCP URL: {result.mcp_url}")
    """
    app_id: str
    app_name: str
    api_key: str
    api_key_name: str
    mcp_url: str
    mcp_config: Dict[str, Any]
    app_info: Dict[str, Any] = field(repr=False)
    api_key_info: Dict[str, Any] = field(repr=False)


# ============================================================================
# 异常类定义
# ============================================================================

class AIPEXBASEError(Exception):
    """AIPEXBASE 基础异常类"""
    pass


class AuthenticationError(AIPEXBASEError):
    """认证失败异常"""
    pass


class APIError(AIPEXBASEError):
    """API 调用异常"""
    pass


class ConfigurationError(AIPEXBASEError):
    """配置错误异常"""
    pass


class AIPEXBASEClient:
    """AIPEXBASE API 客户端"""

    def __init__(self, base_url: str):
        """
        初始化客户端

        Args:
            base_url: AIPEXBASE 服务器地址
        """
        self.base_url = base_url.rstrip('/')
        self.token: Optional[str] = None
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        require_auth: bool = False
    ) -> Dict[str, Any]:
        """
        发送 HTTP 请求

        Args:
            method: HTTP 方法 (GET/POST/DELETE)
            endpoint: API 端点
            data: 请求数据
            require_auth: 是否需要认证

        Returns:
            响应 JSON 数据

        Raises:
            Exception: 请求失败时抛出异常
        """
        url = f"{self.base_url}{endpoint}"
        headers = {}

        if require_auth and self.token:
            headers['Authorization'] = f'Bearer {self.token}'

        try:
            if method.upper() == 'GET':
                response = self.session.get(url, headers=headers, timeout=30)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data, headers=headers, timeout=30)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url, headers=headers, timeout=30)
            else:
                raise ValueError(f"不支持的 HTTP 方法: {method}")

            response.raise_for_status()
            result = response.json()

            # 检查业务状态码
            if result.get('code') != 0:
                error_msg = result.get('message', '未知错误')
                raise Exception(f"API 错误: {error_msg}")

            return result

        except requests.exceptions.Timeout:
            raise Exception(f"请求超时: {url}")
        except requests.exceptions.ConnectionError:
            raise Exception(f"连接失败: 无法连接到 {self.base_url}")
        except requests.exceptions.HTTPError as e:
            raise Exception(f"HTTP 错误 {e.response.status_code}: {e.response.text}")
        except json.JSONDecodeError:
            raise Exception("服务器返回了无效的 JSON 响应")

    def login(self, email: str, password: str) -> str:
        """
        管理员登录

        Args:
            email: 管理员邮箱
            password: 管理员密码

        Returns:
            JWT token
        """
        print(f"{Fore.CYAN}→ 正在登录...")

        data = {
            'email': email,
            'password': password
        }

        result = self._make_request('POST', '/admin/login', data)
        self.token = result.get('data')

        if not self.token:
            raise Exception("登录失败: 未返回 token")

        print(f"{Fore.GREEN}✓ 登录成功")
        return self.token

    def create_application(self, name: str, description: str = '') -> Dict[str, Any]:
        """
        创建应用

        Args:
            name: 应用名称
            description: 应用描述

        Returns:
            应用信息 (包含 appId)
        """
        print(f"{Fore.CYAN}→ 正在创建应用: {name}")

        data = {
            'name': name,
            'appName': name
        }

        if description:
            data['description'] = description

        result = self._make_request('POST', '/admin/application', data, require_auth=True)
        app_info = result.get('data')

        if not app_info or not app_info.get('appId'):
            raise Exception("创建应用失败: 未返回 appId")

        print(f"{Fore.GREEN}✓ 应用创建成功")
        print(f"  应用ID: {Fore.YELLOW}{app_info['appId']}")
        print(f"  应用名称: {app_info['appName']}")
        print(f"  状态: {app_info['status']}")

        return app_info

    def create_api_key(
        self,
        app_id: str,
        name: str,
        description: str = '',
        expire_at: str = ''
    ) -> bool:
        """
        创建 API Key

        Args:
            app_id: 应用ID
            name: API Key 名称
            description: API Key 描述
            expire_at: 过期时间 (格式: YYYY-MM-DD HH:mm:ss)

        Returns:
            是否创建成功
        """
        print(f"{Fore.CYAN}→ 正在生成 API Key...")

        data = {
            'name': name,
            'description': description,
            'expireAt': expire_at
        }

        endpoint = f'/admin/application/config/apikeys/{app_id}/save'
        result = self._make_request('POST', endpoint, data, require_auth=True)

        success = result.get('data', False)
        if not success:
            raise Exception("创建 API Key 失败")

        print(f"{Fore.GREEN}✓ API Key 生成成功")
        return True

    def get_api_keys(self, app_id: str, page: int = 1, page_size: int = 10) -> Dict[str, Any]:
        """
        查询 API Key 列表

        Args:
            app_id: 应用ID
            page: 页码
            page_size: 每页数量

        Returns:
            API Key 列表数据
        """
        print(f"{Fore.CYAN}→ 正在查询 API Key 详情...")

        data = {
            'current': page,
            'pageSize': page_size
        }

        endpoint = f'/admin/application/config/apikeys/{app_id}/page'
        result = self._make_request('POST', endpoint, data, require_auth=True)

        return result.get('data', {})

    def create_project_complete(
        self,
        project_name: str,
        description: str = '',
        api_key_name: str = 'MCP 专用密钥',
        api_key_description: str = '用于 MCP 工具调用的 API 密钥',
        api_key_expire: str = '',
        mcp_server_name: str = 'aipexbase-mcp-server',
        verbose: bool = True
    ) -> ProjectCreationResult:
        """
        完整的项目创建流程（一站式方法）

        包含：创建应用 → 生成 API Key → 查询 Key 详情 → 构建 MCP 配置

        Args:
            project_name: 项目名称
            description: 项目描述
            api_key_name: API Key 显示名称
            api_key_description: API Key 描述
            api_key_expire: API Key 过期时间（格式: YYYY-MM-DD HH:mm:ss）
            mcp_server_name: MCP 服务器名称
            verbose: 是否显示详细输出

        Returns:
            ProjectCreationResult: 项目创建结果数据类

        Raises:
            APIError: API 调用失败
            AuthenticationError: 未认证或认证过期

        Example:
            >>> client = AIPEXBASEClient("http://localhost:8080")
            >>> client.login("admin@example.com", "password")
            >>> result = client.create_project_complete("我的项目", "项目描述")
            >>> print(f"Token: {result.api_key}")
        """
        # 检查是否已登录
        if not self.token:
            raise AuthenticationError("未登录，请先调用 login() 方法")

        # 1. 创建应用
        if verbose:
            print()
        app_info = self.create_application(project_name, description)
        app_id = app_info['appId']

        # 2. 生成 API Key
        if verbose:
            print()
        self.create_api_key(
            app_id=app_id,
            name=api_key_name,
            description=api_key_description,
            expire_at=api_key_expire
        )

        # 3. 查询 API Key 详情
        if verbose:
            print()
        api_keys_data = self.get_api_keys(app_id)
        records = api_keys_data.get('records', [])

        if not records:
            raise APIError("未找到生成的 API Key")

        # 获取最新创建的 API Key
        latest_key = records[0]
        key_name = latest_key['keyName']

        if verbose:
            print(f"{Fore.GREEN}✓ API Key 查询成功")
            print(f"  Key 名称: {latest_key['name']}")
            print(f"  Key 值: {Fore.YELLOW}{key_name}")
            print(f"  状态: {latest_key['status']}")
            print(f"  过期时间: {latest_key['expireAt']}")

        # 4. 生成 MCP 配置
        mcp_base_url = get_mcp_base_url(self.base_url)
        mcp_url = f"{mcp_base_url}/mcp/sse?token={key_name}"
        mcp_config = {
            'mcpServers': {
                mcp_server_name: {
                    'url': mcp_url
                }
            }
        }

        # 5. 构建并返回结果
        return ProjectCreationResult(
            app_id=app_id,
            app_name=app_info['appName'],
            api_key=key_name,
            api_key_name=latest_key['name'],
            mcp_url=mcp_url,
            mcp_config=mcp_config,
            app_info=app_info,
            api_key_info=latest_key
        )


def load_env_config() -> Dict[str, Any]:
    """
    从环境变量加载配置

    优先从 .env 文件加载，如果不存在则使用系统环境变量

    Returns:
        配置字典

    Raises:
        ValueError: 缺少必要的环境变量时抛出
    """
    # 尝试加载 .env 文件
    env_file = Path(__file__).parent / '.env'
    if env_file.exists():
        load_dotenv(env_file)
        print(f"{Fore.CYAN}→ 已加载 .env 文件")
    else:
        print(f"{Fore.YELLOW}→ 未找到 .env 文件，使用系统环境变量")

    # 读取配置
    config = {
        'server': {
            'base_url': os.getenv('AIPEXBASE_BASE_URL', '')
        },
        'admin': {
            'email': os.getenv('AIPEXBASE_ADMIN_EMAIL', ''),
            'password': os.getenv('AIPEXBASE_ADMIN_PASSWORD', '')
        },
        'api_key': {
            'name': os.getenv('AIPEXBASE_API_KEY_NAME', 'MCP 专用密钥'),
            'description': os.getenv('AIPEXBASE_API_KEY_DESC', '用于 MCP 工具调用的 API 密钥'),
            'expire_at': os.getenv('AIPEXBASE_API_KEY_EXPIRE', '')
        },
        'output': {
            'mcp_config_file': os.getenv('AIPEXBASE_OUTPUT_FILE', 'mcp_config.json'),
            'show_full_response': os.getenv('AIPEXBASE_VERBOSE', 'false').lower() == 'true'
        }
    }

    # 验证必要的配置项
    required_fields = [
        ('server', 'base_url', 'AIPEXBASE_BASE_URL'),
        ('admin', 'email', 'AIPEXBASE_ADMIN_EMAIL'),
        ('admin', 'password', 'AIPEXBASE_ADMIN_PASSWORD')
    ]

    missing_fields = []
    for section, field, env_var in required_fields:
        if not config.get(section, {}).get(field):
            missing_fields.append(env_var)

    if missing_fields:
        raise ValueError(
            f"缺少必要的环境变量: {', '.join(missing_fields)}\n"
            f"请创建 .env 文件或设置环境变量（参考 .env.example）"
        )

    return config


def get_mcp_base_url(base_url: str) -> str:
    """
    从 base_url 中提取 MCP 基础 URL（去掉 /baas-api 等 API 前缀）

    Args:
        base_url: 完整的 API base URL，如 http://host:port/baas-api

    Returns:
        MCP 基础 URL，如 http://host:port
    """
    base_url = base_url.rstrip('/')
    # 去掉 /baas-api 后缀
    if base_url.endswith('/baas-api'):
        return base_url[:-9]
    return base_url


def generate_mcp_config(base_url: str, api_key: str, server_name: str = 'aipexbase-mcp-server') -> Dict[str, Any]:
    """
    生成 MCP 服务器配置

    Args:
        base_url: 服务器地址
        api_key: API Key (keyName)
        server_name: MCP 服务器名称

    Returns:
        MCP 配置字典
    """
    mcp_base_url = get_mcp_base_url(base_url)
    mcp_url = f"{mcp_base_url}/mcp/sse?token={api_key}"

    return {
        'mcpServers': {
            server_name: {
                'url': mcp_url
            }
        }
    }


# ============================================================================
# 便捷 API 函数
# ============================================================================

def create_client_from_env(env_file: Optional[str] = None, auto_login: bool = True) -> AIPEXBASEClient:
    """
    从环境变量创建客户端并自动登录

    优先从 .env 文件加载，如果不存在则使用系统环境变量。

    Args:
        env_file: .env 文件路径（可选，默认为脚本目录下的 .env）
        auto_login: 是否自动登录（默认 True）

    Returns:
        AIPEXBASEClient: 已登录的客户端实例

    Raises:
        ConfigurationError: 缺少必要的环境变量
        AuthenticationError: 登录失败

    Example:
        >>> client = create_client_from_env()
        >>> result = client.create_project_complete("我的项目")
    """
    # 加载环境变量
    if env_file:
        env_path = Path(env_file)
    else:
        env_path = Path(__file__).parent / '.env'

    if env_path.exists():
        load_dotenv(env_path)

    # 读取配置
    base_url = os.getenv('AIPEXBASE_BASE_URL', '')
    email = os.getenv('AIPEXBASE_ADMIN_EMAIL', '')
    password = os.getenv('AIPEXBASE_ADMIN_PASSWORD', '')

    # 验证必要配置
    missing = []
    if not base_url:
        missing.append('AIPEXBASE_BASE_URL')
    if not email:
        missing.append('AIPEXBASE_ADMIN_EMAIL')
    if not password:
        missing.append('AIPEXBASE_ADMIN_PASSWORD')

    if missing:
        raise ConfigurationError(
            f"缺少必要的环境变量: {', '.join(missing)}\n"
            f"请创建 .env 文件或设置环境变量（参考 .env.example）"
        )

    # 创建客户端
    client = AIPEXBASEClient(base_url)

    # 自动登录
    if auto_login:
        try:
            client.login(email, password)
        except Exception as e:
            raise AuthenticationError(f"登录失败: {e}")

    return client


def create_project(
    project_name: str,
    description: str = '',
    config: Optional[Dict[str, Any]] = None,
    **kwargs
) -> ProjectCreationResult:
    """
    便捷函数：快速创建项目

    自动从环境变量创建客户端、登录并创建项目。

    Args:
        project_name: 项目名称
        description: 项目描述
        config: 配置字典（可选，用于覆盖环境变量配置）
        **kwargs: 传递给 create_project_complete 的其他参数

    Returns:
        ProjectCreationResult: 项目创建结果

    Raises:
        ConfigurationError: 配置错误
        AuthenticationError: 认证失败
        APIError: API 调用失败

    Example:
        >>> # 最简单的用法（从 .env 读取配置）
        >>> result = create_project("我的项目", "项目描述")
        >>> print(f"Token: {result.api_key}")

        >>> # 自定义配置
        >>> result = create_project(
        ...     "我的项目",
        ...     api_key_name="生产环境密钥",
        ...     api_key_expire="2025-12-31 23:59:59"
        ... )
    """
    # 创建客户端并登录
    client = create_client_from_env()

    # 从环境变量或配置读取 API Key 配置
    if config is None:
        config = {}

    api_key_config = {
        'api_key_name': kwargs.pop('api_key_name', os.getenv('AIPEXBASE_API_KEY_NAME', 'MCP 专用密钥')),
        'api_key_description': kwargs.pop('api_key_description', os.getenv('AIPEXBASE_API_KEY_DESC', '用于 MCP 工具调用的 API 密钥')),
        'api_key_expire': kwargs.pop('api_key_expire', os.getenv('AIPEXBASE_API_KEY_EXPIRE', '')),
        'mcp_server_name': kwargs.pop('mcp_server_name', 'aipexbase-mcp-server'),
        'verbose': kwargs.pop('verbose', os.getenv('AIPEXBASE_VERBOSE', 'false').lower() == 'true')
    }

    # 创建项目
    return client.create_project_complete(
        project_name=project_name,
        description=description,
        **api_key_config,
        **kwargs
    )


def main():
    """命令行入口（向后兼容）"""
    parser = argparse.ArgumentParser(
        description='AIPEXBASE 项目自动创建脚本',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        'project_name',
        nargs='?',
        default=None,
        help='项目名称 (可选，默认: AI项目_时间戳)'
    )
    parser.add_argument(
        'description',
        nargs='?',
        default='',
        help='项目描述 (可选)'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='显示详细输出'
    )

    args = parser.parse_args()

    # 生成默认项目名称（如果未提供）
    if not args.project_name:
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        project_name = f"AI项目_{timestamp}"
        print(f"{Fore.YELLOW}→ 未指定项目名称，使用默认值: {project_name}\n")
    else:
        project_name = args.project_name

    description = args.description or ''

    print(f"{Fore.CYAN}{Style.BRIGHT}=== AIPEXBASE 项目自动创建工具 ==={Style.RESET_ALL}\n")

    try:
        # 1. 加载配置
        config = load_env_config()
        print(f"{Fore.GREEN}✓ 配置加载成功\n")

        # 2. 创建客户端并登录（使用新 API）
        client = create_client_from_env()
        print()

        # 3. 创建项目（使用新的高级 API）
        api_key_config = config.get('api_key', {})
        result = client.create_project_complete(
            project_name=project_name,
            description=description,
            api_key_name=api_key_config.get('name', 'MCP 专用密钥'),
            api_key_description=api_key_config.get('description', '用于 MCP 工具调用的 API 密钥'),
            api_key_expire=api_key_config.get('expire_at', ''),
            verbose=True
        )
        print()

        # 4. 保存 MCP 配置文件
        output_config = config.get('output', {})
        output_filename = output_config.get('mcp_config_file', 'mcp_config.json')

        # 确保保存到脚本所在目录
        script_dir = Path(__file__).parent
        output_file = script_dir / output_filename

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result.mcp_config, f, indent=2, ensure_ascii=False)

        print(f"{Fore.GREEN}✓ MCP 配置已保存到: {Fore.YELLOW}{output_file}\n")

        # 5. 输出配置内容
        print(f"{Fore.CYAN}{Style.BRIGHT}=== MCP 服务器配置 ==={Style.RESET_ALL}")
        print(json.dumps(result.mcp_config, indent=2, ensure_ascii=False))
        print()

        print(f"{Fore.GREEN}{Style.BRIGHT}✓ 所有操作完成！{Style.RESET_ALL}")
        print(f"\n{Fore.CYAN}下一步操作:")
        print(f"  1. 将 {output_file} 中的配置添加到你的 AI IDE 的 MCP 配置中")
        print(f"  2. 重启 AI IDE 以加载 MCP 服务器")
        print(f"  3. 现在你可以使用 MCP 工具操作 AIPEXBASE 了！")

    except ConfigurationError as e:
        print(f"{Fore.RED}✗ 配置错误: {e}")
        sys.exit(1)
    except AuthenticationError as e:
        print(f"{Fore.RED}✗ 认证错误: {e}")
        sys.exit(1)
    except APIError as e:
        print(f"{Fore.RED}✗ API 错误: {e}")
        sys.exit(1)
    except FileNotFoundError as e:
        print(f"{Fore.RED}✗ 文件错误: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"{Fore.RED}✗ 错误: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
