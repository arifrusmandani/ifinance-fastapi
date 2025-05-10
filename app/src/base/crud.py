from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import and_
from sqlalchemy.orm import Session
from app.src.database import Base
from app.src.core.config import PAGINATION_LIMIT
from app.src.database.session import session_manager

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).

        **Parameters**

        * `model`: A SQLAlchemy model class
        * `schema`: A Pydantic model (schema) class
        """
        self.model = model

    async def create(self, db: Session, obj_in: CreateSchemaType) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)  # type: ignore
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)

        if hasattr(self.model, "updated_at"):
            update_data["updated_at"] = datetime.now()
        if hasattr(self.model, "updated_date"):
            update_data["updated_date"] = datetime.now()

        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    async def get(self, db: Session, pk: Any) -> Optional[ModelType]:
        query = db.query(self.model).filter(self.model.id == pk)
        if hasattr(self.model, "deleted_date"):
            query = query.filter(self.model.deleted_date == None)
        if hasattr(self.model, "deleted_at"):
            query = query.filter(self.model.deleted_at == None)
        data = query.first()
        if data:
            return data
        else:
            raise FileNotFoundError("Data not found!")

    async def get_multi(
        self, *args, db: Session, offset: int = 0, limit: int = PAGINATION_LIMIT
    ) -> List[ModelType]:
        query = db.query(self.model).filter(*args)
        if hasattr(self.model, "deleted_date"):
            query = query.filter(self.model.deleted_date == None)
        if hasattr(self.model, "deleted_at"):
            query = query.filter(self.model.deleted_at == None)
        data = query.order_by(self.model.id.desc()).offset(
            offset).limit(limit).all()
        return data

    async def count(
        self, *args, db: Session
    ) -> int:
        query = db.query(self.model).filter(*args)
        if hasattr(self.model, "deleted_date"):
            query = query.filter(self.model.deleted_date == None)
        if hasattr(self.model, "deleted_at"):
            query = query.filter(self.model.deleted_at == None)
        data = query.count()
        return data

    async def remove(self, db: Session, *, pk: int) -> ModelType:
        obj = await self.get(db=db, pk=pk)
        if obj:
            obj.deleted_at = datetime.now()
            db.commit()
            db.refresh(obj)
            return obj
        else:
            raise FileNotFoundError("Data not found!")

    async def create_data(self, obj_in: CreateSchemaType) -> ModelType:
        with session_manager() as db:
            obj_in_data = jsonable_encoder(obj_in)
            db_obj = self.model(**obj_in_data)
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj

    async def update_data(
        self,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        with session_manager() as db:
            obj_data = jsonable_encoder(db_obj)
            if isinstance(obj_in, dict):
                update_data = obj_in
            else:
                update_data = obj_in.dict(exclude_unset=True)

            for field in obj_data:
                if field in update_data:
                    setattr(db_obj, field, update_data[field])
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj

    async def get_detail(self, *args, pk: Any = None) -> Optional[ModelType]:
        with session_manager() as db:
            query = db.query(self.model).filter(*args)
            if pk:
                query = query.filter(self.model.id == pk)
            if hasattr(self.model, "deleted_date"):
                query = query.filter(self.model.deleted_date == None)
            if hasattr(self.model, "deleted_at"):
                query = query.filter(self.model.deleted_at == None)
            if hasattr(self.model, "id"):
                query = query.order_by(self.model.id.desc())
            return query.first()

    async def get_all(
        self, *args, offset: int = 0, limit: int = PAGINATION_LIMIT, order_by: str = None
    ) -> List[ModelType]:
        """
        order_by format: '+column_name' or '-column_name'
        """
        with session_manager() as db:
            query = db.query(self.model).filter(*args)
            if hasattr(self.model, "deleted_date"):
                query = query.filter(self.model.deleted_date == None)
            if hasattr(self.model, "deleted_at"):
                query = query.filter(self.model.deleted_at == None)

            # Determine ordering
            if order_by:
                direction = order_by[0]
                column_name = order_by[1:]

                # Check if the column exists in the model
                if hasattr(self.model, column_name):
                    column = getattr(self.model, column_name)
                    if direction == '+':
                        query = query.order_by(column.asc())
                    elif direction == '-':
                        query = query.order_by(column.desc())
            else:
                if hasattr(self.model, "id"):
                    query = query.order_by(self.model.id.asc())
            return query.offset(offset).limit(limit).all()

    async def bulk_create(self, payload: list):
        with session_manager() as db:
            db.bulk_save_objects(objects=payload)
            db.commit()
            return len(payload)
        
    async def bulk_hard_delete(self, filters: list):
        with session_manager() as db:
            data = db.query(self.model).filter(*filters)
            deleted_data = len(data.all())
            data.delete()
            db.commit()
            return deleted_data

    async def bulk_update(self, obj_in):
        with session_manager() as db:
            db_dict_list = []
            for obj in obj_in:
                db_dict_list.append(jsonable_encoder(obj))
            db.bulk_update_mappings(self.model, db_dict_list)
            db.commit()
            return obj_in

    async def get_count(
        self, *args
    ) -> int:
        with session_manager() as db:
            query = db.query(self.model).filter(*args)
            if hasattr(self.model, "deleted_date"):
                query = query.filter(self.model.deleted_date == None)
            if hasattr(self.model, "deleted_at"):
                query = query.filter(self.model.deleted_at == None)
            data = query.count()
            return data
