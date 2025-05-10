from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.src.base.crud import CRUDBase
from app.src.database.models.category import Category
from app.src.database.models.transaction import Transaction
from typing import List

from app.src.router.transaction.schema import TransactionDetailList


class CRUDTransaction(CRUDBase):

    async def create_transaction(self, db: AsyncSession, user_id: int, transaction_data: dict) -> Transaction:
        transaction = Transaction(
            user_id=user_id,
            amount=transaction_data['amount'],
            description=transaction_data['description'],
            type=transaction_data['type'],
            category_code=transaction_data.get('category_code'),
            date=transaction_data.get('date')
        )
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        return transaction

    async def get_user_transactions(self, db: AsyncSession, user_id: int, offset: int, limit: int) -> List[TransactionDetailList]:
        query = db.query(
            Transaction.id.label('id'),
            Transaction.user_id.label('user_id'),
            Transaction.date.label('date'),
            Transaction.type.label('type'),
            Transaction.amount.label('amount'),
            Transaction.description.label('description'),
            Transaction.category_code.label('category_code'),
            Transaction.created_at.label('created_at'),
            Category.name.label('category_name'),
            Category.icon.label('category_icon')
        ).join(
            Category, Category.code == Transaction.category_code
        ).filter(Transaction.user_id == user_id).order_by(Transaction.id.desc()).offset(
            offset).limit(limit)
        return query.all()

    async def get_transaction_by_id(db: AsyncSession, transaction_id: int, user_id: int) -> Transaction:
        query = db.query(Transaction).filter(
            Transaction.id == transaction_id,
            Transaction.user_id == user_id
        ).order_by(Transaction.id.desc())
        return query.first()
