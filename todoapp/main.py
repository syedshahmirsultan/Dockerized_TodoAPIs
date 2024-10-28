from fastapi import FastAPI,Depends,HTTPException
from sqlmodel import SQLModel,Field,create_engine,Session, select
import os
from typing import Annotated,List




class Todo(SQLModel,table=True):
    id:int = Field(default=None,primary_key=True)
    content:str = Field(default=None,min_length=3,max_length=500)
    is_completed :bool = Field(default=False)

connection_string = os.getenv("POSTGRESQL_CONNECTION_STRING").replace("postgresql","postgresql+psycopg2")
engine = create_engine(connection_string)

def create_tables(app:FastAPI):
    SQLModel.metadata.create_all(engine)
    yield
    

def get_session():
    with Session(engine) as session:
        yield session


app :FastAPI = FastAPI(lifespan=create_tables)


# API for getting all items 
@app.get("/todo",response_model=List[Todo])
def get_all(session:Annotated[Session,Depends(get_session)]):
    todos = session.exec(select(Todo)).all()
    return todos
  

# API for Adding new item in the Database
@app.post("/todo")
def add_item(todo:Todo,session:Annotated[Session,Depends(get_session)]):
    session.add(todo)
    session.commit()
    session.refresh(todo)
    return todo

# API for updating existing items
@app.put("/todo/{id}",response_model=Todo)
def updating_item(id:int,todo:Todo,session:Annotated[Session,Depends(get_session)]):
    existing_todo = session.get(Todo,id)
    
    if existing_todo:
        existing_todo.content = todo.content
        existing_todo.is_completed = todo.is_completed
        session.commit()
        session.refresh(existing_todo)
        return existing_todo
        
    else:
        raise HTTPException(status_code=404,detail="Item not found")
    
    


# API for deleting item
@app.delete("/todo/{id}")
def delete_item(id:int,session:Annotated[Session,Depends(get_session)]):
   todo = session.get(Todo,id)
   if todo:
       session.delete(todo)
       session.commit()
       return "Item deleted successfully"
   else:
       raise HTTPException(status_code=404,detail="Item not found")