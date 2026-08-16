import uuid# it means Unique ids
from datetime import datetime 

from sqlalchemy import DateTime, ForeignKey, String , UniqueConstraint, func
from sqlalchemy.dailects.postgres import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

""" Import	Why
String, DateTime-->column types
ForeignKey-->link environment → organization
UniqueConstraint-->prevent duplicate env slugs per org
func-> DB functions like now() for timestamps UUID
Postgres-native UUID column type
Mapped, mapped_column --> modern SQLAlchemy way to define columns
relationship--> ython navigation between related tables
"""
from database import base
class Organization(Base):
    __tablename__="organizations"
    id:Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(225),nullable=False)
    slug: Mapped[str] = mapped_column(String(225), nullable=False, unique=True,index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime=True)

