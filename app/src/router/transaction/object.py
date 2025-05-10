from app.src.database.models.transaction import Transaction
from app.src.router.transaction.schema import TransactionCreate, TransactionDetailList
from app.src.router.transaction.crud import CRUDTransaction
from app.src.database.session import session_manager
from typing import List


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

    async def get_user_transactions(self, user_id: int, offset: int, limit: int) -> List[TransactionDetailList]:
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
