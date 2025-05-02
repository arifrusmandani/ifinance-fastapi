from datetime import datetime, timedelta
from sqlalchemy import text
from app.src.base.crud import CRUDBase
from app.src.database.session import session_manager


class CRUDDownload():

    async def get_assignment_data(self, fc_id: int):
        with session_manager() as db:
            query = text("""
                SELECT 
                    id, 
                    customer_number AS customer_no, 
                    field_collector, 
                    status, 
                    target, 
                    remark, 
                    route_order, 
                    last_assigned_at AS created_at
                FROM 
                    task_assignment
                WHERE 
                    field_collector = :field_collector
            """)
            result = db.execute(query, {"field_collector": fc_id})
            rows = result.fetchall()
            columns = result.keys()

            return columns, rows


    async def get_agreement_data(self, fc_id: int):
        with session_manager() as db:
            query = text("""
                SELECT ao.*, b.short_name AS branch_short_name
                FROM agreement_overdue ao
                LEFT JOIN (
                    SELECT DISTINCT ON (code) code, short_name
                    FROM branch
                ) b ON ao.branch_code = b.code
                WHERE ao.customer_no IN (
                    SELECT ta.customer_number
                    FROM task_assignment ta
                    WHERE ta.field_collector = :field_collector
                )
                AND ao.cis_status NOT IN ('WAITING_FOR_ASSIGNMENT', 'AUTO_ASSIGNMENT_FAILED')
            """)

            result = db.execute(query, {"field_collector": fc_id})
            rows = result.fetchall()
            columns = result.keys()

            return columns, rows

    async def get_customer_data(self, fc_id: int):
        with session_manager() as db:
            query = text("""
                SELECT 
                    c.id,
                    c.customer_no,
                    c.name,
                    c.nik,
                    c.mobile_phone_1 as phone_number,
                    c.street,
                    c.sub_district,
                    c.district,
                    c.province,
                    c.city,
                    c.rt,
                    c.rw,
                    c.zip_code,
                    c.geopoint
                FROM customers c
                WHERE c.customer_no IN (
                    SELECT ta.customer_number
                    FROM task_assignment ta
                    WHERE ta.field_collector = :field_collector
                )
            """)

            result = db.execute(query, {"field_collector": fc_id})
            rows = result.fetchall()
            columns = result.keys()

            return columns, rows

    async def get_agreement_asset_data(self, fc_id: int):
        with session_manager() as db:
            query = text("""
                SELECT
                    ao.customer_no,
                    aa.agr_agreement_id,
                    aa.asset_name,
                    aa.chasis_number,
                    aa.tag_number,
                    aa.asset_brand
                FROM agreement_asset aa
                JOIN agreement_overdue ao ON aa.agr_agreement_id = ao.agreement_number
                WHERE ao.customer_no IN (
                    SELECT ta.customer_number
                    FROM task_assignment ta
                    WHERE ta.field_collector = :field_collector
                );
            """)

            result = db.execute(query, {"field_collector": fc_id})
            rows = result.fetchall()
            columns = result.keys()

            return columns, rows

    async def get_followup_result_data(self, fc_id: int, current_month: int, current_year: int):
        with session_manager() as db:
            query = text("""
                SELECT fr.*
                    FROM followup_result fr
                    WHERE fr.customer_no IN (
                        SELECT ta.customer_number
                        FROM task_assignment ta
                        WHERE ta.field_collector = :fc_id
                        AND ta.status != 'CLOSED'
                    )
                    AND EXTRACT(MONTH FROM fr.visit_date) = :current_month
                    AND EXTRACT(YEAR FROM fr.visit_date) = :current_year;
            """)

            # Execute the query, passing parameters as a dictionary
            result = db.execute(query, {"fc_id": fc_id, "current_month": current_month, "current_year": current_year})
            rows = result.fetchall()
            columns = result.keys()

            return columns, rows

    async def get_customer_history_data(self, fc_id: int):
        thirty_days_ago = datetime.now() - timedelta(days=30)

        with session_manager() as db:
            query = text("""
                SELECT ch.*
                FROM customer_history ch
                LEFT JOIN followup_session fs ON ch.followup_session_id = fs.id
                WHERE ch.customer_no IN (
                    SELECT ta.customer_number
                    FROM task_assignment ta
                    WHERE ta.field_collector = :fc_id
                )
                AND ch.created_at >= :thirty_days_ago
                AND fs.end_event_id IS NOT NULL
                AND fs.is_canceled = FALSE
            """)

            result = db.execute(query, {"fc_id": fc_id, "thirty_days_ago": thirty_days_ago})
            rows = result.fetchall()
            columns = result.keys()

            return columns, rows

    async def get_ptp_followup_result_data(self, fc_id: int):
        with session_manager() as db:
            query = text("""
                SELECT 
                    ta.id,
                    (CASE WHEN ta.last_assigned_at is not null 
                        THEN ta.last_assigned_at
                        ELSE ta.created_at
                    END) assigned_at,
                    fr.*
                FROM task_assignment ta
                JOIN followup_result fr ON fr.customer_no = ta.customer_number
                JOIN (
                    SELECT
                        followup_result.agreement_id as agreement_id,
                        followup_result.customer_no as customer_no,
                        max(followup_result.visit_date) as latest_visit_date
                    FROM
                        followup_result
                    JOIN followup_session ON followup_session.id = followup_result.followup_session_id
                    WHERE
                        followup_session.end_event_id IS NOT NULL
                    GROUP BY 
                        followup_result.agreement_id, 
                        followup_result.customer_no
                ) AS latest_followup ON latest_followup.customer_no = fr.customer_no
                    AND latest_followup.latest_visit_date = fr.visit_date
                WHERE ta.field_collector = :fc_id
            """)

            # Execute the query, passing parameters as a dictionary
            result = db.execute(query, {"fc_id": fc_id})
            rows = result.fetchall()
            columns = result.keys()

            return columns, rows