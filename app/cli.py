import typer
from app.database import create_db_and_tables, get_session, drop_all
from app.models import User
from fastapi import Depends
from sqlmodel import select, or_
from sqlalchemy.exc import IntegrityError
from typing import Annotated

cli = typer.Typer()

@cli.command()
def initialize():
    '''
    Initialize the database and create user
    '''
    with get_session() as db: # Get a connection to the database
        drop_all() # delete all tables
        create_db_and_tables() #recreate all tables
        bob = User(username = 'bob', email = 'bob@mail.com', password = 'bobpass') # Create a new user (in memory)
        db.add(bob) # Tell the database about this new data
        db.commit() # Tell the database persist the data
        db.refresh(bob) # Update the user (we use this to get the ID from the db)
        print("Database Initialized")


@cli.command()
def get_user(
    username: Annotated[str, typer.Argument(help="Username to be searched")]
    ):
    '''
    Retrieve user by username and print
    '''
    with get_session() as db: # Get a connection to the database
        user = db.exec(select(User).where(User.username == username)).first()
        if not user:
            print(f'{username} not found!')
            return
        print(user)


@cli.command()
def get_all_users():
    '''
    Retrieve all users
    '''
    with get_session() as db:
        all_users = db.exec(select(User)).all()
        if not all_users:
            print("No users found")
        else:
            for user in all_users:
                print(user)
   

@cli.command()
def change_email(
    username: Annotated[str, typer.Argument(help="User whose email is to be changed")],
    new_email: Annotated[str, typer.Argument(help="New email")]
    ):
    '''
    Update the email of an existing user
    '''
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
def create_user(
    new_username: Annotated[str, typer.Argument(help="Username for new user")],
    new_email: Annotated[str,typer.Argument(help="Email for new user")],
    new_password: Annotated[str, typer.Argument(help="Password for new user")]
    ):
    '''
    Create new user and add to database
    '''
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
def delete_user(
    username: Annotated[str, typer.Argument(help="Username of user to be deleted")]
    ):
    '''
    Delete existing user
    '''
    with get_session() as db:
        user = db.exec(select(User).where(User.username == username)).first()
        if not user:
            print(f"User {username} does not exist")
            return
        db.delete(user)
        db.commit()
        print(f"Successfully deleted user {username}")


@cli.command()
def get_user_partial(
    name: Annotated[str, typer.Argument(help="Partial username/email of user to retrieve")]
    ):
    '''
    Retrieve user using partial match of username OR email
    '''

    with get_session() as db:
        user = db.exec(select(User).where(
            or_(
                User.username.ilike(f"%{name}%"),
                User.email.ilike(f"%{name}%")))).first()
        if not user:
            print("No matches found")
            return
        print(user)


@cli.command()
def get_range(
    offset: Annotated[int, typer.Argument(help="Starting point")] = 0,
    limit: Annotated[int, typer.Argument(help="Number of users to retrieve")] = 10
 ):
    '''
    Retrieve first N users
    '''
    with get_session() as db:
        users = db.exec(select(User).offset(offset).limit(limit)).all()
        if not users:
            print("No users found within range")
            return
        for user in users:
            print(user)



if __name__ == "__main__":
    cli()