from sqlalchemy.orm import Session
from typing import List, Optional
from ..models import IAMResource
from ..schemas import IAMResourceCreate

class IAMResourceService:
    def __init__(self, db: Session):
        self.db = db

    def create_resource(self, resource: IAMResourceCreate) -> IAMResource:
        db_resource = IAMResource(**resource.model_dump())
        self.db.add(db_resource)
        self.db.commit()
        self.db.refresh(db_resource)
        return db_resource

    def get_resource(self, resource_id: int) -> Optional[IAMResource]:
        return self.db.query(IAMResource).filter(IAMResource.id == resource_id).first()

    def get_resources(self, skip: int = 0, limit: int = 100) -> List[IAMResource]:
        return self.db.query(IAMResource).offset(skip).limit(limit).all()

    def get_resources_by_app(self, app_id: int) -> List[IAMResource]:
        return self.db.query(IAMResource).filter(IAMResource.app_id == app_id).all()

    def update_resource(self, resource_id: int, resource: IAMResourceCreate) -> Optional[IAMResource]:
        db_resource = self.get_resource(resource_id)
        if db_resource:
            for key, value in resource.model_dump().items():
                setattr(db_resource, key, value)
            self.db.commit()
            self.db.refresh(db_resource)
        return db_resource

    def delete_resource(self, resource_id: int) -> bool:
        db_resource = self.get_resource(resource_id)
        if db_resource:
            self.db.delete(db_resource)
            self.db.commit()
            return True
        return False 