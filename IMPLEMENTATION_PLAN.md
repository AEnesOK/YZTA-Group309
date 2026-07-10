# 🚀 CodePeer AI - Ekip Geliştirme Planı (MVP Odaklı)

Selam takım (CodePeer AI Team)! 👋

Harika bir giriş yaptık ve projenin temel yapısını başarıyla ayağa kaldırdık. Ekipçe aldığımız kararlar doğrultusunda, **Yapay Zeka (AI) entegrasyonunu son sprinte (Sprint 3) bırakıyoruz.** 

Şu anki (Sprint 2) en büyük hedefimiz: **Uygulamanın arayüzünü toparlayıp, kullanıcıların sorunsuz bir şekilde kod paylaşıp okuyabildiği, çalışan temiz bir MVP (Minimum Viable Product) ortaya çıkarmak.**

Aşağıda takım olarak belirlediğimiz strateji doğrultusunda baştan sona güncellenmiş MVP geliştirme planımız yer almaktadır.

---

## 🏗️ Şu Ana Kadar Neler Yaptık?

Ekip olarak kolları sıvayıp çekirdek altyapıyı çoktan kurduk:
- **Backend & Veritabanı:** FastAPI ve SQLite ile `User`, `CodePost` tabloları ve temel mimarimizi oluşturduk.
- **Kullanıcı İşlemleri:** Temel giriş yapma (login), üyelik oluşturma (register) işlemlerini tamamladık.
- **Kod Paylaşımı:** Kullanıcıların sisteme kod yükleyebilmesi ve bu kodların listelenmesi özelliğini devreye aldık.

---

## 🎯 Şimdilik Odaklanacağımız MVP Adımları (Sprint 2)

Bu sprint bitmeden projeyi "kullanıma hazır bir MVP" haline getirmek için ekipçe yapacağımız teknik değişiklikler:

### 1. Anasayfa ve Gizlilik Mantığının Değişmesi
**Mevcut Durum:** Kodlar doğrudan anasayfada herkese açık listeleniyor.
**Yapılacaklar:**
- `main.py` içindeki `/` (anasayfa) endpoint'ini güncelleyeceğiz. 
- Eğer kullanıcı giriş yapmamışsa (misafir ise), anasayfada sadece platformun tanıtımı (Hero Section) ve "Kayıt Ol / Giriş Yap" butonları görünecek. Paylaşılan kodlar gizlenecek.
- Kullanıcı ancak **giriş yaptıktan sonra** paylaşılan kodların akışını (feed) görebilecek.

### 2. Arayüz (UI) Tasarımlarının Düzenlenmesi
**Mevcut Durum:** Temel Bootstrap ile çalışıyoruz ancak "MVP" diyebilmemiz için tasarımları toparlamamız lazım.
**Yapılacaklar:**
- `static/css/style.css` oluşturulup projeye eklenecek (Şu anki `app.mount("/static")` hatası da böylece çözülecek).
- Sayfa tasarımları (Anasayfa, Üyelik Oluşturma, Kod Yükleme ve Paylaşım kısımları) elden geçirilip daha profesyonel bir görünüme kavuşturulacak.
- *Opsiyonel:* Kodların `<textarea>` yerine daha şık görünmesi için kod renklendirme (Syntax Highlighting - Örn: Prism.js veya Monaco Editor read-only modu) eklenecek.

### 3. Veritabanı (DB) Güncellemeleri
Veritabanımızı MVP ihtiyaçlarına göre biraz daha güncelleyeceğiz:
- `CodePost` ve ileride eklenecek yorumlar için gerekli ilişkiler (relationships) gözden geçirilecek, eksik alanlar varsa eklenecek.

---

## ❓ Ekibin Kararlaştırması Gereken Konular (Açıkta Kalanlar)

Aşağıdaki konular MVP sonrasına (Sprint 3'e) bırakılmış veya henüz netleşmemiş konulardır. Sonraki toplantılarımızda takımca karar vermeliyiz:

> [!QUESTION]
> **Yapay Zeka (AI) Entegrasyonu Nasıl Olacak?**
> AI ve analiz kısımlarını Sprint 3'te yapacağız. Ancak API anahtarını (örn: Groq API Key) nasıl yöneteceğiz? Sunucuya tek bir key mi koyacağız, yoksa herkesin lokal `.env` dosyasında kendi key'i mi olacak? (Güvenlik açısından .env önerilir)

> [!QUESTION]
> **Arayüz Tasarımı (UI/UX) Kararı:**
> Arayüzü düzenlerken sadece hazır Bootstrap üzerinden mi gidelim, yoksa projenin premium görünmesi için özel bir CSS/Tailwind yapısı mı kuralım? Tasarımın renk paleti ne olmalı?

> [!QUESTION]
> **Kod İnceleme (Code Review) Sayfası:**
> Kullanıcıların kodlara tıklayıp yorum yapabileceği detay sayfası (Çift Kör/Double-Blind mantığı) bu Sprint 2 MVP'sine dahil edilecek mi, yoksa o da mı Sprint 3'teki analiz kısmına bırakılacak?
