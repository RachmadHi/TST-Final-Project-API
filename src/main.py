# Tugas TST API 
# Nama  : Rachmad Hidayat
# NIM   : 18220049

from fastapi import FastAPI, Depends, HTTPException, Body, Form
from requests_html import HTMLSession
from pydantic import BaseModel, Field
import uvicorn
from .models import Product_data, Base
from .database import engine, SessionLocal
from sqlalchemy.orm import Session
from .auth.jwt_handler import signJSONWebToken
from .auth.jwt_bearer import JSONWebTokenBearer
from multipart import *

app = FastAPI()

Base.metadata.create_all(bind=engine)

def get_db():
    try :
        db = SessionLocal()
        yield db
    finally:
        db.close()

class UserSchema(BaseModel):
    email : str = Field(default = None)
    password : str = Field(default = None)
    class Config:
        the_schema = {
            "example" : {
                "email" : "user123@gmail.com",
                "password" : "12345678"
        
            }
        }

class UserLoginSchema(BaseModel):
    email : str = Field(default = None)
    password : str = Field(default = None)

    class Config:
        the_schema = {
            "example" : {
                "email" : "user123@gmail.com",
                "password" : "12345678"
        
            }
        }

def check_user(data : UserLoginSchema):
    for user in users :
        if user.email == data.email and user.password == data.password :
            return True
        else :
            return False
            
productlist = []
users = []

@app.get("/", tags=["Default"])
def root() :
    return ("Analisis Penjualan Toko Online")

@app.get("/read-data",  dependencies=[Depends(JSONWebTokenBearer())], tags=["Read Data"])
def read_data(db: Session = Depends(get_db)) :
    try :
        return db.query(Product_data).all()
    except :
        return ("Tidak Ada Data!")
 
@app.get("/read-data/{id}", dependencies=[Depends(JSONWebTokenBearer())], tags=["Read Data"])
def read_data(id : int, db: Session = Depends(get_db)) :
    return db.query(Product_data).filter(Product_data.id == id).first()

# Mengambil data dari salah satu toko di tokopedia
@app.get("/ambil-data",  dependencies=[Depends(JSONWebTokenBearer())], tags=["Ambil Data"])
async def get_data(link : str, db: Session = Depends(get_db)) :
    def parse_price(price_raw):
        price = ""
        for i in range (0, len(price_raw)):
            if price_raw[i].isdigit() :
                price += price_raw[i]
        return price

    def parse_terjual(terjual_raw):
        terjual = ""
        for i in range (0, len(terjual_raw)):
            if terjual_raw[i].isdigit() :
                terjual += terjual_raw[i]
        return terjual
    
    url = f"{link}"
    print(url)
    session = HTMLSession()
    r = session.get(url)

    product = r.html.find('div.css-1sn1xa2')
    for p in product:
        Nama = p.find('div.prd_link-product-name.css-svipq6', first = True).text.strip()
        Price_raw = p.find('div.prd_link-product-price.css-1ksb19c', first = True).text.strip()

        try :
            Terjual_raw = p.find('span.prd_label-integrity.css-1duhs3e', first = True).text.strip()
        except :
            Terjual_raw = "Terjual 0"
            print ("Data Penjualan Tidak Ditemukan")

        try :
            Rating = p.find('span.prd_rating-average-text.css-t70v7i', first = True).text.strip()
        except :
            Rating = "0.0"
            print ("Data Rating Tidak Ditemukan")
            
        Price = parse_price(Price_raw)
        Terjual = parse_terjual(Terjual_raw)

        item = {
            'Nama' : Nama,
            'Harga' : Price,
            'Terjual' : Terjual,
            'Rating' : Rating
        }
        productlist.append(item)

    for item in productlist:
        product_data_model = Product_data()
        product_data_model.nama = item['Nama']
        product_data_model.harga= item['Harga']
        product_data_model.terjual = item['Terjual']
        product_data_model.rating = item['Rating']
        
        db.add(product_data_model)
        db.commit()

    return productlist

@app.put("/update-data-penjualan", dependencies=[Depends(JSONWebTokenBearer())], tags=["Update Data"])
async def update_data(link : str, db : Session = Depends(get_db)):
    delete_data_penjualan(db)
    get_data(link, db)

@app.delete("/delete-all-data-penjualan", dependencies=[Depends(JSONWebTokenBearer())], tags=["Delete Data"])
async def delete_data_penjualan(db : Session = Depends(get_db)):
    for i in range (1, len(db.query(Product_data).all())+1):
        product_data_model = Product_data()
        product_data_model = db.query(Product_data).filter(Product_data.id == i).first()
        if product_data_model is not None:
            db.query(Product_data).filter(Product_data.id == product_data_model.id).delete()
    
    db.commit()
    return ("Semua data berhasil dihapus.")

@app.delete("/delete-data-penjualan/{id}", dependencies=[Depends(JSONWebTokenBearer())], tags=["Delete Data"])
async def delete_data_penjualan(id : int, db : Session = Depends(get_db)):
    product_data_model = Product_data()
    product_data_model = db.query(Product_data).filter(Product_data.id == id).first()
    if product_data_model is None:
        raise HTTPException(
            status_code=404,
            detail=f"ID {id} : Does not exist"
        )
    
    db.query(Product_data).filter(Product_data.id == id).delete()
    db.commit()

@app.get("/analisis-penjualan", dependencies=[Depends(JSONWebTokenBearer())],  tags=["Analisis Data"])
async def analisis_data_penjualan(db : Session = Depends(get_db)):

    count_data = len(db.query(Product_data).all())
    
    def total_penjualan():
        sum = 0
        for i in range (1, count_data):
            product_data_model = db.query(Product_data).filter(Product_data.id == i).first()
            sum += product_data_model.harga * product_data_model.terjual
        
        return sum
    
    def total_produk_terjual():
        sum = 0
        for i in range (1, count_data):
            product_data_model = db.query(Product_data).filter(Product_data.id == i).first()
            sum += product_data_model.terjual
        
        return sum   

    def mean_penjualan() :
        sum = 0
        for i in range (1, count_data):
            product_data_model = db.query(Product_data).filter(Product_data.id == i).first()
            sum += product_data_model.harga * product_data_model.terjual
        
        mean = sum/count_data
        return mean 

    def mean_produk_terjual() :
        sum = 0
        for i in range (1, count_data):
            product_data_model = db.query(Product_data).filter(Product_data.id == i).first()
            sum += product_data_model.terjual
        
        mean = sum/count_data
        return mean 

    def produk_terlaris():
        produk_terlaris = db.query(Product_data).filter(Product_data.id == 1).first()
        for i in range (2, count_data):
            product_data_model = db.query(Product_data).filter(Product_data.id == i).first()
            if product_data_model.terjual >= produk_terlaris.terjual :
                produk_terlaris = product_data_model

        return produk_terlaris.nama

    def total_penjualan_produk_terlaris():
        produk_terlaris = db.query(Product_data).filter(Product_data.id == 1).first()
        for i in range (2, count_data):
            product_data_model = db.query(Product_data).filter(Product_data.id == i).first()
            if product_data_model.terjual >= produk_terlaris.terjual :
                produk_terlaris = product_data_model

        return produk_terlaris.terjual
    
    def proyeksi_penjualan() :
        proyeksi_penjualan = (mean_penjualan() * mean_produk_terjual())/12
        return proyeksi_penjualan

    item_analisis_penjualan = {
        "Total Penjualan" : "Rp"+ str(total_penjualan()),
        "Rata-rata Penjualan" : "Rp" + str(mean_penjualan()),
        "Total Produk Terjual" : total_produk_terjual(),
        "Rata-rata Produk Terjual" : round(mean_produk_terjual()),
        "------------------------------------------" : "------------------------------------------",
        "Produk Terlaris" : produk_terlaris(),
        "Total Penjualan Produk Terlaris" : total_penjualan_produk_terlaris(),
        "------------------------------------------" : "------------------------------------------",
        "Proyeksi Penjualan Bulan Depan" : "Rp" + str(round(proyeksi_penjualan(), 3)),
    }

    return item_analisis_penjualan

@app.post("/user/signup", tags=["User"])
def user_signup(email : str = Form(default=None), password : str = Form(default=None)):
    user = UserSchema()
    user.email = email
    user.password = password
    users.append(user)
    return signJSONWebToken(user.email)

@app.post("/user/login", tags=["User"])
def user_login(email : str = Form(default=None), password : str = Form(default=None)):
    user = UserLoginSchema()
    user.email = email
    user.password = password
    if check_user(user):
        return signJSONWebToken(user.email)
    else :
        return {
            "error" : "Invalid login!"
        }

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8080)