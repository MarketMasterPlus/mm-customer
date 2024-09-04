import jwt
import datetime
from flask import current_app

def generate_jwt(customer_id):
    """Generate a JWT token with a 1-hour expiration"""
    expiration = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    payload = {
        'customer_id': customer_id,
        'exp': expiration
    }
    # Ensure the key name matches the one in the environment configuration
    token = jwt.encode(payload, current_app.config['JWT_SECRET_KEY'], algorithm='HS256')
    return token

def verify_jwt(token):
    """Verify JWT token and return the decoded payload"""
    try:
        decoded = jwt.decode(token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
        return decoded
    except jwt.ExpiredSignatureError:
        return {'error': 'Token has expired'}, 401
    except jwt.InvalidTokenError:
        return {'error': 'Invalid token'}, 400
    except jwt.PyJWTError as e:
        return {'error': str(e)}, 400
