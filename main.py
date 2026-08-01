from fastapi import FastAPI, Request, Depends, Form, status, Response, Cookie
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from passlib.context import CryptContext
import database
import ai_service

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

# --- KOD DETAY SAYFASI ---
@app.get("/post/{post_id}")
def post_detail(request: Request, post_id: int, current_user: str = Cookie(None), db: Session = Depends(database.get_db)):
    if not current_user:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
        
    post = db.query(database.CodePost).filter(database.CodePost.id == post_id).first()
    if not post:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
        
    comments = db.query(database.Comment).filter(database.Comment.post_id == post_id).order_by(database.Comment.id.desc()).all()
    
    # Çift Kör (Double-Blind) Mantığı
    author_name = "Gizli Yazar"
    if post.owner.username == current_user:
        author_name = f"{current_user} (Sen)"
        
    for c in comments:
        if c.author.username == current_user:
            c.display_name = f"{current_user} (Sen)"
        else:
            c.display_name = f"CodePeer #{c.user_id}"

    return templates.TemplateResponse(
        request=request, 
        name="post_detail.html", 
        context={
            "title": post.title, 
            "username": current_user, 
            "post": post,
            "author_name": author_name,
            "comments": comments
        }
    )

# # --- YORUM EKLEME ---
# @app.post("/post/{post_id}/comment")
# def add_comment(
#     request: Request, 
#     post_id: int, 
#     content: str = Form(...), 
#     current_user: str = Cookie(None), 
#     db: Session = Depends(database.get_db)
# ):
#     if not current_user:
#         return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
        
#     user = db.query(database.User).filter(database.User.username == current_user).first()
#     if user:
#         new_comment = database.Comment(content=content, user_id=user.id, post_id=post_id)
#         db.add(new_comment)
#         db.commit()
    
#     return RedirectResponse(url=f"/post/{post_id}", status_code=status.HTTP_303_SEE_OTHER)

# --- YORUM EKLEME VE YAPAY ZEKA DEĞERLENDİRMESİ ---
@app.post("/post/{post_id}/comment")
def add_comment(
    request: Request, 
    post_id: int, 
    content: str = Form(...), 
    current_user: str = Cookie(None), 
    db: Session = Depends(database.get_db)
):
    if not current_user:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
        
    user = db.query(database.User).filter(database.User.username == current_user).first()
    
    if user:
        # 1. Kullanıcının yorumunu veritabanına kaydet
        new_comment = database.Comment(content=content, user_id=user.id, post_id=post_id)
        db.add(new_comment)
        db.commit()
        db.refresh(new_comment) # Yorumun ID'sini alabilmek için nesneyi güncelliyoruz
        
        # 2. İlgili kodu veritabanından çek (Yapay zekaya bağlam olarak sunmak için)
        post = db.query(database.CodePost).filter(database.CodePost.id == post_id).first()
        
        if post:
            # 3. AI Service'i çağır ve yorumu değerlendir
            score, review_text = ai_service.evaluate_code_review(
                code_content=post.content, 
                user_comment=content
            )
            
            # 4. Yapay zekanın değerlendirmesini ai_reviews tablosuna kaydet
            new_ai_review = database.AIReview(
                review_text=review_text,
                score=score,
                target_type="comment",
                post_id=post_id,
                comment_id=new_comment.id
            )
            db.add(new_ai_review)
            db.commit()
    
    return RedirectResponse(url=f"/post/{post_id}", status_code=status.HTTP_303_SEE_OTHER)


# # --- KULLANICI PROFİL SAYFASI ---
# @app.get("/profile")
# def profile_page(request: Request, current_user: str = Cookie(None), db: Session = Depends(database.get_db)):
#     # Kullanıcı giriş yapmamışsa login'e yönlendir
#     if not current_user:
#         return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
        
#     # Mevcut kullanıcıyı veritabanından çek
#     user = db.query(database.User).filter(database.User.username == current_user).first()
    
#     if not user:
#         return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

#     # user nesnesini gönderdiğimizde user.posts ve user.comments 
#     # veritabanı ilişkileri (relationship) sayesinde otomatik olarak erişilebilir olacak
#     return templates.TemplateResponse(
#         request=request, 
#         name="profile.html", 
#         context={
#             "title": f"{user.username} - Profil", 
#             "username": current_user, 
#             "user": user
#         }
#     )


# --- KULLANICI PROFİL SAYFASI VE ROZET SİSTEMİ ---
@app.get("/profile")
def profile_page(request: Request, current_user: str = Cookie(None), db: Session = Depends(database.get_db)):
    if not current_user:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
        
    user = db.query(database.User).filter(database.User.username == current_user).first()
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)


    total_score = 0
    review_count = 0
    language_stats = {}
    
    # Mentorluk istatistikleri için yeni değişkenler
    mentor_score = 0
    mentor_count = 0

    # Yorumları ve dilleri analiz et
    for comment in user.comments:
        if comment.ai_reviews and comment.ai_reviews[0].score is not None:
            ai_score = comment.ai_reviews[0].score
            total_score += ai_score
            review_count += 1
            
            lang = comment.post.language.strip()
            
            # KODUN SATIR SAYISINI HESAPLA
            code_lines = len(comment.post.content.strip().splitlines())
            
            # Eğer kod 5 satır veya daha az ise, bunu MENTORLUK olarak değerlendir
            if code_lines <= 5:
                mentor_score += ai_score
                mentor_count += 1
            else:
                # Eğer kod 5 satırdan uzunsa, bunu TEKNİK ustalık (Dil bazlı) olarak değerlendir
                if lang not in language_stats:
                    language_stats[lang] = {"total_score": 0, "count": 0}
                
                language_stats[lang]["total_score"] += ai_score
                language_stats[lang]["count"] += 1

    # Genel ortalama
    avg_score = round(total_score / review_count, 1) if review_count > 0 else 0

    # Rozetleri Belirle
    earned_badges = []
    
    # 1. MENTORLUK ROZETLERİ (Kısa kodlara yapılan destekleyici yorumlar için)
    if mentor_count >= 1:
        mentor_avg = mentor_score / mentor_count
        if mentor_count >= 2 and mentor_avg >= 8.5:
            earned_badges.append("🤝 Topluluk Mentoru")
        elif mentor_count >= 1 and mentor_avg >= 7.0:
            earned_badges.append("👋 Yardımsever Geliştirici")

    # 2. TEKNİK ROZETLER (Uzun kodlara yapılan teknik yorumlar için)
    for lang, stats in language_stats.items():
        lang_avg = stats["total_score"] / stats["count"]
        
        if stats["count"] >= 3 and lang_avg >= 8.5:
            earned_badges.append(f"🏅 {lang} Master Reviewer")
        elif stats["count"] >= 2 and lang_avg >= 7.0:
            earned_badges.append(f"⭐ {lang} Senior Reviewer")
        elif stats["count"] >= 1 and lang_avg >= 5.0:
            earned_badges.append(f"👍 {lang} Gözlemcisi")

    # total_score = 0
    # review_count = 0
    # language_stats = {} # Dillere göre istatistikleri tutacağımız sözlük

    # # Yorumları ve dilleri analiz et
    # for comment in user.comments:
    #     if comment.ai_reviews and comment.ai_reviews[0].score is not None:
    #         ai_score = comment.ai_reviews[0].score
    #         total_score += ai_score
    #         review_count += 1
            
    #         # Yorumun yapıldığı kodun dilini bul
    #         lang = comment.post.language.strip().title() # Örn: "python" -> "Python"
            
    #         if lang not in language_stats:
    #             language_stats[lang] = {"total_score": 0, "count": 0}
            
    #         language_stats[lang]["total_score"] += ai_score
    #         language_stats[lang]["count"] += 1

    # # Genel ortalama
    # avg_score = round(total_score / review_count, 1) if review_count > 0 else 0

    # # Rozetleri Belirle
    # earned_badges = []
    # for lang, stats in language_stats.items():
    #     lang_avg = stats["total_score"] / stats["count"]
        
    #     # Rozet Kazanma Kuralları
    #     if stats["count"] >= 3 and lang_avg >= 8.5:
    #         earned_badges.append(f"🏅 {lang} Master Reviewer")
    #     elif stats["count"] >= 2 and lang_avg >= 7.0:
    #         earned_badges.append(f"⭐ {lang} Senior Reviewer")
    #     elif stats["count"] >= 1 and lang_avg >= 5.0:
    #         earned_badges.append(f"👍 {lang} Gözlemcisi")

    return templates.TemplateResponse(
        request=request, 
        name="profile.html", 
        context={
            "title": f"{user.username} - Profil", 
            "username": current_user, 
            "user": user,
            "avg_score": avg_score,
            "earned_badges": earned_badges # Kazanılan rozetleri HTML'e gönder
        }
    )

# --- AI EĞİTİM PROGRAMI OLUŞTURMA ---
@app.post("/profile/generate-plan")
def generate_plan(request: Request, current_user: str = Cookie(None), db: Session = Depends(database.get_db)):
    if not current_user:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
        
    user = db.query(database.User).filter(database.User.username == current_user).first()
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    # Kullanıcının AI'dan aldığı eleştirileri topla
    ai_feedbacks = []
    for comment in user.comments:
        for review in comment.ai_reviews:
            if review.review_text:
                ai_feedbacks.append(review.review_text)

    # AI servisine yolla ve planı al
    plan = ai_service.generate_learning_plan(ai_feedbacks)
    
    # Kullanıcının planını güncelle
    user.learning_plan = plan
    db.commit()

    return RedirectResponse(url="/profile", status_code=status.HTTP_303_SEE_OTHER)