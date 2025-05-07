from app.src.database.models.transaction import Transaction
from app.src.router.transaction.schema import TransactionCreate
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

    async def get_user_transactions(self, user_id: int) -> List[Transaction]:
        with session_manager() as db:
            filters = [Transaction.user_id == user_id]
            data = await self.crud_transaction.get_multi(*filters, db=db)
        return data


    async def get_transaction_by_id(self, transaction_id: int, user_id: int) -> Transaction:
        with session_manager() as db:
            transaction = await self.crud_transaction.get(db, transaction_id)
            if not transaction:
                raise FileNotFoundError("Transaction not found.")
            return transaction
