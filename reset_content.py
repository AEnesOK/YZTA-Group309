import database

# Veritabanı oturumu oluştur
db = database.SessionLocal()

try:
    # 1. Önce AI değerlendirmelerini sil (Yorumlara ve Kodlara bağlı olduğu için ilk bu silinmeli)
    db.query(database.AIReview).delete()
    print("🧹 AI değerlendirmeleri silindi...")

    # 2. Yorumları sil (Kodlara bağlı olduğu için ikinci sırada silinmeli)
    db.query(database.Comment).delete()
    print("🧹 Kullanıcı yorumları silindi...")

    # 3. Paylaşılan kodları sil (Sadece kullanıcılara bağlı)
    db.query(database.CodePost).delete()
    print("🧹 Paylaşılan kodlar silindi...")
    
    # Değişiklikleri veritabanına kaydet
    db.commit()
    print("✅ İşlem tamamen başarılı! Sadece kullanıcı hesapları duruyor, proje tertemiz oldu.")

except Exception as e:
    print(f"❌ Bir hata oluştu: {e}")
    db.rollback() # Hata olursa veritabanını korumak için işlemi geri al
finally:
    db.close()