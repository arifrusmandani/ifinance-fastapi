from typing import List, Optional, Dict
from datetime import date, datetime, timedelta
from sqlalchemy import func, desc, extract
from app.src.database.models.transaction import Transaction, TransactionType
from app.src.router.report.crud import CRUDReport
from app.src.database.session import session_manager
from app.src.router.report.schema import CategoryReport, MonthlyChartData, DashboardSummaryItem


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
                return ((current - previous) / abs(previous)) * 100

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
