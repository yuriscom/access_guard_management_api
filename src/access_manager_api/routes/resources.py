from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..services.db import get_db
from ..schemas import IAMResource, IAMResourceCreate
from ..services import create_iam_resource

router = APIRouter(prefix="/iam/resources", tags=["iam-resources"])


@router.post("/", response_model=IAMResource)
def create_resource(resource: IAMResourceCreate, db: Session = Depends(get_db)):
    """Create a new IAM resource"""
    return create_iam_resource(db, resource)
