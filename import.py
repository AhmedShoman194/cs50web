import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import csv


# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

f = open("books.csv")
reader = csv.reader(f)
for isbn, title, author, year in reader:
    db.execute("INSERT INTO books (isbn, title, auther, year) VALUES (:x, :y, :z, :v)", {"x": isbn, "y": title, "z": author, "v": year})

db.commit()
