# Tugas TST API 
# Nama  : Rachmad Hidayat
# NIM   : 18220049

from fastapi import FastAPI, Depends, HTTPException, Body, Form
from requests_html import HTMLSession
from pydantic import BaseModel, Field
import uvicorn
from models import Product_data, Base
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from auth.jwt_handler import signJSONWebToken
from auth.jwt_bearer import JSONWebTokenBearer

app = FastAPI()

Base.metadata.create_all(bind=engine)

def get_db():
    try :
        db = SessionLocal()
        yield db
    finally:
        db.close()

class Product_data(BaseModel):
    nama : str
    harga : int
    terjual : int
    rating : float

class UserSchema(BaseModel):
    username : str = Field(default = None)
    email : str = Field(default = None)
    password : str = Field(default = None)

    class Config:
        the_schema = {
            "example" : {
                "name" : "User",
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

@app.get("/", dependencies=[Depends(JSONWebTokenBearer())], tags=["Default"])
def root() :
    return ("Analisis Penjualan Toko Online")

@app.get("/read-data", dependencies=[Depends(JSONWebTokenBearer())], tags=["Read Data"])
def read_data(db: Session = Depends(get_db)) :
    return db.query(Product_data).all()
 
@app.get("/read-data/{id}", dependencies=[Depends(JSONWebTokenBearer())], tags=["Read Data"])
def read_data(id : int, db: Session = Depends(get_db)) :
    return db.query(Product_data).filter(Product_data.id == id).first()

# Mengambil data dari salah satu toko di tokopedia
@app.get("/ambil-data", dependencies=[Depends(JSONWebTokenBearer())],  tags=["Ambil Data"])
async def get_data(link : str, db: Session = Depends(get_db)) :
    def parse_price(price_raw):
        if price_raw[5]==("."):
            return price_raw[3:5]+price_raw[6:9]
        elif price_raw[4] == ("."):
            return price_raw[3]+price_raw[5:8]
        else :
            return price_raw[3:6]+price_raw[7:10]
    
    def parse_terjual(terjual_raw):
        if len(terjual_raw) >= 11 :
            if terjual_raw[9] == "r" :
                return terjual_raw[8] * 1000
            elif terjual_raw[10] == "+" :
               return terjual_raw[8:10]
            elif terjual_raw[11] == "+" :
               return terjual_raw[8:11]
            return terjual_raw[8:]
        else :
            return terjual_raw[8:]
    
    url = f"{link}"
    print(url)
    session = HTMLSession()
    r = session.get(url)

    product = r.html.find('div.css-1sn1xa2')

    for p in product:
        Nama = p.find('div.prd_link-product-name.css-svipq6', first = True).text.strip()
        Price_raw = p.find('div.prd_link-product-price.css-1ksb19c', first = True).text.strip()

        if p.find('span.prd_label-integrity.css-1duhs3e', first = True).text.strip() is not None :
            Terjual_raw = p.find('span.prd_label-integrity.css-1duhs3e', first = True).text.strip()
        else :
            Terjual_raw = 0

        if p.find('span.prd_rating-average-text.css-t70v7i', first = True).text.strip() is not None :
            Rating = p.find('span.prd_rating-average-text.css-t70v7i', first = True).text.strip()
        else :
            Rating = 0.0
        
        Price = parse_price(Price_raw)
        Terjual = parse_terjual(Terjual_raw)

        item = {
            'Nama' : Nama,
            'Harga' : Price,
            'Terjual' : Terjual,
            'Rating' : Rating
        }
        productlist.append(item)

    product_data_model = Product_data()
    for item in productlist:
        product_data_model = Product_data()
        product_data_model.nama = str(Nama)
        product_data_model.harga= Price
        product_data_model.terjual = Terjual
        product_data_model.rating = Rating
        
        db.add(product_data_model)
        db.commit()

    return productlist

# @app.put("/update-data-penjualan")
# async def update_data():
    #for 


# @app.delete("delete-data-penjualan/{id}", dependencies=[Depends(JSONWebTokenBearer())], tags=["Delete Data"])
# async def delete_data_penjualan(id : int, db : Session = Depends(get_db)):

#     product_data_model = db.query(Product_data).filter(Product_data.id == id).first()
#     print(product_data_model)
#     if product_data_model is None:
#         raise HTTPException(
#             status_code=404,
#             detail=f"ID {id} : Does not exist"
#         )
    
#     db.query(Product_data).filter(Product_data.id == id).delete()
#     db.commit()

@app.get("/analisis-penjualan", dependencies=[Depends(JSONWebTokenBearer())], tags=["Analisis Data"])
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

    def produk_terlaris():
        produk_terlaris = db.query(Product_data).filter(Product_data.id == 1).first()
        for i in range (2, count_data):
            product_data_model = db.query(Product_data).filter(Product_data.id == i).first()
            if product_data_model.terjual >= produk_terlaris.terjual :
                produk_terlaris = product_data_model

        return produk_terlaris.nama

    item_analisis_penjualan = {
        "Total Penjualan" : total_penjualan(),
        "Total Produk Terjual" : total_produk_terjual(),
        "Produk Terlaris" : produk_terlaris(),
    }

    return item_analisis_penjualan

@app.post("/user/signup", tags=["User"])
def user_signup(user : UserSchema = Body(default=None)):
    users.append(user)
    return signJSONWebToken(user.email)

@app.post("/user/login", tags=["User"])
def user_login(user : UserLoginSchema = Body(default=None)):
    if check_user(user):
        return signJSONWebToken(user.email)
    else :
        return {
            "error" : "Invalid login!"
        }

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8080)