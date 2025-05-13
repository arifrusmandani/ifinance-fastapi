from fastapi import Response, status as http_status, Depends
from fastapi.encoders import jsonable_encoder
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from datetime import date
from typing import Optional

from app.src.core.config import PAGINATION_LIMIT
from app.src.database.models.user import User
from app.src.exception.handler.context import api_exception_handler
from app.src.router.transaction.object import TransactionObject
from app.src.router.transaction.schema import (
    TransactionBase,
    TransactionResponse,
    TransactionListResponse,
    TransactionSummaryResponse
)
from app.src.router.user.security import get_authorized_user

router = InferringRouter()


@cbv(router)
class TransactionView:
    """ Transaction View Router """
    res: Response

    def __init__(self, authorized_user: User = Depends(get_authorized_user)):
        self.authorized_user = authorized_user
        self.transaction_object = TransactionObject(authorized_user)

    @router.post("/", response_model=TransactionResponse)
    async def create_transaction(
        self,
        transaction: TransactionBase,
    ) -> dict:
        """
        Create a new transaction.

        - **amount**: Transaction amount
        - **description**: Transaction description
        - **transaction_type**: Type of transaction (INCOME/EXPENSE)
        - **category**: Transaction category (optional)
        - **date**: Transaction date (optional, defaults to current time)

        Returns the created transaction.
        """
        with api_exception_handler(self.res) as response_builder:
            transaction_data = transaction.dict()
            new_transaction = await self.transaction_object.create_transaction(
                user_id=self.authorized_user.id,
                transaction_data=transaction_data
            )
            response_builder.status = True
            response_builder.code = http_status.HTTP_201_CREATED
            response_builder.message = "Transaction created successfully"
            response_builder.data = jsonable_encoder(new_transaction)
        return response_builder.to_dict()

    @router.get("/", response_model=TransactionListResponse)
    async def get_transactions(
        self,
        offset: int = 0,
        limit: int = PAGINATION_LIMIT
    ) -> dict:
        """
        Get all transactions for the current user.

        Returns a list of transactions.
        """
        with api_exception_handler(self.res, response_type="list") as response_builder:
            transactions = await self.transaction_object.get_user_transactions(
                user_id=self.authorized_user.id,
                offset=offset,
                limit=limit
            )
            response_builder.status = True
            response_builder.code = http_status.HTTP_200_OK
            response_builder.message = "Transactions retrieved successfully"
            response_builder.data = jsonable_encoder(transactions)
        return response_builder.to_dict()

    @router.get("/{transaction_id}", response_model=TransactionResponse)
    async def get_transaction(
        self,
        transaction_id: int,
    ) -> dict:
        """
        Get a specific transaction by ID.

        - **transaction_id**: ID of the transaction to retrieve

        Returns the transaction if found.
        """
        with api_exception_handler(self.res) as response_builder:
            transaction = await self.transaction_object.get_transaction_by_id(
                transaction_id=transaction_id,
                user_id=self.authorized_user.id
            )
            response_builder.status = True
            response_builder.code = http_status.HTTP_200_OK
            response_builder.message = "Transaction retrieved successfully"
            response_builder.data = jsonable_encoder(transaction)
        return response_builder.to_dict()

    @router.get("/user/summary", response_model=TransactionSummaryResponse)
    async def get_transaction_summary(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> dict:
        """
        Get transaction summary (total income and expense) for the current user.

        - **start_date**: Filter transactions from this date (optional)
        - **end_date**: Filter transactions until this date (optional)

        Returns total income, total expense, and net amount.
        """
        with api_exception_handler(self.res) as response_builder:
            total_income, total_expense = await self.transaction_object.get_transaction_summary(
                user_id=self.authorized_user.id,
                start_date=start_date,
                end_date=end_date
            )

            summary = {
                "total_income": total_income,
                "total_expense": total_expense,
                "net_amount": total_income - total_expense
            }

            response_builder.status = True
            response_builder.code = http_status.HTTP_200_OK
            response_builder.message = "Transaction summary retrieved successfully"
            response_builder.data = summary
        return response_builder.to_dict()
