import uuid# it means Unique ids
from datetime import datetime 

from sqlalchemy import DateTime, ForeignKey, String , UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

""" Import	Why
String, DateTime-->column types
ForeignKey-->link environment → organization
UniqueConstraint-->prevent duplicate env slugs per org
func-> DB functions like now() for timestamps UUID
Postgres-native UUID column type
Mapped, mapped_column --> modern SQLAlchemy way to define columns
relationship--> python navigation between related tables
"""
from app.database import Base
class Organization(Base):
    __tablename__="organizations"
    id:Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(225),nullable=False)
    slug: Mapped[str] = mapped_column(String(225), nullable=False, unique=True,index=True)#slug is a unique identifier for the organization small name used in URL
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    environments: Mapped[list["Environment"]]= relationship(back_populates="organization",cascade="all, delete-orphan")



class Environment(Base):
    __tablename__="environments"# table name
    __table_args__=(UniqueConstraint("organization_id","slug",name="uq-environment_org_slug"),#unique constraint for the environment slug and organization id
    )#this is a unique constraint for the environment slug and organization id
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID]= mapped_column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"),index=True,nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime]= mapped_column(DateTime(timezone=True),nullable=False, server_default=func.now())
    organization: Mapped["Organization"] = relationship(back_populates="environments")#relationship to the organization table this is the parent of the environment table 


