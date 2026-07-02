from __future__ import annotations
import base64, hashlib, hmac, json, re
from datetime import datetime, timedelta, timezone
from typing import Any

SECRET_PATTERNS = [re.compile(r"sk-[A-Za-z0-9_\-]{12,}"), re.compile(r"AKIA[0-9A-Z]{16}"), re.compile(r"(?i)(password|secret|token|api[_-]?key)\s*[:=]\s*[^\s,;]+")]
PII_PATTERNS = [re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"), re.compile(r"\+?\d[\d\s().-]{8,}\d")]
PROMPT_INJECTION_PATTERNS = [re.compile(r"(?i)ignore (all )?(previous|prior|above) instructions"), re.compile(r"(?i)system prompt"), re.compile(r"(?i)developer message"), re.compile(r"(?i)exfiltrate|leak|bypass approval|unauthorized tool"), re.compile(r"(?i)send payment without approval|skip reviewer|do not log")]

def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()

def _unb64(data: str) -> bytes:
    return base64.urlsafe_b64decode((data + "=" * (-len(data) % 4)).encode())

def hash_password(password: str) -> str:
    return hashlib.pbkdf2_hmac("sha256", password.encode(), b"workflowops-demo-salt", 120_000).hex()

def verify_password(password: str, hashed: str) -> bool:
    return hmac.compare_digest(hash_password(password), hashed) or hmac.compare_digest(hashlib.sha256(password.encode()).hexdigest(), hashed)

def create_access_token(subject: str, role: str, organization_id: str, secret: str, minutes: int = 1440) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {"sub": subject, "role": role, "organization_id": organization_id, "exp": int((datetime.now(timezone.utc) + timedelta(minutes=minutes)).timestamp())}
    signing_input = f"{_b64(json.dumps(header, separators=(',', ':')).encode())}.{_b64(json.dumps(payload, separators=(',', ':')).encode())}"
    sig = hmac.new(secret.encode(), signing_input.encode(), hashlib.sha256).digest()
    return f"{signing_input}.{_b64(sig)}"

def verify_access_token(token: str, secret: str) -> dict[str, Any]:
    try:
        signing_input, sig = token.rsplit(".", 1)
        expected = _b64(hmac.new(secret.encode(), signing_input.encode(), hashlib.sha256).digest())
        if not hmac.compare_digest(sig, expected):
            raise ValueError("Invalid token signature")
        payload = json.loads(_unb64(signing_input.split(".")[1]))
        if int(payload["exp"]) < int(datetime.now(timezone.utc).timestamp()):
            raise ValueError("Token expired")
        return payload
    except Exception as exc:
        raise ValueError("Invalid token") from exc

def create_demo_token(subject: str, role: str, secret: str = "change-me-in-production") -> str:
    return create_access_token(subject, role, "demo-org", secret)

def verify_demo_token(token: str, secret: str = "change-me-in-production") -> dict[str, Any]:
    return verify_access_token(token, secret)

def redact_text(text: str) -> str:
    redacted = text or ""
    for pattern in SECRET_PATTERNS + PII_PATTERNS:
        redacted = pattern.sub("[REDACTED]", redacted)
    return redacted

def detect_prompt_injection(text: str) -> list[str]:
    return [p.pattern for p in PROMPT_INJECTION_PATTERNS if p.search(text or "")]

def is_allowed_tool(tool_name: str, allowed_tools: set[str]) -> bool:
    return tool_name in allowed_tools

ALLOWED_EXTERNAL_ACTIONS = {"create_task", "request_approval", "generate_report", "export_data_stub", "notify_user_stub"}
