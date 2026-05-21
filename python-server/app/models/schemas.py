from sqlalchemy import Column, BigInteger, String, Text, DateTime, Integer, Enum as SAEnum
from sqlalchemy.sql import func
from app.models.database import Base
import enum


class Platform(str, enum.Enum):
    NAVER = "naver"
    INSTAGRAM = "instagram"


class PostStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    PUBLISHED = "published"
    FAILED = "failed"


class PostHistory(Base):
    __tablename__ = "post_history"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    platform = Column(SAEnum(Platform), nullable=False)
    input_type = Column(String(20), nullable=False)  # keyword | image
    input_keyword = Column(Text)
    generated_title = Column(Text)
    generated_content = Column(Text)
    generated_hashtags = Column(Text)  # JSON array as string
    published_url = Column(Text)
    status = Column(SAEnum(PostStatus), nullable=False, default=PostStatus.PENDING)
    retry_count = Column(Integer, default=0)
    error_message = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
