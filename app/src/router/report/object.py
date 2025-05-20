from typing import List, Optional, Dict, Any
from datetime import date, datetime, timedelta
from sqlalchemy import func, desc, extract
from app.src.database.models.transaction import Transaction, TransactionType
from app.src.database.models.category import Category
from app.src.router.report.crud import CRUDReport
from app.src.database.session import session_manager
from app.src.router.report.schema import (
    CategoryReport,
    MonthlyChartData,
    DashboardSummaryItem,
    MostExpenseCategory,
    CategoryAmount,
    MonthCashflow,
    CashflowTransaction
)


class ReportObject:
    def __init__(self, authorized_user):
        self.crud_report = CRUDReport(Transaction)
        self.authorized_user = authorized_user

    async def get_category_report(
        self,
        user_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[CategoryReport]:
        with session_manager() as db:
            # Base query with user filter
            query = db.query(
                Transaction.category_code,
                Transaction.type,
                func.sum(Transaction.amount).label('total')
            ).filter(Transaction.user_id == user_id)

            # Add date filters if provided
            if start_date:
                query = query.filter(Transaction.date >= start_date)
            if end_date:
                query = query.filter(Transaction.date <= end_date)

            # Group by category and type
            query = query.group_by(Transaction.category_code, Transaction.type)

            # Execute query
            results = query.all()

            # Process results into category reports
            reports = []

            # First, add income categories
            income_reports = []
            expense_reports = []

            for category_code, type_, total in results:
                if type_ == TransactionType.INCOME:
                    income_reports.append(
                        CategoryReport(
                            category=category_code,
                            type=type_,
                            amount=float(total)
                        )
                    )
                elif type_ == TransactionType.EXPENSE:
                    expense_reports.append(
                        CategoryReport(
                            category=category_code,
                            type=type_,
                            amount=float(total)
                        )
                    )

            # Sort income reports by amount (descending)
            income_reports.sort(key=lambda x: x.amount, reverse=True)

            # Sort expense reports by amount (descending)
            expense_reports.sort(key=lambda x: x.amount, reverse=True)

            # Combine reports: income first, then expense
            reports = income_reports + expense_reports

            return reports

    async def get_monthly_chart_data(
        self,
        user_id: int,
        year: int = datetime.now().year
    ) -> List[MonthlyChartData]:
        with session_manager() as db:
            # Base query with user filter and year
            query = db.query(
                extract('month', Transaction.date).label('month'),
                Transaction.type,
                func.sum(Transaction.amount).label('total')
            ).filter(
                Transaction.user_id == user_id,
                extract('year', Transaction.date) == year
            )

            # Group by month and type
            query = query.group_by(
                extract('month', Transaction.date),
                Transaction.type
            )

            # Execute query
            results = query.all()

            # Process results into monthly data
            monthly_data: Dict[int, Dict[str, float]] = {}

            # Initialize all months with zero values
            for month in range(1, 13):
                monthly_data[month] = {
                    'income': 0.0,
                    'expense': 0.0
                }

            # Fill in the actual values
            for month, type_, total in results:
                if type_ == TransactionType.INCOME:
                    monthly_data[month]['income'] = float(total)
                elif type_ == TransactionType.EXPENSE:
                    monthly_data[month]['expense'] = float(total)

            # Convert to MonthlyChartData objects
            month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                           'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

            reports = []
            for month, totals in monthly_data.items():
                reports.append(
                    MonthlyChartData(
                        name=month_names[month - 1],
                        income=totals['income'],
                        expense=totals['expense']
                    )
                )

            return reports

    async def get_dashboard_summary(
        self,
        user_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[DashboardSummaryItem]:
        with session_manager() as db:
            # If no period is given, use current month as default
            today = datetime.now().date()
            if not start_date or not end_date:
                start_date = today.replace(day=1)
                # end_date is last day of current month
                next_month = (start_date.replace(day=28) +
                              timedelta(days=4)).replace(day=1)
                end_date = next_month - timedelta(days=1)

            # Calculate previous period (last month)
            prev_end = start_date - timedelta(days=1)
            prev_start = prev_end.replace(day=1)

            # Helper to get totals for a period
            def get_totals(start, end):
                q = db.query(
                    Transaction.type,
                    func.sum(Transaction.amount).label('total')
                ).filter(
                    Transaction.user_id == user_id,
                    Transaction.date >= start,
                    Transaction.date <= end
                ).group_by(Transaction.type)
                res = {TransactionType.INCOME: 0.0,
                       TransactionType.EXPENSE: 0.0}
                for t, total in q:
                    res[t] = float(total)
                return res

            # Current period
            totals = get_totals(start_date, end_date)
            # Previous period
            prev_totals = get_totals(prev_start, prev_end)

            # Calculate percent change helper
            def percent_change(current, previous):
                if previous == 0:
                    return 0.0 if current == 0 else 100.0
                return round(((current - previous) / abs(previous)) * 100, 2)

            # Prepare summary items
            balance = totals[TransactionType.INCOME] - \
                totals[TransactionType.EXPENSE]
            prev_balance = prev_totals[TransactionType.INCOME] - \
                prev_totals[TransactionType.EXPENSE]
            summary = [
                DashboardSummaryItem(
                    label="Total Balance",
                    value=balance,
                    percent=percent_change(balance, prev_balance),
                    last_month=prev_balance
                ),
                DashboardSummaryItem(
                    label="Total Period Expenses",
                    value=totals[TransactionType.EXPENSE],
                    percent=percent_change(
                        totals[TransactionType.EXPENSE], prev_totals[TransactionType.EXPENSE]),
                    last_month=prev_totals[TransactionType.EXPENSE]
                ),
                DashboardSummaryItem(
                    label="Total Period Income",
                    value=totals[TransactionType.INCOME],
                    percent=percent_change(
                        totals[TransactionType.INCOME], prev_totals[TransactionType.INCOME]),
                    last_month=prev_totals[TransactionType.INCOME]
                ),
            ]
            return summary

    async def get_most_expense_by_category(
        self,
        user_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[MostExpenseCategory]:
        with session_manager() as db:
            # If no period is given, use current month as default
            today = datetime.now().date()
            if not start_date or not end_date:
                start_date = today.replace(day=1)
                next_month = (start_date.replace(day=28) +
                              timedelta(days=4)).replace(day=1)
                end_date = next_month - timedelta(days=1)

            # Get total expense for percentage calculation
            total_expense = db.query(func.sum(Transaction.amount)).filter(
                Transaction.user_id == user_id,
                Transaction.type == TransactionType.EXPENSE,
                Transaction.date >= start_date,
                Transaction.date <= end_date
            ).scalar() or 0.0

            # Get category expenses with category details
            results = db.query(
                Transaction.category_code,
                Category.name.label('category_name'),
                Category.color,
                func.sum(Transaction.amount).label('total')
            ).join(
                Category,
                Transaction.category_code == Category.code
            ).filter(
                Transaction.user_id == user_id,
                Transaction.type == TransactionType.EXPENSE,
                Transaction.date >= start_date,
                Transaction.date <= end_date
            ).group_by(
                Transaction.category_code,
                Category.name,
                Category.color
            ).order_by(
                desc('total')
            ).all()

            # Process results
            categories = []
            for category_code, category_name, color, total in results:
                amount = float(total)
                percentage = (amount / total_expense *
                              100) if total_expense > 0 else 0

                categories.append(
                    MostExpenseCategory(
                        category_code=category_code,
                        category_name=category_name,
                        amount=amount,
                        color=color,
                        percentage=round(percentage, 2)
                    )
                )

            return categories

    async def get_income_categories(
        self,
        user_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[CategoryAmount]:
        with session_manager() as db:
            # If no period is given, use current month as default
            today = datetime.now().date()
            if not start_date or not end_date:
                start_date = today.replace(day=1)
                next_month = (start_date.replace(day=28) +
                              timedelta(days=4)).replace(day=1)
                end_date = next_month - timedelta(days=1)

            # Get category incomes with category details
            results = db.query(
                Transaction.category_code,
                Category.name.label('category_name'),
                Category.color,
                func.sum(Transaction.amount).label('total')
            ).join(
                Category,
                Transaction.category_code == Category.code
            ).filter(
                Transaction.user_id == user_id,
                Transaction.type == TransactionType.INCOME,
                Transaction.date >= start_date,
                Transaction.date <= end_date
            ).group_by(
                Transaction.category_code,
                Category.name,
                Category.color
            ).order_by(
                desc('total')
            ).all()

            # Process results
            categories = []
            for category_code, category_name, color, total in results:
                amount = float(total)
                categories.append(
                    CategoryAmount(
                        category_code=category_code,
                        category_name=category_name,
                        amount=amount,
                        color=color
                    )
                )

            return categories

    async def get_expense_categories(
        self,
        user_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[CategoryAmount]:
        with session_manager() as db:
            # If no period is given, use current month as default
            today = datetime.now().date()
            if not start_date or not end_date:
                start_date = today.replace(day=1)
                next_month = (start_date.replace(day=28) +
                              timedelta(days=4)).replace(day=1)
                end_date = next_month - timedelta(days=1)

            # Get category expenses with category details
            results = db.query(
                Transaction.category_code,
                Category.name.label('category_name'),
                Category.color,
                func.sum(Transaction.amount).label('total')
            ).join(
                Category,
                Transaction.category_code == Category.code
            ).filter(
                Transaction.user_id == user_id,
                Transaction.type == TransactionType.EXPENSE,
                Transaction.date >= start_date,
                Transaction.date <= end_date
            ).group_by(
                Transaction.category_code,
                Category.name,
                Category.color
            ).order_by(
                desc('total')
            ).all()

            # Process results
            categories = []
            for category_code, category_name, color, total in results:
                amount = float(total)
                categories.append(
                    CategoryAmount(
                        category_code=category_code,
                        category_name=category_name,
                        amount=amount,
                        color=color
                    )
                )

            return categories

    async def get_cashflow_data(
        self,
        user_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[MonthCashflow]:
        with session_manager() as db:
            # If no period is given, use current year as default
            today = datetime.now().date()
            if not start_date or not end_date:
                start_date = today.replace(month=1, day=1)
                end_date = today.replace(month=12, day=31)

            # Query transactions with category code
            query = db.query(
                Transaction.date,
                Transaction.type,
                Transaction.amount,
                Transaction.description,
                Transaction.category_code
            ).filter(
                Transaction.user_id == user_id,
                Transaction.date >= start_date,
                Transaction.date <= end_date
            ).order_by(Transaction.date)

            results = query.all()

            # Group transactions by month
            cashflow_by_month: Dict[str, MonthCashflow] = {}

            for date_, type_, amount, description, category_code in results:
                month_str = date_.strftime('%Y-%m')

                if month_str not in cashflow_by_month:
                    cashflow_by_month[month_str] = MonthCashflow(
                        month=month_str)

                transaction = CashflowTransaction(
                    category_code=category_code,
                    description=description,
                    amount=float(amount),
                    date=date_
                )

                if type_ == TransactionType.INCOME:
                    cashflow_by_month[month_str].income.append(transaction)
                elif type_ == TransactionType.EXPENSE:
                    cashflow_by_month[month_str].expense.append(transaction)

            # Convert dictionary values to a sorted list
            sorted_cashflow = sorted(
                cashflow_by_month.values(), key=lambda x: x.month)

            return sorted_cashflow
