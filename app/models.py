from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Dictionary(Base):
    __tablename__ = 'dictionary'
    id = Column(Integer, primary_key=True, autoincrement=True)
    haka = Column(String, nullable=False)  # ҺАКАЛЫЫ
    sakha = Column(String, nullable=False)  # САХАЛЫЫ
    nuuchcha = Column(String, nullable=False)  # НЬУУЧЧАЛЫЫ
    sim = Column(Float, nullable=True)  # SIM
    haka_ex = Column(String, nullable=True)  # ҺАКАЛЫЫ_ex
    sakha_ex = Column(String, nullable=True)  # САХАЛЫЫ_ex
    nuuchcha_ex = Column(String, nullable=True)  # НЬУУЧЧАЛЫЫ_ex
    group = Column(String, nullable=True)  # GROUP
