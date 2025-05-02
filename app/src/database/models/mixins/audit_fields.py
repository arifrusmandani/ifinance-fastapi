from datetime import datetime

from sqlalchemy import Column, DateTime, String


class DeletedFieldsMixin(object):
    deleted_date = Column(DateTime)
    deleted_by = Column(String(64), default='')


class AuditFieldsMixin(DeletedFieldsMixin):
    created_date = Column(DateTime, default=datetime.now)
    created_by = Column(String(64), default='')
    updated_date = Column(DateTime, onupdate=datetime.now)
    updated_by = Column(String(64), default='')
