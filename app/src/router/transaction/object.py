import json
import re
from app.src.database.models.transaction import Transaction, TransactionType
from app.src.router.transaction.schema import TransactionCreate, TransactionDetailList
from app.src.router.transaction.crud import CRUDTransaction
from app.src.database.session import session_manager
from typing import List, Optional, Tuple, Dict, Any
from datetime import datetime, date
from sqlalchemy import func
import pandas as pd
from fastapi import UploadFile
import io


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
            datas, total_data = await self.crud_transaction.get_user_transactions(
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

            return result, total_data

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

    def _validate_excel_columns(self, df: pd.DataFrame) -> None:
        """Validate required columns in Excel file."""
        required_columns = ['amount', 'type',
                            'description', 'date', 'category_code']
        missing_columns = [
            col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(
                f"Missing required columns: {', '.join(missing_columns)}")

    def _validate_row_count(self, df: pd.DataFrame) -> None:
        """Validate number of rows in Excel file."""
        if len(df) > 1000:
            raise ValueError("Maximum 1000 rows allowed")

    def _validate_amount(self, amount: Any, row_index: int) -> Tuple[float, List[str]]:
        """Validate amount field."""
        errors = []
        if pd.isna(amount):
            errors.append(f"Row {row_index + 2}: Amount is required")
            return None, errors

        try:
            amount_float = float(amount)
            if amount_float <= 0:
                errors.append(
                    f"Row {row_index + 2}: Amount must be greater than 0")
                return None, errors
            return amount_float, errors
        except ValueError:
            errors.append(f"Row {row_index + 2}: Invalid amount format")
            return None, errors

    def _validate_type(self, type_value: Any, row_index: int) -> Tuple[TransactionType, List[str]]:
        """Validate transaction type field."""
        errors = []
        if pd.isna(type_value):
            errors.append(f"Row {row_index + 2}: Type is required")
            return None, errors

        try:
            type_enum = TransactionType(str(type_value).upper())
            return type_enum, errors
        except ValueError:
            errors.append(
                f"Row {row_index + 2}: Invalid transaction type. Must be INCOME or EXPENSE")
            return None, errors

    def _validate_description(self, description: Any, row_index: int) -> Tuple[str, List[str]]:
        """Validate description field."""
        errors = []
        if pd.isna(description):
            errors.append(f"Row {row_index + 2}: Description is required")
            return None, errors

        desc_str = str(description)
        if not desc_str.strip():
            errors.append(f"Row {row_index + 2}: Description cannot be empty")
            return None, errors

        return desc_str, errors

    def _validate_date(self, date_value: Any, row_index: int) -> Tuple[datetime, List[str]]:
        """Validate date field."""
        errors = []
        if pd.isna(date_value):
            errors.append(f"Row {row_index + 2}: Date is required")
            return None, errors

        try:
            if isinstance(date_value, datetime):
                date_obj = date_value
            elif isinstance(date_value, str):
                date_obj = datetime.strptime(date_value, '%Y-%m-%d')
            else:
                # fallback: try convert via pandas Timestamp or other
                date_obj = pd.to_datetime(date_value).to_pydatetime()
            return date_obj, errors
        except Exception:
            errors.append(
                f"Row {row_index + 2}: Invalid date format. Use YYYY-MM-DD")
            return None, errors

    def _validate_category_code(self, category_code: Any, row_index: int) -> Tuple[str, List[str]]:
        """Validate category code field."""
        errors = []
        if pd.isna(category_code):
            errors.append(f"Row {row_index + 2}: Category code is required")
            return None, errors

        code_str = str(category_code)
        if not code_str.strip():
            errors.append(
                f"Row {row_index + 2}: Category code cannot be empty")
            return None, errors

        return code_str, errors

    def _validate_row(self, row: pd.Series, index: int) -> Tuple[Dict, List[str]]:
        """Validate a single row of transaction data."""
        errors = []
        transaction_data = {}

        # Validate amount
        amount, amount_errors = self._validate_amount(row['amount'], index)
        errors.extend(amount_errors)
        if amount is not None:
            transaction_data['amount'] = amount

        # Validate type
        type_, type_errors = self._validate_type(row['type'], index)
        errors.extend(type_errors)
        if type_ is not None:
            transaction_data['type'] = type_

        # Validate description
        description, desc_errors = self._validate_description(
            row['description'], index)
        errors.extend(desc_errors)
        if description is not None:
            transaction_data['description'] = description

        # Validate date
        date_, date_errors = self._validate_date(row['date'], index)
        errors.extend(date_errors)
        if date_ is not None:
            transaction_data['date'] = date_

        # Validate category code
        category_code, code_errors = self._validate_category_code(
            row['category_code'], index)
        errors.extend(code_errors)
        if category_code is not None:
            transaction_data['category_code'] = category_code

        return transaction_data, errors

    async def bulk_create_transactions(
        self,
        user_id: int,
        file: UploadFile
    ) -> Dict:
        # Read Excel file
        contents = await file.read()
        try:
            df = pd.read_excel(io.BytesIO(contents), sheet_name='transaction')
        except Exception as e:
            raise ValueError(f"Invalid Excel file format: {str(e)}")

        # Validate Excel structure
        self._validate_excel_columns(df)
        self._validate_row_count(df)

        # Remove rows where all required columns are empty/NaN
        required_columns = ['amount', 'type',
                            'description', 'date', 'category_code']
        df = df.dropna(subset=required_columns, how='all')

        # Process rows
        errors = []
        valid_transactions = []

        for index, row in df.iterrows():
            # Skip if all required fields are empty
            if all(pd.isna(row[col]) for col in required_columns):
                continue

            transaction_data, row_errors = self._validate_row(row, index)
            errors.extend(row_errors)

            if transaction_data and not row_errors:
                valid_transactions.append(transaction_data)

        if errors:
            raise ValueError("\n".join(errors))

        # Insert valid transactions
        with session_manager() as db:
            created_transactions = []
            for transaction_data in valid_transactions:
                transaction = TransactionCreate(
                    user_id=user_id,
                    **transaction_data
                )
                created = await self.crud_transaction.create(db, transaction)
                created_transactions.append(created)

            return {
                "total_rows": len(df),
                "valid_rows": len(valid_transactions),
                "created_rows": len(created_transactions)
            }
