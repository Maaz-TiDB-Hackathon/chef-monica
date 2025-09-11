from sqlalchemy.orm import Session
from database import DBChat, DBUser, DBRole
from models import ChatCreate, UserCreate
import bcrypt
from database import session
from sqlalchemy import update, cast, JSON, desc
from sqlalchemy.sql import func
from recipe_document_generator import get_review_table
from pytidb.filters import IN
from tidb import tidb_client

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(password, hashed_password):
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_user_by_id(user_id: int):
    """Get user by ID."""
    return session().query(DBUser).filter(DBUser.id == user_id).first()

def get_user_by_email(email: str):
    """Get user by email."""
    return session().query(DBUser).filter(DBUser.email == email).first()

def create_user(user: UserCreate):
    """Create a new user."""
    hashed_password = hash_password(user.password)
    db_user = DBUser(
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_password
    )

    # Assign default user role
    db = session()
    user_role = db.query(DBRole).filter(DBRole.name == "user").first()
    if user_role:
        db_user.roles.append(user_role)

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(email: str, password: str):
    """Authenticate user with username and password."""
    user = get_user_by_email(session(), email)
    if not user:
        return False
    if not check_password(password, user.hashed_password):
        return False
    return user

def create_role(db: Session, name: str, description: str = ""):
    """Create a new role."""
    db_role = DBRole(name=name, description=description)
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role

def create_new_chat(chat: ChatCreate):
    """Create a new chat."""
    db_chat = DBChat(id = chat.id,user_id = chat.user_id, messages = chat.messages)
    db = session()
    db.add(db_chat)
    db.commit()
    db.refresh(db_chat)
    return db_chat

def get_all_chats_for_user(user_id: int, skip: int = 0, limit: int = 100):
    """Get chat by ID."""
    return session().query(DBChat).filter(DBChat.user_id == user_id).order_by(desc(DBChat.created_at)).offset(skip).limit(limit).all()

def get_chat_by_id(id: int):
    """Get chat by ID."""
    return session().query(DBChat).filter(DBChat.id == id).first()

def append_message_to_chat(id: str, message: dict):
    """Append message to chat."""
    db = session()
    stmt = (
        update(DBChat)
        .where(DBChat.id == id)
        .values(
            messages=func.json_array_append(
                DBChat.messages,
                '$',
                cast(message, JSON)
            )
        )
    )
    db.execute(stmt)
    db.commit()

def get_all_users(skip: int = 0, limit: int = 100):
    """Get all users with pagination."""
    return session().query(DBUser).offset(skip).limit(limit).all()

def get_role_by_name(db: Session, name: str):
    """Get role by name."""
    return db.query(DBRole).filter(DBRole.name == name).first()

def get_reviews(recipe_ids: list[int]) -> list[dict]:
    return get_review_table().query(filters={"recipe_id": {IN: recipe_ids}}).to_pydantic()

def find_food_item_in_usda_fdc(food_item: str) -> list[dict]:
    sql="""
    SELECT fdc_id, description FROM food
    WHERE fts_match_word(:food_item, description)
    ORDER BY fts_match_word(:food_item, description) DESC
    LIMIT 10
    """
    return tidb_client.query(sql = sql, params = {"food_item": food_item}).to_list()


def find_nutrient_information_for_food_item(fdc_id: int) -> list[dict]:
    sql="""
    SELECT nutrient.name as name, food_nutrient.amount as amount, nutrient.unit_name as unit
    FROM food_nutrient
    JOIN nutrient ON food_nutrient.nutrient_id = nutrient.id
    WHERE food_nutrient.fdc_id = :fdc_id
    AND food_nutrient.amount > 0
    ORDER BY nutrient.id ASC
    """
    return tidb_client.query(sql = sql, params = {"fdc_id": fdc_id}).to_list()
