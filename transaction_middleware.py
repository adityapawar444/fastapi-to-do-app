from fastapi import Request
from typing import Callable

from sqlalchemy.orm import Session
from db import get_db_session


async def db_txn_middleware(
    request: Request,
    call_next: Callable
):
    db_session: Session = get_db_session()
    request.state.db_session = db_session
    try:
        response = await call_next(request)
        db_session.commit()
        return response
    except Exception as e:
        db_session.rollback()
        raise e
    finally:
        db_session.close()
