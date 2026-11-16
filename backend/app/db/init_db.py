from app.db.base import Base
from app.db.session import engine
from app.models.user import Users

def create_table():
    Base.metadata.create_all(bind=engine)
    print("database table created successfully!")
    
if __name__=="__main__":
    create_table()