import pytest
from unittest.mock import MagicMock, patch
from jose import JWTError
from fastapi import UploadFile

from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.services.share_service import ShareService
from app.services.org_service import OrganizationService
from app.services.artifact_service import ArtifactService


# =====================================================
# AUTH SERVICE
# =====================================================

def test_login_success():
    db = MagicMock()
    service = AuthService(db)

    user = MagicMock(id="u1", password_hash="hash")

    service.user_repo = MagicMock()
    service.role_repo = MagicMock()
    service.refresh_repo = MagicMock()
    service.audit_repo = MagicMock()

    service.user_repo.get_by_email.return_value = user
    service.role_repo.get_roles_for_user.return_value = [MagicMock(role="admin")]

    with patch("app.services.auth_service.verify_password", return_value=True), \
         patch("app.services.auth_service.resolve_permissions", return_value=["*"]), \
         patch("app.services.auth_service.create_access_token", return_value="access"), \
         patch("app.services.auth_service.create_refresh_token", return_value=("refresh", "exp")), \
         patch("app.services.auth_service.hash_refresh_token", return_value="hash"):

        access, refresh = service.login("a@b.com", "pwd")
        assert access == "access"
        assert refresh == "refresh"


def test_login_invalid_user():
    service = AuthService(MagicMock())
    service.user_repo = MagicMock()
    service.user_repo.get_by_email.return_value = None

    with pytest.raises(ValueError):
        service.login("x@y.com", "pwd")


def test_refresh_invalid_token():
    service = AuthService(MagicMock())

    with patch("app.services.auth_service.decode_token", side_effect=JWTError()):
        with pytest.raises(ValueError):
            service.refresh("bad-token")


def test_logout():
    service = AuthService(MagicMock())
    service.refresh_repo = MagicMock()
    service.audit_repo = MagicMock()

    service.logout("u1")
    service.refresh_repo.revoke_all_for_user.assert_called_once()


# =====================================================
# USER SERVICE
# =====================================================

def test_list_users_superadmin():
    service = UserService(MagicMock())
    service.user_repo = MagicMock()

    service.user_repo.get_all_with_roles.return_value = ["users"]

    actor = {"permissions": ["*"]}
    assert service.list_users(actor) == ["users"]


def test_list_users_admin():
    service = UserService(MagicMock())
    service.user_repo = MagicMock()

    service.user_repo.get_users_by_org_with_roles.return_value = ["org-users"]

    actor = {"permissions": [], "org_id": "o1"}
    assert service.list_users(actor) == ["org-users"]


def test_assign_user_cross_org_denied():
    service = UserService(MagicMock())

    actor = {"permissions": [], "org_id": "o1"}
    with pytest.raises(ValueError):
        service.assign_user_to_org("u1", "o2", "admin", actor)


def test_assign_user_success():
    service = UserService(MagicMock())
    service.role_repo = MagicMock()
    service.audit = MagicMock()

    mapping = MagicMock(id="m1")
    service.role_repo.assign.return_value = mapping

    actor = {"permissions": ["*"], "id": "admin"}
    result = service.assign_user_to_org("u1", "o1", "admin", actor)
    assert result == mapping


def test_get_user_permissions():
    service = UserService(MagicMock())
    service.role_repo = MagicMock()

    role = MagicMock(role="admin", org_id="o1")
    service.role_repo.get_roles_for_user.return_value = [role]

    perms = service.get_user_permissions("u1", {"permissions": ["*"]})
    assert isinstance(perms, list)


# =====================================================
# SHARE SERVICE
# =====================================================

def test_create_share_success():
    service = ShareService(MagicMock())
    service.artifact_repo = MagicMock()
    service.share_repo = MagicMock()
    service.audit = MagicMock()

    artifact = MagicMock(id="a1", org_id="o1")
    service.artifact_repo.get_by_id.return_value = artifact
    service.share_repo.create.return_value = MagicMock(id="s1")

    share = service.create_share("a1", "u1", 10)
    assert share.id == "s1"


def test_create_share_artifact_not_found():
    service = ShareService(MagicMock())
    service.artifact_repo = MagicMock()
    service.artifact_repo.get_by_id.return_value = None

    with pytest.raises(ValueError):
        service.create_share("a1", "u1", 10)


def test_access_share_success():
    service = ShareService(MagicMock())
    service.share_repo = MagicMock()
    service.artifact_repo = MagicMock()
    service.audit = MagicMock()

    share = MagicMock(id="s1", artifact_id="a1")
    artifact = MagicMock(id="a1", org_id="o1")

    service.share_repo.get_valid_share.return_value = share
    service.artifact_repo.get_by_id.return_value = artifact

    result = service.access_share("s1")
    assert result == artifact


def test_access_share_invalid():
    service = ShareService(MagicMock())
    service.share_repo = MagicMock()
    service.share_repo.get_valid_share.return_value = None

    with pytest.raises(ValueError):
        service.access_share("s1")


# =====================================================
# ORG SERVICE
# =====================================================

def test_create_org():
    service = OrganizationService(MagicMock())
    service.repo = MagicMock()
    service.audit = MagicMock()

    org = MagicMock(id="o1")
    service.repo.create.return_value = org

    result = service.create_org("Org", "admin")
    assert result == org


def test_delete_org_not_found():
    db = MagicMock()
    service = OrganizationService(db)

    db.query().filter().first.return_value = None

    with pytest.raises(ValueError):
        service.delete_org("o1", {"id": "admin"})


# =====================================================
# ARTIFACT SERVICE
# =====================================================

@pytest.mark.asyncio
async def test_upload_invalid_content_type():
    service = ArtifactService(MagicMock())

    file = MagicMock(spec=UploadFile)
    file.content_type = "exe"

    with pytest.raises(Exception):
        await service.upload_streaming(file, {"id": "u1", "org_id": "o1"})


def test_search_prefix_too_short():
    service = ArtifactService(MagicMock())

    with pytest.raises(ValueError):
        service.search_artifacts_by_prefix(prefix="a", user={"org_id": "o1"})


def test_get_artifact_cross_org():
    service = ArtifactService(MagicMock())
    service.repo = MagicMock()

    artifact = MagicMock(org_id="o2")
    service.repo.get_by_id.return_value = artifact

    with pytest.raises(ValueError):
        service.get_artifact("a1", "o1", False)