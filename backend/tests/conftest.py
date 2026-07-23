import pytest
from app import create_app
from app.extensions import db as _db

@pytest.fixture(scope="session")
def app():
    """Provides application instance running Testing configurations."""
    app = create_app("testing")
    
    # Establish application context
    ctx = app.app_context()
    ctx.push()
    
    yield app
    
    # Tear down application context
    ctx.pop()


@pytest.fixture(scope="session")
def db(app):
    """Initializes in-memory test database schema structure."""
    _db.create_all()
    
    yield _db
    
    _db.drop_all()


@pytest.fixture(scope="function")
def session(db):
    """Provides a fresh transactional session for test cases, rolling back after use."""
    connection = db.engine.connect()
    transaction = connection.begin()
    
    from sqlalchemy.orm import scoped_session, sessionmaker
    # Bind session to transaction connection
    Session = scoped_session(sessionmaker(bind=connection))
    
    old_session = db.session
    db.session = Session
    
    yield Session
    
    transaction.rollback()
    connection.close()
    Session.remove()
    db.session = old_session



@pytest.fixture(scope="function")
def client(app):
    """Provides a web API client mock for simulator route checks."""
    return app.test_client()
