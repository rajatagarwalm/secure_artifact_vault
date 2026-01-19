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

    user = MagicMock(id="u1", password_hash="hash", password_expires_at=None)

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


def test_create_user_success():
    """Test successful user creation by superadmin."""
    service = UserService(MagicMock())
    service.user_repo = MagicMock()
    service.role_repo = MagicMock()
    service.audit = MagicMock()

    user = MagicMock(id="u1", email="newuser@example.com", is_active=True)
    mapping = MagicMock(id="m1")

    service.user_repo.get_by_email.return_value = None
    service.user_repo.create.return_value = user
    service.role_repo.assign.return_value = mapping

    actor = {"permissions": ["*"], "id": "admin"}

    with patch("app.services.user_service.hash_password", return_value="hashed_pwd"):
        result = service.create_user(
            email="newuser@example.com",
            password="secure_password",
            org_id="o1",
            role="editor",
            actor=actor,
        )

    assert result["id"] == "u1"
    assert result["email"] == "newuser@example.com"
    assert result["message"] == "User created successfully"
    service.user_repo.create.assert_called_once()
    service.role_repo.assign.assert_called_once()
    service.audit.log.assert_called_once()


def test_create_user_non_superadmin_denied():
    """Test that non-superadmin cannot create users."""
    service = UserService(MagicMock())

    actor = {"permissions": ["artifact:read"], "org_id": "o1", "id": "regular_user"}

    with pytest.raises(ValueError) as exc_info:
        service.create_user(
            email="newuser@example.com",
            password="secure_password",
            org_id="o1",
            role="editor",
            actor=actor,
        )

    assert "Only superadmin can create users" in str(exc_info.value)


def test_create_user_duplicate_email():
    """Test that duplicate email raises error."""
    service = UserService(MagicMock())
    service.user_repo = MagicMock()

    existing_user = MagicMock(id="u2", email="existing@example.com")
    service.user_repo.get_by_email.return_value = existing_user

    actor = {"permissions": ["*"], "id": "admin"}

    with pytest.raises(ValueError) as exc_info:
        service.create_user(
            email="existing@example.com",
            password="secure_password",
            org_id="o1",
            role="editor",
            actor=actor,
        )

    assert "already exists" in str(exc_info.value)


def test_create_user_assigns_correct_role():
    """Test that user is assigned with the correct role."""
    service = UserService(MagicMock())
    service.user_repo = MagicMock()
    service.role_repo = MagicMock()
    service.audit = MagicMock()

    user = MagicMock(id="u1", email="newuser@example.com", is_active=True)
    mapping = MagicMock(id="m1")

    service.user_repo.get_by_email.return_value = None
    service.user_repo.create.return_value = user
    service.role_repo.assign.return_value = mapping

    actor = {"permissions": ["*"], "id": "admin"}

    with patch("app.services.user_service.hash_password", return_value="hashed_pwd"):
        service.create_user(
            email="newuser@example.com",
            password="secure_password",
            org_id="o1",
            role="admin",
            actor=actor,
        )

    service.role_repo.assign.assert_called_once_with("u1", "o1", "admin")


def test_create_user_audit_logged():
    """Test that user creation is logged in audit trail."""
    service = UserService(MagicMock())
    service.user_repo = MagicMock()
    service.role_repo = MagicMock()
    service.audit = MagicMock()

    user = MagicMock(id="u1", email="newuser@example.com", is_active=True)
    mapping = MagicMock(id="m1")

    service.user_repo.get_by_email.return_value = None
    service.user_repo.create.return_value = user
    service.role_repo.assign.return_value = mapping

    actor = {"permissions": ["*"], "id": "admin123"}

    with patch("app.services.user_service.hash_password", return_value="hashed_pwd"):
        service.create_user(
            email="newuser@example.com",
            password="secure_password",
            org_id="o1",
            role="viewer",
            actor=actor,
        )

    service.audit.log.assert_called_once()
    call_args = service.audit.log.call_args
    assert call_args[1]["action"] == "user_created"
    assert call_args[1]["actor_id"] == "admin123"
    assert call_args[1]["org_id"] == "o1"
    assert call_args[1]["resource_type"] == "user"
    assert call_args[1]["resource_id"] == "u1"
    assert call_args[1]["extra_data"]["email"] == "newuser@example.com"
    assert call_args[1]["extra_data"]["role"] == "viewer"


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


# =====================================================
# PASSWORD MANAGEMENT TESTS
# =====================================================

def test_change_password_success():
    """Test successful password change."""
    service = UserService(MagicMock())
    service.user_repo = MagicMock()
    service.password_history = MagicMock()
    service.audit = MagicMock()

    user = MagicMock(id="u1", email="user@example.com", password_hash="old_hash")
    service.user_repo.get_by_id.return_value = user

    actor = {"id": "u1", "org_id": "o1"}

    with patch("app.services.user_service.verify_password", return_value=True), \
         patch("app.services.user_service.hash_password", return_value="new_hash"):
        result = service.change_password(
            user_id="u1",
            old_password="old_password",
            new_password="new_password",
            actor=actor,
        )

    assert result["message"] == "Password changed successfully"
    service.password_history.create.assert_called_once()
    service.audit.log.assert_called_once()


def test_change_password_wrong_old_password():
    """Test password change fails with wrong old password."""
    service = UserService(MagicMock())
    service.user_repo = MagicMock()

    user = MagicMock(id="u1", password_hash="old_hash")
    service.user_repo.get_by_id.return_value = user

    actor = {"id": "u1", "org_id": "o1"}

    with patch("app.services.user_service.verify_password", return_value=False):
        with pytest.raises(ValueError) as exc_info:
            service.change_password(
                user_id="u1",
                old_password="wrong_password",
                new_password="new_password",
                actor=actor,
            )
        assert "Incorrect current password" in str(exc_info.value)


def test_change_password_other_user_denied():
    """Test that user cannot change another user's password."""
    service = UserService(MagicMock())
    service.user_repo = MagicMock()

    user = MagicMock(id="u2", password_hash="old_hash")
    service.user_repo.get_by_id.return_value = user

    actor = {"id": "u1", "org_id": "o1"}

    with patch("app.services.user_service.verify_password", return_value=True):
        with pytest.raises(ValueError) as exc_info:
            service.change_password(
                user_id="u2",
                old_password="old_password",
                new_password="new_password",
                actor=actor,
            )
        assert "own password" in str(exc_info.value)


def test_reset_password_success():
    """Test successful admin password reset."""
    service = UserService(MagicMock())
    service.user_repo = MagicMock()
    service.password_history = MagicMock()
    service.audit = MagicMock()

    user = MagicMock(id="u2", email="user@example.com", password_hash="old_hash")
    service.user_repo.get_by_id.return_value = user

    actor = {"id": "admin", "permissions": ["*"], "org_id": "o1"}

    with patch("app.services.user_service.hash_password", return_value="new_hash"):
        result = service.reset_password(
            user_id="u2",
            new_password="new_password",
            actor=actor,
        )

    assert result["id"] == "u2"
    assert result["email"] == "user@example.com"
    assert result["message"] == "Password reset successfully"
    assert "password_expires_at" in result
    service.password_history.create.assert_called_once()
    service.audit.log.assert_called_once()


def test_reset_password_non_superadmin_denied():
    """Test that non-superadmin cannot reset passwords."""
    service = UserService(MagicMock())

    actor = {"id": "admin", "permissions": ["user:manage"], "org_id": "o1"}

    with pytest.raises(ValueError) as exc_info:
        service.reset_password(
            user_id="u2",
            new_password="new_password",
            actor=actor,
        )
    assert "Only superadmin" in str(exc_info.value)


def test_is_password_expired_true():
    """Test password expiration check returns True for expired password."""
    from datetime import datetime, timedelta
    
    service = UserService(MagicMock())
    service.user_repo = MagicMock()

    user = MagicMock(
        id="u1",
        password_expires_at=datetime.utcnow() - timedelta(hours=1)
    )
    service.user_repo.get_by_id.return_value = user

    result = service.is_password_expired("u1")
    assert result is True


def test_is_password_expired_false():
    """Test password expiration check returns False for valid password."""
    from datetime import datetime, timedelta
    
    service = UserService(MagicMock())
    service.user_repo = MagicMock()

    user = MagicMock(
        id="u1",
        password_expires_at=datetime.utcnow() + timedelta(hours=1)
    )
    service.user_repo.get_by_id.return_value = user

    result = service.is_password_expired("u1")
    assert result is False


def test_is_password_expired_no_expiration():
    """Test password expiration check returns False when no expiration set."""
    service = UserService(MagicMock())
    service.user_repo = MagicMock()

    user = MagicMock(id="u1", password_expires_at=None)
    service.user_repo.get_by_id.return_value = user

    result = service.is_password_expired("u1")
    assert result is False