#importando ferramentas
from fastapi import FastAPI, Query


#Modulos
from database.connection import get_connection
from api.crud import get_generic_livros

#Modelos Pydantic
from models.livros import Livro_Generico



#criando o app
app = FastAPI(title="API Books to Scrape")




@app.get("/healthcheck")
def healthcheck():
    return {"status": "Isso é uma mensagem"}


@app.get("/healthdatabase")
def healthdatabase():
    try:
        conn = get_connection()
        result = conn.execute("SELECT 1").fetchone()
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        conn.close()
    return {"status": "Resultado com o banco saudável"}



@app.get("/livros", response_model=list[Livro_Generico])
def listar_livros(limit: int = Query(25, le=50), offset: int = Query(0, ge=0)):
    return get_generic_livros(limit=limit, offset=offset)