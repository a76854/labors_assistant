"""
SQLAlchemy ORM 数据库模型定义
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
import uuid
from backend.db.database import Base
from backend.utils.timezone import now_beijing


class Session(Base):
    """对话会话表"""
    __tablename__ = "sessions"
    
    # Primary Key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Foreign Keys & Properties
    user_id = Column(String(36), nullable=True, index=True)  # 可选，MVP可不实现用户认证
    case_type = Column(String(50), nullable=False)  # "wage_arrears", "labor_contract", "work_injury"
    status = Column(String(20), nullable=False, default="active")  # "new", "active", "completed", "closed"
    description = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=now_beijing, index=True)
    updated_at = Column(DateTime, nullable=False, default=now_beijing, onupdate=now_beijing)
    
    # Relationships
    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan")
    case_elements = relationship("CaseElement", back_populates="session", uselist=False, cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="session", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Session(id={self.id}, case_type={self.case_type}, status={self.status})>"


class Message(Base):
    """对话消息表"""
    __tablename__ = "messages"
    
    # Primary Key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Foreign Keys
    session_id = Column(String(36), ForeignKey("sessions.id"), nullable=False, index=True)
    
    # Properties
    role = Column(String(20), nullable=False)  # "user", "assistant"
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, nullable=False, default=now_beijing, index=True)
    
    # Relationships
    session = relationship("Session", back_populates="messages")
    
    def __repr__(self):
        return f"<Message(id={self.id}, role={self.role}, session_id={self.session_id})>"


class CaseElement(Base):
    """案件要素表（结构化数据）"""
    __tablename__ = "case_elements"
    
    # Primary Key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Foreign Keys
    session_id = Column(String(36), ForeignKey("sessions.id"), nullable=False, unique=True, index=True)
    
    # Properties - JSON存储结构化数据
    plaintiff_info = Column(JSON, nullable=True)  # 原告信息 {name, id_number, contact, ...}
    defendant_info = Column(JSON, nullable=True)  # 被告信息 {name, address, ...}
    facts = Column(JSON, nullable=True)  # 案件事实 ["事实1", "事实2", ...]
    claims = Column(JSON, nullable=True)  # 诉讼请求 [{type, amount, description}, ...]
    applicable_laws = Column(JSON, nullable=True)  # 适用法律 [{law, article, content}, ...]
    
    # Metadata
    confidence_score = Column(Float, nullable=True)  # 提取可信度 0.0-1.0
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=now_beijing)
    updated_at = Column(DateTime, nullable=False, default=now_beijing, onupdate=now_beijing)
    
    # Relationships
    session = relationship("Session", back_populates="case_elements")
    
    def __repr__(self):
        return f"<CaseElement(id={self.id}, session_id={self.session_id}, confidence={self.confidence_score})>"


class Document(Base):
    """生成的文档表"""
    __tablename__ = "documents"
    
    # Primary Key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Foreign Keys
    session_id = Column(String(36), ForeignKey("sessions.id"), nullable=False, index=True)
    
    # Properties
    template_id = Column(String(100), nullable=False)  # "wage_arrears", "labor_contract", "work_injury"
    title = Column(String(255), nullable=True)  # 诉状标题
    status = Column(String(20), nullable=False, default="pending")  # "pending", "generated", "exported"
    content = Column(Text, nullable=True)  # Word/HTML内容
    file_url = Column(String(500), nullable=True)  # 导出文件的URL/路径
    file_size = Column(Integer, nullable=True)  # 文件大小（字节）
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=now_beijing)
    updated_at = Column(DateTime, nullable=False, default=now_beijing, onupdate=now_beijing)
    
    # Relationships
    session = relationship("Session", back_populates="documents")
    
    def __repr__(self):
        return f"<Document(id={self.id}, template_id={self.template_id}, status={self.status})>"


class Template(Base):
    """诉讼模板表"""
    __tablename__ = "templates"
    
    # Primary Key
    id = Column(String(100), primary_key=True)  # "wage_arrears", "labor_contract", "work_injury"
    
    # Properties
    name = Column(String(255), nullable=False)  # 诉讼模板名称
    case_type = Column(String(50), nullable=False, index=True)  # 对应的案件类型
    description = Column(Text, nullable=True)  # 模板描述
    fields = Column(JSON, nullable=True)  # 模板所需字段列表 ["plaintiff_name", "defendant_name", ...]
    example_content = Column(Text, nullable=True)  # 示例内容
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=now_beijing)
    
    def __repr__(self):
        return f"<Template(id={self.id}, name={self.name})>"
