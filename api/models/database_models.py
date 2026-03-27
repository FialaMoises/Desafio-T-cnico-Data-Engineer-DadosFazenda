from sqlalchemy import Column, Integer, String, Numeric, TIMESTAMP, ForeignKey, CheckConstraint, UniqueConstraint, CHAR, Text
from sqlalchemy.orm import relationship, DeclarativeBase
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    pass


class Imovel(Base):
    __tablename__ = "imoveis"

    id = Column(Integer, primary_key=True)
    codigo_incra = Column(String(17), unique=True, nullable=False, index=True)
    nome_imovel = Column(Text, nullable=True)
    uf = Column(CHAR(2), nullable=False, index=True)
    municipio = Column(Text, nullable=False, index=True)
    area_ha = Column(Numeric(12, 4), nullable=True)
    situacao = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    vinculos = relationship("Vinculo", back_populates="imovel", cascade="all, delete-orphan")


class Pessoa(Base):
    __tablename__ = "pessoas"

    id = Column(Integer, primary_key=True)
    cpf = Column(String(14), unique=True, nullable=False, index=True)
    nome_completo = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    vinculos = relationship("Vinculo", back_populates="pessoa")


class Vinculo(Base):
    __tablename__ = "vinculos"

    id = Column(Integer, primary_key=True)
    imovel_id = Column(Integer, ForeignKey("imoveis.id", ondelete="CASCADE"), nullable=False, index=True)
    pessoa_id = Column(Integer, ForeignKey("pessoas.id", ondelete="CASCADE"), nullable=False, index=True)
    tipo_vinculo = Column(Text, nullable=False)
    participacao_pct = Column(Numeric(5, 2), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    imovel = relationship("Imovel", back_populates="vinculos")
    pessoa = relationship("Pessoa", back_populates="vinculos")

    __table_args__ = (
        UniqueConstraint("imovel_id", "pessoa_id", "tipo_vinculo", name="uq_vinculo"),
        CheckConstraint("tipo_vinculo IN ('Proprietário', 'Arrendatário')", name="check_tipo_vinculo"),
        CheckConstraint("participacao_pct >= 0 AND participacao_pct <= 100", name="check_participacao_pct"),
    )
