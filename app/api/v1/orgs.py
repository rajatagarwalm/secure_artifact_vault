from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user, require_permission
from app.schemas.org import OrganizationCreateRequest, OrganizationResponse
from app.services.org_service import OrganizationService
from app.repositories.org_repo import OrganizationRepository

router = APIRouter(prefix="/orgs", tags=["Organizations"])


@router.get(
    "",
    response_model=list[OrganizationResponse],
    dependencies=[Depends(require_permission("*"))],  # superadmin only
)
def list_orgs(db: Session = Depends(get_db)):
    orgs = OrganizationRepository(db).get_all()
    return [
        OrganizationResponse(
            id=str(o.id),
            name=o.name,
            is_deleted=o.is_deleted,
        )
        for o in orgs
    ]


@router.post(
    "",
    response_model=OrganizationResponse,
    dependencies=[Depends(require_permission("org:manage"))],
)
def create_org(
    payload: OrganizationCreateRequest,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    org = OrganizationService(db).create_org(
        name=payload.name,
        actor_id=user["id"],
    )
    return OrganizationResponse(
        id=str(org.id),
        name=org.name,
        is_deleted=org.is_deleted,
    )


@router.delete(
    "/{org_id}",
    dependencies=[Depends(require_permission("*"))],  # superadmin only
)
def delete_organization(
    org_id: str,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        OrganizationService(db).delete_org(
            org_id=org_id,
            actor=user,
        )
        return {"message": "Organization deleted successfully"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
