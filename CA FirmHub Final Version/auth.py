"""Authentication: JWT tokens (PyJWT) and password hashing (Werkzeug)."""
import jwt
import datetime
from functools import wraps
from flask import request, jsonify, g
from werkzeug.security import generate_password_hash, check_password_hash
from config import SECRET_KEY, TOKEN_EXPIRE_HOURS
from database import get_db, dict_row

def hash_password(password):
    return generate_password_hash(password)

def verify_password(password, hashed):
    return check_password_hash(hashed, password)

def create_token(user_id, role):
    payload = {
        "sub": str(user_id),  # JWT spec requires sub to be a string
        "role": role,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=TOKEN_EXPIRE_HOURS)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def decode_token(token):
    return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

def login_required(f):
    """Decorator: require valid JWT token."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            print(f"  [AUTH] 401 - No Bearer token for {request.path}")
            return jsonify({"detail": "Not authenticated"}), 401
        try:
            token_str = auth.split(" ", 1)[1]
            payload = decode_token(token_str)
        except jwt.ExpiredSignatureError:
            print(f"  [AUTH] 401 - Token expired for {request.path}")
            return jsonify({"detail": "Token expired"}), 401
        except jwt.InvalidTokenError as e:
            print(f"  [AUTH] 401 - Invalid token for {request.path}: {e}")
            return jsonify({"detail": "Invalid token"}), 401

        db = get_db()
        user = dict_row(db.execute("SELECT * FROM users WHERE id=? AND is_active=1", (int(payload["sub"]),)).fetchone())
        if not user:
            print(f"  [AUTH] 401 - User id={payload.get('sub')} not found for {request.path}")
            return jsonify({"detail": "User not found or inactive"}), 401
        g.user = user
        return f(*args, **kwargs)
    return wrapper

def require_role(*roles):
    """Decorator factory: require specific roles."""
    def decorator(f):
        @wraps(f)
        @login_required
        def wrapper(*args, **kwargs):
            if g.user["role"] not in roles:
                return jsonify({"detail": "Insufficient permissions"}), 403
            return f(*args, **kwargs)
        return wrapper
    return decorator

def log_action(db, user_id, action, entity_type=None, entity_id=None, details=None, ip=None):
    IST = datetime.timezone(datetime.timedelta(hours=5, minutes=30))
    ist_now = datetime.datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S")
    db.execute(
        "INSERT INTO audit_logs (user_id, action, entity_type, entity_id, details, ip_address, timestamp) VALUES (?,?,?,?,?,?,?)",
        (user_id, action, entity_type, entity_id, details, ip, ist_now)
    )
    db.commit()
