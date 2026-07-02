from __future__ import annotations
from enum import StrEnum
class Role(StrEnum):
    ADMIN="admin"; AUTOMATION_MANAGER="automation_manager"; REVIEWER="reviewer"; VIEWER="viewer"
PERMISSIONS={Role.ADMIN:{"*"},Role.AUTOMATION_MANAGER:{"workflow:create","workflow:read","workflow:run","workflow:stop","workflow:replay","workflow:enqueue","workflow:resume","template:write","document:upload","document:read","task:assign","approval:request","approval:read","report:read","report:export","audit:read","reliability:run","reliability:read","connector:read","connector:test","connector:dry_run","policy:read","settings:read","queue:read"},Role.REVIEWER:{"workflow:read","approval:read","approval:decide","task:read","document:read","report:read","audit:read","reliability:read","connector:read","policy:read","queue:read"},Role.VIEWER:{"workflow:read","task:read","document:read","report:read","audit:read","reliability:read","connector:read","policy:read"}}
def has_permission(role:str,permission:str)->bool:
    try: allowed=PERMISSIONS[Role(role)]
    except ValueError: return False
    return "*" in allowed or permission in allowed
def require_permission(role:str,permission:str)->None:
    if not has_permission(role,permission): raise PermissionError(f"Role {role!r} cannot perform {permission!r}")
