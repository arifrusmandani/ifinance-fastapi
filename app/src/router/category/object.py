from typing import List, Optional
from app.src.database.models.category import Category
from app.src.database.models.transaction import TransactionType
from app.src.router.category.crud import CRUDCategory
from app.src.database.session import session_manager


class CategoryObject:
    def __init__(self, authorized_user):
        self.crud_category = CRUDCategory(Category)
        self.authorized_user = authorized_user

    async def get_categories(self, category_type: Optional[TransactionType] = None) -> List[Category]:
        with session_manager() as db:
            filters = []
            if type:
                filters.append(Category.type == category_type)
            data = await self.crud_category.get_multi(*filters, db=db)
        return data
