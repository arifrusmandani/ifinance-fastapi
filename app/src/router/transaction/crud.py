from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.src.base.crud import CRUDBase
from app.src.database.models.transaction import Transaction
from typing import List



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


    async def get_user_transactions(db: AsyncSession, user_id: int) -> List[Transaction]:
        query = db.query(Transaction).filter(Transaction.user_id == user_id).order_by(Transaction.id.desc())
        return query.all()


    async def get_transaction_by_id(db: AsyncSession, transaction_id: int, user_id: int) -> Transaction:
        query = db.query(Transaction).filter(
            Transaction.id == transaction_id,
            Transaction.user_id == user_id
        ).order_by(Transaction.id.desc())
        return query.first()
