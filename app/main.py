from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer
from starlette.middleware.sessions import SessionMiddleware
import requests
from jose import jwt
from .models import User
from .database import SessionLocal, get_db
import secrets
from .config import settings
from .oauth2 import create_access_token

app = FastAPI()

# Add session middleware for managing state
app.add_middleware(SessionMiddleware, secret_key=settings.secret_key)

# OAuth2 password bearer for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Google OAuth2 configuration
GOOGLE_CLIENT_ID = settings.google_client_id
GOOGLE_CLIENT_SECRET = settings.google_client_secret
GOOGLE_REDIRECT_URI = settings.google_redirect_uri

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/login/google")
async def login_google(request: Request):
    # Generate a random state parameter to prevent CSRF attacks
    state = secrets.token_urlsafe(16)
    request.session['oauth_state'] = state
    
    # Redirect to Google's OAuth 2.0 server
    return RedirectResponse(
        f"https://accounts.google.com/o/oauth2/auth?response_type=code&client_id={GOOGLE_CLIENT_ID}&redirect_uri={GOOGLE_REDIRECT_URI}&scope=openid%20profile%20email&access_type=offline&state={state}"
    )

@app.get("/auth/google/callback")
async def auth_google_callback(request: Request, code: str, state: str = None, db=Depends(get_db)):
    # Verify state to prevent CSRF attacks
    stored_state = request.session.get('oauth_state')
    if not state or not stored_state or state != stored_state:
        raise HTTPException(
            status_code=400,
            detail='Invalid state parameter'
        )
    
    # Clear the stored state
    request.session.pop('oauth_state', None)
    
    # Exchange the authorization code for tokens
    token_url = "https://accounts.google.com/o/oauth2/token"
    data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code",
    }
    
    response = requests.post(token_url, data=data)
    token_data = response.json()
    
    if "error" in token_data:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to retrieve token: {token_data.get('error_description', token_data.get('error'))}"
        )
    
    # Get access token from the response
    access_token = token_data.get("access_token")
    
    # Get user info using the access token
    user_info_url = "https://www.googleapis.com/oauth2/v3/userinfo"
    headers = {"Authorization": f"Bearer {access_token}"}
    user_info_response = requests.get(user_info_url, headers=headers)
    user_info = user_info_response.json()
    
    if "error" in user_info:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to retrieve user info: {user_info.get('error_description', user_info.get('error'))}"
        )
    
    # Extract user information
    email = user_info.get('email')
    name = user_info.get('name', '')
    picture = user_info.get('picture', '')
    
    if not email:
        raise HTTPException(
            status_code=400,
            detail="Email not provided by Google"
        )
    
    # Find or create user in the database
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        user = User(email=email, password='', role='user')
        db.add(user)
        db.commit()
        db.refresh(user)
    
    # Create JWT access token for your application
    app_access_token = create_access_token(data={"user_id": user.id, "email": user.email})
    
    # Return the token
    return {"access_token": app_access_token, "token_type": "bearer", "user": {"email": email, "name": name, "picture": picture}}

def get_current_user(token: str = Depends(oauth2_scheme), db=Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode JWT token
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
    except jwt.JWTError:
        raise credentials_exception
    
    # Get user from database
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    
    return user

@app.get("/me")
def read_users_me(current_user: User = Depends(get_current_user)):
    return {
        "email": current_user.email,
        "role": current_user.role,
        "id": current_user.id
    }

# For testing purposes
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)