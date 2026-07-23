from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_marshmallow import Marshmallow
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from celery import Celery
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import BigInteger, UUID
import uuid

@compiles(JSONB, "sqlite")
def compile_jsonb_sqlite(type_, compiler, **kw):
    return "TEXT"

@compiles(BigInteger, "sqlite")
def compile_bigint_sqlite(type_, compiler, **kw):
    return "INTEGER"

# Monkeypatch UUID bind_processor to convert strings to uuid.UUID objects automatically
original_bind_processor = UUID.bind_processor

def new_bind_processor(self, dialect):
    proc = original_bind_processor(self, dialect)
    if proc is None:
        return proc
    def process(value):
        if isinstance(value, str):
            try:
                value = uuid.UUID(value)
            except ValueError:
                pass
        return proc(value)
    return process

UUID.bind_processor = new_bind_processor




# Instantiate the SQLAlchemy database ORM extension
db = SQLAlchemy()

# Instantiate the Bcrypt hashing engine
bcrypt = Bcrypt()

# Instantiate the JWT authentication manager
jwt = JWTManager()

# Instantiate Cross-Origin Resource Sharing filter
cors = CORS()

# Instantiate Marshmallow serialization helper
ma = Marshmallow()

# Instantiate rate limiter targeting remote client IP addresses
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100 per 15 minutes"],
    storage_uri="memory://"  # Default; will override with Redis in factory setup
)

# Instantiate Celery tasks engine (Will configure task queues inside factory context)
celery_app = Celery("e_rakshak")
