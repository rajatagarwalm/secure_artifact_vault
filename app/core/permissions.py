ROLE_PERMISSIONS = {
    "viewer": ["artifact:read"],
    "editor": ["artifact:read", "artifact:write"],
    "admin": ["org:manage", "artifact:*", "user:manage"],
    "superadmin": ["*"],
}


def resolve_permissions(roles: list[str]) -> list[str]:
    permissions: set[str] = set()
    for role in roles:
        perms = ROLE_PERMISSIONS.get(role, [])
        for p in perms:
            permissions.add(p)
    return list(permissions)


def has_permission(user_permissions: list[str], required: str) -> bool:
    if "*" in user_permissions:
        return True
    if required in user_permissions:
        return True

    # wildcard support: artifact:* matches artifact:read
    prefix = required.split(":")[0] + ":*"
    return prefix in user_permissions
