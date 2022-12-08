from sqlalchemy import Column, Integer, String, Float
from database import Base

class Product_data(Base) :
    __tablename__ = "data_penjualan"

    id = Column(Integer, primary_key=True, index=True)
    nama = Column(String)
    harga = Column(Integer)
    terjual = Column(Integer)
    rating = Column(Float)