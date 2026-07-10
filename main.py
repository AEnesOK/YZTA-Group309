from fastapi import FastAPI, Request, Depends, Form, status, Response, Cookie
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from passlib.context import CryptContext
import database

app = FastAPI(title="AI-Peer Platform")

# Veri tabanı tablolarını oluştur
database.Base.metadata.create_all(bind=database.engine)

# Statik ve Şablon dosyaları bağlama
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Şifreleme ayarları
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

# ANA SAYFA
@app.get("/")
def home(request: Request, current_user: str = Cookie(None), db: Session = Depends(database.get_db)):
    # Sadece giriş yapan kullanıcılar kodları görebilir
    if current_user:
        posts = db.query(database.CodePost).order_by(database.CodePost.id.desc()).all()
    else:
        posts = []
    
    return templates.TemplateResponse(
        request=request, 
        name="index.html", 
        context={
            "title": "AI-Peer - Ana Sayfa", 
            "username": current_user, 
            "posts": posts  # Çekilen kodları HTML sayfasına gönderiyoruz
        }
    )

# --- KAYIT OL (REGISTER) ---
@app.get("/register")
def register_page(request: Request):
    return templates.TemplateResponse(request=request, name="register.html", context={"title": "Kayıt Ol"})

@app.post("/register")
def register(
    request: Request, 
    username: str = Form(...), 
    email: str = Form(...), 
    password: str = Form(...), 
    db: Session = Depends(database.get_db)
):
    # Kullanıcı adı veya e-posta zaten var mı kontrol et
    existing_user = db.query(database.User).filter(
        (database.User.username == username) | (database.User.email == email)
    ).first()
    
    if existing_user:
        return templates.TemplateResponse(
            request=request, 
            name="register.html", 
            context={"title": "Kayıt Ol", "error": "Bu kullanıcı adı veya e-posta zaten kullanılıyor!"}
        )
    
    # Yeni kullanıcıyı kaydet
    hashed_password = get_password_hash(password)
    new_user = database.User(username=username, email=email, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    
    # Başarılı kayıttan sonra giriş sayfasına yönlendir
    return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

# --- GİRİŞ YAP (LOGIN) ---
@app.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse(request=request, name="login.html", context={"title": "Giriş Yap"})

@app.post("/login")
def login(
    request: Request, 
    response: Response, # Çerez (cookie) ayarlamak için eklendi
    username: str = Form(...), 
    password: str = Form(...), 
    db: Session = Depends(database.get_db)
):
    user = db.query(database.User).filter(database.User.username == username).first()
    
    if not user or not verify_password(password, user.hashed_password):
        return templates.TemplateResponse(
            request=request, 
            name="login.html", 
            context={"title": "Giriş Yap", "error": "Hatalı kullanıcı adı veya şifre!"}
        )
    
    # Giriş başarılıysa ana sayfaya yönlendir ve tarayıcıya 'current_user' çerezini bırak
    redirect_response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    redirect_response.set_cookie(key="current_user", value=username)
    return redirect_response


# --- ÇIKIŞ YAP (LOGOUT) ---
@app.get("/logout")
def logout():
    # Çıkış yapıldığında çerezi sil ve ana sayfaya yönlendir
    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie(key="current_user")
    return response


# --- KOD PAYLAŞIM SAYFASINI GÖRÜNTÜLEME ---
@app.get("/post")
def post_page(request: Request, current_user: str = Cookie(None)):
    if not current_user:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse(request=request, name="post.html", context={"title": "Kod Paylaş"})

# --- KOD PAYLAŞIM ---
@app.post("/post")
def create_post(
    request: Request,
    title: str = Form(...),
    language: str = Form(...),
    content: str = Form(...),
    current_user: str = Cookie(None),
    db: Session = Depends(database.get_db)
):
    if not current_user:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
        
    # Giriş yapan kullanıcıyı bul
    user = db.query(database.User).filter(database.User.username == current_user).first()
    
    # Kodu, paylaşan kullanıcının ID'si ile birlikte kaydet
    new_post = database.CodePost(title=title, language=language, content=content, user_id=user.id)
    db.add(new_post)
    db.commit()
    
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)