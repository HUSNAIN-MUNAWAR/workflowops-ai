from app.core.rbac import has_permission, require_permission
import pytest


def test_rbac_admin_and_viewer():
    assert has_permission("admin", "anything")
    assert has_permission("viewer", "report:read")
    assert not has_permission("viewer", "workflow:stop")


def test_rbac_require_denies():
    with pytest.raises(PermissionError):
        require_permission("viewer", "workflow:stop")
