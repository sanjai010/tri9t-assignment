from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

DATABASE_URL = "sqlite:///./app.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    versions = relationship("DocumentVersion", back_populates="document")


class DocumentVersion(Base):
    __tablename__ = "document_versions"
    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    version_number = Column(Integer)
    pdf_path = Column(String)
    document = relationship("Document", back_populates="versions")
    nodes = relationship("Node", back_populates="version")


class Node(Base):
    __tablename__ = "nodes"
    id = Column(Integer, primary_key=True)
    version_id = Column(Integer, ForeignKey("document_versions.id"))
    section_number = Column(String)
    heading = Column(Text)
    level = Column(Integer)
    body = Column(Text)
    parent_id = Column(Integer, nullable=True)
    content_hash = Column(String)
    version = relationship("DocumentVersion", back_populates="nodes")


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()