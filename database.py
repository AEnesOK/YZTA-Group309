from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

# Ücretsiz ve yerel SQLite veri tabanı bağlantı adresi
DATABASE_URL = "sqlite:///./ai_peer.db"

# Veri tabanı motorunu oluşturuyoruz
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 1. KULLANICI TABLOSU
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    
    posts = relationship("CodePost", back_populates="owner")
    comments = relationship("Comment", back_populates="author")

# 2. YÜKLENEN KODLARIN TABLOSU
class CodePost(Base):
    __tablename__ = "code_posts"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(Text)  # Kullanıcının yüklediği ham kod bloğu
    language = Column(String)  # Python, JS, C++ vb.
    created_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post")
    ai_reviews = relationship("AIReview", back_populates="post")

# 3. KULLANICI YORUMLARI TABLOSU
class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text)  # Kullanıcının kod hakkındaki analizi/yorumu
    created_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"))
    post_id = Column(Integer, ForeignKey("code_posts.id"))

    author = relationship("User", back_populates="comments")
    post = relationship("CodePost", back_populates="comments")
    ai_reviews = relationship("AIReview", back_populates="comment")

# 4. YAPAY ZEKA (LLM) DEĞERLENDİRMELERİ TABLOSU
class AIReview(Base):
    __tablename__ = "ai_reviews"
    id = Column(Integer, primary_key=True, index=True)
    review_text = Column(Text)  # LLM'den gelen detaylı analiz metni
    score = Column(Integer, nullable=True)  # LLM'in verdiği puan (Örn: 1-10 arası)
    target_type = Column(String)  # "post" (kod için) veya "comment" (yorum incelemesi için)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    post_id = Column(Integer, ForeignKey("code_posts.id"), nullable=True)
    comment_id = Column(Integer, ForeignKey("comments.id"), nullable=True)

    post = relationship("CodePost", back_populates="ai_reviews")
    comment = relationship("Comment", back_populates="ai_reviews")

# Veri tabanı oturumu açıp kapatmak için yardımcı fonksiyon
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()