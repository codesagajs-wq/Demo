from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import timedelta
import sys
sys.path.append('..')

from auth.auth_handler import (
    authenticate_user, create_access_token, decode_token,
    get_user, ACCESS_TOKEN_EXPIRE_MINUTES, Token, User
)
from agents.coordinator import CoordinatorAgent

app = FastAPI(title="Report Generator")

coordinator = CoordinatorAgent()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# Authentication Endpoints
@app.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login endpoint"""
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Get current authenticated user"""
    token_data = decode_token(token)
    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = get_user(username=token_data.username)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user


# Report Generation Endpoints
class QueryRequest(BaseModel):
    query: str

@app.post("/api/reports/query")
async def generate_report_from_query(
    request: QueryRequest,
    current_user: User = Depends(get_current_user)
):
    """Generate report from natural language query"""
    
    try:
        user_context = {
            'full_name': current_user.full_name,
            'department': current_user.department,
            'role': current_user.role,
            'email': current_user.email
        }
        
        result = coordinator.process_user_query(
            user_query=request.query,
            user_context=user_context
        )
        
        return {
            'success': True,
            'query': request.query,
            'user': current_user.full_name,
            'parsed_request': result.get('parsed_request', {}),
            'workflow': result.get('workflow', {}),
            'data_sources_used': result.get('data_sources_used', []),
            'records_fetched': result.get('records_fetched', {}),
            'insights': result.get('insights', []),
            'anomalies': result.get('anomalies', []),
            'forecasts': result.get('forecasts', {}),
            'aggregated_data': result.get('aggregated_data', {}),
            'report': result.get('report', ''),
            'status': result.get('status', 'unknown')
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/user/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """Get current user info"""
    return current_user

@app.get("/health")
async def health():
    return {"status": "healthy", "version": "2.0"}