from fastapi import FastAPI, Form, Request, Depends, Response
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import bcrypt
from datetime import datetime
from itsdangerous import URLSafeTimedSerializer as Serializer, BadSignature

app = FastAPI()
templates = Jinja2Templates(directory="public")
DATABASE_URL = "mysql://root:1324@svc.sel4.cloudtype.app:30729/solveit"
engine = create_engine(DATABASE_URL)
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
current_date = datetime.now().strftime("%Y-%m-%d")

# 비밀 키 설정 (쿠키 암호화에 사용)
SECRET_KEY = "mysecretkey"
serializer = Serializer(SECRET_KEY)

class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, index=True)
    nickname = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    created_at = Column(String, nullable=False)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
# 로그인 상태 체크를 위한 커스텀 종속성
def get_current_user(request: Request):
    user_cookie = request.cookies.get("user_data")
    if user_cookie:
        try:
            user_data = serializer.loads(user_cookie)
            return user_data  # {'id': user.id, 'nickname': user.nickname}
        except BadSignature:
            return None  # 쿠키가 만료되었거나 변조된 경우
    return None
@app.get("/")
@app.get("/index")
async def index_page(request: Request, current_user: dict = Depends(get_current_user)):
    return templates.TemplateResponse("index.html", {"request": request, "current_user": current_user})

@app.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(
    request: Request,
    nicknameoremail: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = (
        db.query(User)
        .filter((User.nickname == nicknameoremail) | (User.email == nicknameoremail))
        .first()
    )

    if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
        # 사용자를 암호화하여 쿠키에 저장
        user_data = {'id': user.id, 'nickname': user.nickname}
        encrypted_data = serializer.dumps(user_data)

        response = RedirectResponse(url="/", status_code=302)
        response.set_cookie(key="user_data", value=encrypted_data)
        return response
    else:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "message": "닉네임/이메일 또는 비밀번호가 잘못되었습니다."},
        )

@app.get("/signup")
async def signup_page(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request, "message": ""})

@app.post("/signup")
async def signup(
    request: Request,
    name: str = Form(...),
    nickname: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirmpassword: str = Form(...),
    db: Session = Depends(get_db),
):
    if confirmpassword != password:
        return templates.TemplateResponse(
            "signup.html", {"request": request, "message": "비밀번호가 일치하지 않습니다."}
        )

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    existing_user = db.query(User).filter(
        (User.nickname == nickname) | (User.email == email)
    ).first()

    if existing_user:
        return templates.TemplateResponse(
            "signup.html", {"request": request, "message": "닉네임 또는 이메일이 이미 존재합니다."}
        )

    new_user = User(
        name=name,
        nickname=nickname,
        email=email,
        password=hashed_password,
        created_at=current_date
    )

    db.add(new_user)
    db.commit()

    # 새로운 사용자를 암호화하여 쿠키에 저장
    user_data = {'id': new_user.id, 'nickname': new_user.nickname}
    encrypted_data = serializer.dumps(user_data)

    response = RedirectResponse(url="/", status_code=302)
    response.set_cookie(key="user_data", value=encrypted_data)
    return response


@app.get("/logout")
async def logout(response: Response):
    response.delete_cookie("user_data")  # 쿠키 삭제
    return RedirectResponse(url="/", status_code=302)
