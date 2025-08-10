#FASTAPI
from fastapi import FastAPI, Query, Depends
from fastapi.security import OAuth2PasswordBearer


#Modulos
from database.connection import get_connection
from api.crud import get_generic_livros

#Modelos Pydantic
from models.livros import Livro_Generico, Response_Livro_Generico
from models.user import User

#typing
from typing import Annotated

#criando o app
app = FastAPI(title="API Books to Scrape")

@app.get("/health")
def healthcheck():
    return {"status": "Healthy"}

@app.get("/healthdatabase")
def healthdatabase():
    try:
        conn = get_connection()
        result = conn.execute("SELECT * FROM livros LIMIT 1").fetchone()
        return {"status": "Healthy"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    

@app.get("/livros", response_model=Response_Livro_Generico)
def listar_livros(limit: int = Query(25, le=50), offset: int = Query(0, ge=0)):
    return get_generic_livros(limit=limit, offset=offset)