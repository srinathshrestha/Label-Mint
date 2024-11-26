from sqlalchemy.orm import Session
from datetime import datetime
from app.models import Token

def issue_tokens_to_user(db: Session, user_id: int, token_amount: int):
    token_entry = db.query(Token).filter(Token.user_id == user_id).first()
    if not token_entry:
        token_entry = Token(user_id=user_id, token_balance=token_amount, last_updated=datetime.now())
        db.add(token_entry)
    else:
        token_entry.token_balance += token_amount
        token_entry.last_updated = datetime.now()
    db.commit()
