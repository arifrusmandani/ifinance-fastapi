from app.src.database.models.transaction import Transaction, TransactionType
from app.src.router.transaction.schema import TransactionCreate, TransactionDetailList
from app.src.router.transaction.crud import CRUDTransaction
from app.src.database.session import session_manager
from typing import List, Optional, Tuple
from datetime import datetime, date
from sqlalchemy import func


class TransactionObject:
    def __init__(self, authorized_user):
        self.crud_transaction = CRUDTransaction(Transaction)
        self.authorized_user = authorized_user

    async def create_transaction(self, user_id: int, transaction_data: dict) -> Transaction:
        with session_manager() as db:
            transaction_data = TransactionCreate(
                user_id=user_id,
                amount=transaction_data['amount'],
                description=transaction_data['description'],
                type=transaction_data['type'],
                category_code=transaction_data.get('category_code'),
                date=transaction_data.get('date')
            )
            return await self.crud_transaction.create(db, transaction_data)

    async def get_user_transactions(self, user_id: int, offset: int = 0, limit: int = 20) -> List[TransactionDetailList]:
        result = []
        with session_manager() as db:
            datas = await self.crud_transaction.get_user_transactions(
                db=db, user_id=user_id, offset=offset, limit=limit)

            for data in datas:
                result.append(
                    TransactionDetailList(
                        id=data.id,
                        user_id=data.user_id,
                        amount=data.amount,
                        description=data.description,
                        type=data.type,
                        category_code=data.category_code,
                        date=data.date,
                        category_name=data.category_name,
                        category_icon=data.category_icon,
                        created_at=data.created_at,
                    )
                )

            return result

    async def get_transaction_by_id(self, transaction_id: int, user_id: int) -> Transaction:
        with session_manager() as db:
            transaction = await self.crud_transaction.get(db, transaction_id)
            if not transaction:
                raise FileNotFoundError("Transaction not found.")
            return transaction

    async def get_transaction_summary(
        self,
        user_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Tuple[float, float]:
        with session_manager() as db:
            # Base query with user filter
            query = db.query(
                Transaction.type,
                func.sum(Transaction.amount).label('total')
            ).filter(Transaction.user_id == user_id)

            # Add date filters if provided
            if start_date:
                query = query.filter(Transaction.date >= start_date)
            if end_date:
                query = query.filter(Transaction.date <= end_date)

            # Group by transaction type
            query = query.group_by(Transaction.type)

            # Execute query
            results = query.all()

            # Initialize totals
            total_income = 0.0
            total_expense = 0.0

            # Process results
            for type_, total in results:
                if type_ == TransactionType.INCOME:
                    total_income = float(total)
                elif type_ == TransactionType.EXPENSE:
                    total_expense = float(total)

            return total_income, total_expense
