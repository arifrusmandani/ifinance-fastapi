from app.src.database.models.transaction import Transaction
from app.src.router.transaction.schema import TransactionCreate
from app.src.router.transaction.crud import create_transaction, get_user_transactions, get_transaction_by_id
from app.src.database.session import session_manager
from typing import List


class TransactionObject:
    @classmethod
    async def create_transaction(cls, user_id: int, transaction_data: dict) -> Transaction:
        try:
            with session_manager() as db:
                return await create_transaction(db, user_id, transaction_data)
        except Exception as e:
            raise e

    @classmethod
    async def get_user_transactions(cls, user_id: int) -> List[Transaction]:
        with session_manager() as db:
            data = await get_user_transactions(db, user_id)
            return data 

    @classmethod
    async def get_transaction_by_id(cls, transaction_id: int, user_id: int) -> Transaction:
        with session_manager() as db:
            transaction = await get_transaction_by_id(db, transaction_id, user_id)
            if not transaction:
                raise FileNotFoundError("Transaction not found.")
            return transaction
