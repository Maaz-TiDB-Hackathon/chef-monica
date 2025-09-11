from sqlalchemy import create_engine, Column, Integer, Float, String, Boolean, DateTime, Table, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func
from tidb import tidb_client
from sqlalchemy.dialects.mssql import JSON

engine=tidb_client.db_engine
session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Association table for many-to-many relationship between users and roles
user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('role_id', Integer, ForeignKey('roles.id'))
)

class DBUser(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255))
    hashed_password = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    roles = relationship("DBRole", secondary=user_roles, back_populates="users")

class DBRole(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True)
    description = Column(String(255))

    users = relationship("DBUser", secondary=user_roles, back_populates="roles")

class DBChat(Base):
    __tablename__ = "chats"

    id = Column(String(255), primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    messages = Column(JSON)
    created_at = Column(DateTime, default=func.now())

# Create tables
Base.metadata.create_all(bind=engine)
