import typer
from app.database import create_db_and_tables, get_session, drop_all
from app.models import User
from fastapi import Depends
from sqlmodel import select
from sqlalchemy.exc import IntegrityError

cli = typer.Typer()

@cli.command()
def initialize():
    with get_session() as db: # Get a connection to the database
        drop_all() # delete all tables
        create_db_and_tables() #recreate all tables
        bob = User(username = 'bob', email = 'bob@mail.com', password = 'bobpass') # Create a new user (in memory)
        db.add(bob) # Tell the database about this new data
        db.commit() # Tell the database persist the data
        db.refresh(bob) # Update the user (we use this to get the ID from the db)

        john = User(username='john', email='john@gmail.com', password='johnpass')
        db.add(john)
        db.commit()
        db.refresh(john)

        print("Database Initialized")

@cli.command()
def get_user(username:str):
    with get_session() as db: # Get a connection to the database
        user = db.exec(select(User).where(User.username == username)).first()
        if not user:
            print(f'{username} not found!')
            return
        print(user)


@cli.command()
def get_all_users():
    with get_session() as db:
        all_users = db.exec(select(User)).all()
        if not all_users:
            print("No users found")
        else:
            for user in all_users:
                print(user)
   

@cli.command()
def change_email(username: str, new_email:str):
    with get_session() as db:
        user = db.exec(select(User).where(User.username == username)).first()
        if not user:
            print(f"{username} does not exist")
            return
        
        user.email = new_email
        db.add(user)
        db.commit()
        print(f"Updated {user.username}'s email to {user.email}")
            
   
@cli.command()
def create_user(new_username: str, new_email:str, new_password: str):
    with get_session() as db:
        newUser = User(username=new_username, email=new_email, password=new_password)
        try:
            db.add(newUser)
            db.commit()
            db.refresh(newUser)
        except IntegrityError as e:
            db.rollback()
            print(e.orig)
            print("Username or email already taken!")
        else:
            print("Succesfully added new user!")
            print(newUser)


@cli.command()
def delete_user(username: str):
    with get_session() as db:
        user = db.exec(select(User).where(User.username == username)).first()
        if not user:
            print(f"User {username} does not exist")
            return
        db.delete(user)
        db.commit()
        print(f"Successfully deleted user {username}")


if __name__ == "__main__":
    cli()