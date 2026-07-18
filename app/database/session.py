from typing import Annotated

from fastapi import Depends
from sqlalchemy import create_engine
from sqlmodel import SQLModel
from sqlalchemy.orm import Session


engine = create_engine(
    url="sqlite:///sqlite.db",
    echo=True,
    connect_args={
        "check_same_thread":False
    }
)
from .models import Shipment
def create_db_tables():

    SQLModel.metadata.create_all(bind=engine)

def get_session():
    with  Session(engine) as session:
        yield session

SessionDep=Annotated[Session,Depends(get_session)]