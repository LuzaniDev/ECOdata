import hashlib
import os
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

_root = os.getenv("ECODATA_ROOT", os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
DB_DIR = os.path.join(_root, "data")
os.makedirs(DB_DIR, exist_ok=True)
DB_PATH = os.path.join(DB_DIR, "server.db")
DATABASE_URL = os.getenv("ECODATA_DB_URL", f"sqlite:///{DB_PATH}")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass


class Execution(Base):
    __tablename__ = "executions"
    id = Column(Integer, primary_key=True)
    tipo = Column(String(50), nullable=False, index=True)
    status = Column(String(20), default="running")
    started_at = Column(DateTime, default=datetime.now)
    finished_at = Column(DateTime, nullable=True)
    duration_ms = Column(Integer, nullable=True)
    file_path = Column(String(500), nullable=True)
    file_hash = Column(String(64), nullable=True)
    rows_count = Column(Integer, nullable=True)
    file_size = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)
    output_log = Column(Text, nullable=True)
    created_by = Column(String(100), default="system")
    empresa_utilizada = Column(String(20), nullable=True)
    empresa_nome = Column(String(200), nullable=True)
    available_companies = Column(Text, nullable=True)


class Schedule(Base):
    __tablename__ = "schedules"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    tipo = Column(String(50), nullable=False)
    cron_expression = Column(String(100), nullable=True)
    interval_minutes = Column(Integer, nullable=True)
    enabled = Column(Boolean, default=True)
    use_windows_scheduler = Column(Boolean, default=False)
    send_sftp = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)
    last_run = Column(DateTime, nullable=True)
    next_run = Column(DateTime, nullable=True)


class LogEntry(Base):
    __tablename__ = "logs"
    id = Column(Integer, primary_key=True)
    level = Column(String(20), default="INFO")
    message = Column(Text, nullable=False)
    source = Column(String(100), default="system")
    created_at = Column(DateTime, default=datetime.now)


class AuditLog(Base):
    __tablename__ = "audit_log"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=True)
    username = Column(String(100), default="system")
    action = Column(String(50), nullable=False)
    resource_type = Column(String(50), nullable=False)
    resource_id = Column(String(100), nullable=True)
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now)


class BackupRecord(Base):
    __tablename__ = "backups"
    id = Column(Integer, primary_key=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=True)
    tipo = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.now)


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True, nullable=False)
    api_key_hash = Column(String(128), nullable=False)
    role = Column(String(20), default="viewer")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)


def hash_api_key(api_key: str) -> str:
    return hashlib.sha256(api_key.encode()).hexdigest()


def verify_api_key(api_key: str, api_key_hash: str) -> bool:
    return hash_api_key(api_key) == api_key_hash


def init_db():
    Base.metadata.create_all(bind=engine)


def get_session():
    return SessionLocal()