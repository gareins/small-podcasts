from sqlalchemy import Column, Integer, String, Boolean, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True)
    url = Column(String(250), nullable=False)
    type = Column(String(10), nullable=False)  # audio or xml
    filename = Column(String(250))
    modified = Column(Boolean)
    last_accessed = Column(Date)
    created = Column(Date)

    def __repr__(self):
        return "{} : {}".format(self.url, self.modified)

# Create an engine that stores data in the local directory's
# sqlalchemy_example.db file.
engine = create_engine('sqlite:///tsst.db')

# Create all tables in the engine. This is equivalent to "Create Table"
# statements in raw SQL.
Base.metadata.create_all(engine)

# Create Session maker
Session = sessionmaker(bind=engine)
