from sqlalchemy.orm import declarative_base
SqlAlchemyBase = declarative_base() 

# this creates a base class that links python classes to the
# db tables in sqlalchemy 
# any model class that inerits from 
# Base is directly registeres as a database table .
 