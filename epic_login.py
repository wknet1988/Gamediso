"""Epic Games 账密登录（邮箱 + 密码 + 两步验证）

流程与 Heroic / legendary 的网页登录一致：
    csrf -> reputation（验证码风控检测）-> login（邮箱密码）-> mfa（两步验证）-> exchange（换取一次性授权码）
成功后由 blueprints/epic.py 调用 `legendary auth --token <授权码>` 完成认证并落盘。

安全说明：
    - 密码仅用于向 Epic 官方登录接口发起请求，不写入任何文件、不记录日志；
    - 登录过程中的 Cookie 只保存在内存中，成功 / 失败 / 取消后立即清除；
    - 登录会话 10 分钟未完成自动过期。

实现说明：
    使用标准库 urllib 而非 requests —— 部分内置 Python 环境的 requests/urllib3
    存在版本兼容问题（带 body 的 POST 会报 _EventBundle 错误），标准库最稳妥。
"""

import http.cookiejar
import json
import secrets
import ssl
import threading
import time
import urllib.error
import urllib.parse
import urllib.request

EPIC_WEB_BASE = "https://www.epicgames.com"
SESSION_TTL = 600  # 登录会话有效期（秒）

_USER_AGENT = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
               "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")

_sessions = {}
_lock = threading.Lock()


class NetworkError(Exception):
    pass


def _cleanup_expired():
    now = time.time()
    with _lock:
        for key in [k for k, v in _sessions.items() if now - v["created"] > SESSION_TTL]:
            _sessions.pop(key, None)


def _drop(login_id):
    if not login_id:
        return
    with _lock:
        entry = _sessions.pop(login_id, None)
    if entry:
        try:
            entry["opener"].handlers = []
        except Exception:
            pass


def _new_opener():
    jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(jar),
        urllib.request.HTTPSHandler(context=ssl.create_default_context()),
    )
    return opener, jar


def _cookie(jar, name):
    for c in jar:
        if c.name == name:
            return c.value
    return None


def _request(opener, method, url, headers=None, data=None, timeout=20):
    """发起请求，返回 (status_code, body_bytes)"""
    body = None
    req_headers = {"User-Agent": _USER_AGENT, "Accept": "application/json"}
    if headers:
        req_headers.update(headers)
    if data is not None:
        body = urllib.parse.urlencode(data).encode("utf-8")
        req_headers.setdefault("Content-Type", "application/x-www-form-urlencoded")
    req = urllib.request.Request(url, data=body, headers=req_headers, method=method)
    try:
        with opener.open(req, timeout=timeout) as resp:
            return resp.status, resp.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()
    except Exception as e:
        raise NetworkError(str(e))


def _json(raw):
    try:
        return json.loads(raw.decode("utf-8", "replace"))
    except Exception:
        return {}


def _xsrf(opener, jar):
    """获取 / 刷新 XSRF-TOKEN"""
    try:
        _request(opener, "GET", f"{EPIC_WEB_BASE}/id/api/csrf", timeout=15)
    except NetworkError:
        return None
    return _cookie(jar, "XSRF-TOKEN")


def _error_info(raw):
    """从 Epic 错误响应中提取 errorCode / errorMessage"""
    data = _json(raw)
    if isinstance(data, dict):
        return data.get("errorCode"), (data.get("errorMessage") or data.get("message"))
    return None, None


def _mfa_method(raw):
    data = _json(raw)
    if isinstance(data, dict):
        return data.get("metadata", {}).get("twoFactorMethod") or "authenticator"
    return "authenticator"


def _exchange_code(opener, jar):
    """登录成功后获取一次性 exchange code（legendary auth --token 所需）"""
    xsrf = _xsrf(opener, jar)
    if not xsrf:
        return None
    headers = {"x-xsrf-token": xsrf}
    for method, url in (("GET", f"{EPIC_WEB_BASE}/id/api/exchange"),
                        ("POST", f"{EPIC_WEB_BASE}/id/api/exchange/generate")):
        try:
            status, raw = _request(opener, method, url, headers=headers, timeout=15)
            if status == 200:
                code = _json(raw).get("code")
                if code:
                    return code
        except NetworkError:
            continue
    return None


def start_password_login(email, password):
    """第一步：使用邮箱 + 密码登录 Epic。

    返回:
        {"success": True, "exchange_code": "..."}                 登录完成
        {"mfa_required": True, "login_id": "...", "method": "..."} 需要两步验证
        {"success": False, "error": "<错误码>"}                    登录失败
    """
    _cleanup_expired()
    opener, jar = _new_opener()

    xsrf = _xsrf(opener, jar)
    if not xsrf:
        return {"success": False, "error": "network_error"}

    # 验证码风控检测：被判定需要验证码时无法走账密流程，引导使用授权码方式
    try:
        status, raw = _request(opener, "GET", f"{EPIC_WEB_BASE}/id/api/reputation",
                               headers={"x-xsrf-token": xsrf}, timeout=15)
        if status == 200:
            verdict = _json(raw).get("verdict")
            if verdict is not None and verdict != "allow":
                return {"success": False, "error": "captcha_required"}
    except NetworkError:
        pass  # 该接口异常时不阻塞，继续尝试登录，以登录接口返回的错误为准

    try:
        status, raw = _request(opener, "POST", f"{EPIC_WEB_BASE}/id/api/login",
                               headers={"x-xsrf-token": xsrf},
                               data={"email": email, "password": password,
                                     "rememberMe": "true", "captcha": ""},
                               timeout=25)
    except NetworkError:
        return {"success": False, "error": "network_error"}

    if status == 200:
        code = _exchange_code(opener, jar)
        if not code:
            return {"success": False, "error": "exchange_failed"}
        return {"success": True, "exchange_code": code}

    error_code, error_message = _error_info(raw)
    if (error_code == "errors.com.epicgames.common.two_factor_authentication.required"
            or status == 431):
        login_id = secrets.token_hex(16)
        _xsrf(opener, jar)  # mfa 提交前刷新 csrf
        with _lock:
            _sessions[login_id] = {
                "opener": opener,
                "jar": jar,
                "created": time.time(),
                "method": _mfa_method(raw),
            }
        return {"mfa_required": True, "login_id": login_id,
                "method": _mfa_method(raw)}

    if error_code == "errors.com.epicgames.account.invalid_account_credentials":
        return {"success": False, "error": "invalid_credentials"}
    if status == 429:
        return {"success": False, "error": "rate_limited"}
    if "captcha" in (error_code or "").lower():
        return {"success": False, "error": "captcha_required"}

    return {"success": False, "error": "login_failed",
            "detail": error_message or error_code}


def submit_mfa_code(login_id, code):
    """第二步：提交两步验证码"""
    with _lock:
        entry = _sessions.get(login_id)
    if not entry:
        return {"success": False, "error": "session_expired"}
    opener, jar = entry["opener"], entry["jar"]
    method = entry.get("method", "authenticator")

    xsrf = _xsrf(opener, jar)
    if not xsrf:
        _drop(login_id)
        return {"success": False, "error": "network_error"}

    try:
        status, raw = _request(opener, "POST", f"{EPIC_WEB_BASE}/id/api/login/mfa",
                               headers={"x-xsrf-token": xsrf},
                               data={"code": code, "method": method,
                                     "rememberDevice": "false"},
                               timeout=25)
    except NetworkError:
        _drop(login_id)
        return {"success": False, "error": "network_error"}

    if status == 200:
        exchange = _exchange_code(opener, jar)
        _drop(login_id)
        if not exchange:
            return {"success": False, "error": "exchange_failed"}
        return {"success": True, "exchange_code": exchange}

    error_code, error_message = _error_info(raw)
    if error_code in ("errors.com.epicgames.accountportal.mfa_code_invalid",
                      "errors.com.epicgames.accountportal.validation"):
        # 验证码错误时保留会话，允许用户重新输入
        return {"success": False, "error": "mfa_invalid"}
    _drop(login_id)
    return {"success": False, "error": "mfa_failed",
            "detail": error_message or error_code}


def cancel_login(login_id):
    """取消登录并清除服务端会话"""
    _drop(login_id)
    return {"success": True}
