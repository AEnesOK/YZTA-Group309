import os
import json
from groq import Groq
from dotenv import load_dotenv

# .env dosyasındaki değişkenleri sisteme yükle
load_dotenv()

# Groq istemcisini başlat
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)


def evaluate_code_review(code_content: str, user_comment: str):
    """
    Kullanıcının yaptığı code review yorumunu yapay zekaya denetletir.
    Geriye (score, review_text) şeklinde bir tuple döner.
    """

    prompt = f"""
    You are NOT a code reviewer.

    You are a reviewer evaluator.

    Your job is to evaluate whether the HUMAN review correctly identifies issues in the code.

    Sen bir "Kod İnceleme (Code Review) Hakemi"sin.
    Senin görevin KOD YAZMAK, KODU DÜZELTMEK veya TAVSİYE VERMEK DEĞİLDİR!
    Sen, B kişisinin (yorumcunun), A kişisinin (yazarın) koduna yaptığı analizin doğruluk ve kalitesini ölçeceksin.

    ÖZEL DURUM (MOTİVASYON VE BASİT KODLAR - ÇOK ÖNEMLİ!):
    - Eğer orijinal kod çok basitse (örneğin 1-5 satırlık bir "Hello World" veya temel bir print işlemiyse), yorumu yazan kişiden derinlemesine teknik bir analiz veya hata bulmasını KESİNLİKLE BEKLEME. 
    - Bu tür temel kodlarda, yorumcunun kodu yazan kişiyi motive edici, eğitici (pedagojik) ve destekleyici tavrı teknik analizden çok daha değerlidir. 
    - Eğer yorumcu sadece destek olmak, tebrik etmek ve temel mantığı (örneğin print fonksiyonunu) övmek için yazmışsa; bunu mükemmel bir mentorluk olarak gör, yüksek puan ver ve ASLA "teknik eksiklik var" veya "hata bulmadın" diye puan KIRMA.

    SÜREÇ:
    1. Orijinal KOD'u analiz et ve içindeki bariz hataları, mantık sorunlarını veya eksikleri kendi içinde tespit et.
    2. YORUM'u oku. Yorumu yazan kişi, koddaki gerçek ve bariz hataları başarıyla fark etmiş mi?
    3. Yorumu yazan kişi olmayan bir hatayı var gibi mi göstermiş (yanlış tespit)?
    4. Yorumu yazan kişi, koddaki bariz ve kritik bir hatayı tamamen gözden kaçırmış mı?

    KESİN KURALLAR (BUNLARI İHLAL ETMEK KESİNLİKLE YASAKTIR):
    - ASLA kodu nasıl düzelteceğini anlatma!
    - ASLA kod parçacığı (code snippet), kütüphane önerisi veya fonksiyon örneği paylaşma!
    - B kişisine (yorumu yazana) kodu düzeltmesi gerektiğini SÖYLEME, çünkü o sadece bir inceleyici, kodun sahibi değil.
    - SADECE B kişisinin analizinin kalitesini değerlendir. Neyi doğru buldu, neyi gözden kaçırdı?
    
    ÖRNEK DOĞRU HAKEM DÖNÜŞÜ (Sadece bunu model al):
    "Koddaki döngü (loop) mantığı hatasını çok iyi yakalamışsın, başarılı bir tespit. Ancak girdi doğrulaması (input validation) yapılmadığını tamamen gözden kaçırmışsın. Kodun genelini inceleme konusunda daha dikkatli olmalısın."

    ÖRNEK YASAKLI DÖNÜŞ (BUNU ASLA YAPMA):
    "Döngü mantığını iyi bulmuşsun. Girdi doğrulaması için kodu şöyle değiştirmelisin: try-except ekle..." -> (ÇÜNKÜ ÇÖZÜM SUNMAK YASAKTIR!)

    verdiğim örnek cümleler sadece örnek amaçlı. sen koddaki hata veya yanlışlara göre yorum yapacaksın. standart bir cevabın yok. koddaki hatalara göre cevaplıyorsun.

    Never provide new code improvements.
    Never explain how to fix the code.
    Never suggest implementation changes.
    Never teach the author how to rewrite the code.

    Instead:

    1. Compare the review against the code.
    2. Decide whether each claim in the review is correct.
    3. Detect important issues that the reviewer missed.
    4. Tell the reviewer ONLY WHAT THEY MISSED.
    5. Do not explain HOW TO FIX the missed issue.

    çok basit bir kod veya çok kısa bir kod verildiğinde örneğin temel bir script olabilir. kullanıcı kodlamaya yeni başlamış olabilir. bu tarz kodlara yapılan destekleyici ve moral verici yorumları puanlarken ve analiz ederken
    kodlama konusunda yorum yapmalarını bekleme. bu tarz yorumlar yalnızca kişileri mental olarak desteklemek maksatlı yapılmıs yorumlar olabilir. bu yorumlara da güzel 8+ puan verebilirsin. 

    eğerki yorum yapılan kod çok basit ve kısa bir kodsa. bu koda yapılan yorumda kodun kalitesini, hata durumlarını, fonksiyonun parametrelerini vs. gibi noktaları değerlendirme. sonuçta bu kod temel bir kod ve kimse bir destek 
    mesajından daha fazlasını beklemıyor. 
    STRICT PROHIBITIONS

    You must never:

    - rewrite the code
    - optimize the code
    - generate code
    - provide code snippets
    - explain implementation details
    - suggest algorithms
    - recommend design patterns
    - tell how to solve an issue
    - explain the correct implementation

    If you do any of the above, your answer is incorrect.

    Step 1
    Extract every claim from the review.

    Step 2
    Verify each claim against the code.

    Step 3
    Determine whether there are any significant issues that the reviewer did NOT mention.

    If there are no significant missed issues, return an empty list.

    Do NOT invent additional issues simply to criticize the reviewer.

    It is perfectly acceptable if the reviewer missed nothing important.

    A high-quality review may legitimately have an empty "missed_issues" list.

    Step 4
    Give feedback ONLY about the review quality.

    Never discuss code improvements.

    If you detect a missed issue, you must only mention that the reviewer overlooked it.

    Do NOT explain how that issue should be fixed.

    Good:
    "You overlooked that the function does not handle invalid input."

    Bad:
    "You overlooked invalid input. You should use try-except."



    Scoring Guide

    10
    The review correctly identifies almost all important issues and contains no false claims.

    8-9
    The review identifies most important issues but misses minor ones.

    6-7
    The review identifies some important issues but misses several significant ones.

    4-5
    The review contains multiple incorrect claims or overlooks major issues.

    1-3
    The review is mostly incorrect, irrelevant, or unsupported by the code.



    Important:

    It is perfectly acceptable if the reviewer missed nothing important.

    Do NOT invent additional issues just to provide criticism.

    If the review already covers all major issues, explicitly state that no significant issues were overlooked.

    You must ignore the quality of the code itself.

    Your score represents ONLY the quality of the human review.

    A very bad code can still receive a score of 10 if the review accurately identifies its problems.

    A very good code can receive a score of 2 if the review contains false or irrelevant comments.


    
    Imagine the code has already been frozen.

    Nobody is allowed to modify the code anymore.

    Your evaluation will be used ONLY to grade the reviewer.

    Therefore never provide advice intended for the code author.

    KOD:
    {code_content}

    YAPILAN YORUM:
    {user_comment}

    Bana SADECE geçerli bir JSON formatında şu yapıyla cevap ver:

    {{
        "score": (1 ile 10 arasında kalite puanı),
        "review_text": "Evaluate ONLY the human review.

        Mention:

        - correct observations
        - incorrect observations
        - overlooked issues

        Never explain how to fix the code.

        Never suggest code improvements."
    }}
    """

    try:
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a Code Review Evaluator. Your ONLY task is to evaluate the quality of a human code review.Never review the code yourself.Never explain how to improve the code.Never suggest fixes.Return valid JSON only."
                            )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"}
        )

        result = json.loads(response.choices[0].message.content)

        return result.get("score"), result.get("review_text")

    except Exception as e:
        print(f"AI Hatası: {e}")
        return None, "Yapay zeka değerlendirmesi şu an yapılamadı."

<<<<<<< HEAD
def generate_learning_plan(ai_feedbacks: list):
    """
    Kullanıcının daha önceki yorumlarına yapılan AI eleştirilerini analiz edip
    kişiselleştirilmiş bir çalışma/gelişim programı üretir.
    """
    if not ai_feedbacks:
        return "Henüz yeterli değerlendirme verisi yok. Sana özel bir plan çıkarabilmem için kodlara daha fazla yorum yapmalısın! 🚀"
        
    feedbacks_str = "\n".join([f"- {f}" for f in ai_feedbacks])
    
    prompt = f"""
    Sen CodePeer AI platformunda kıdemli bir yazılım mentorusun.
    Kullanıcı, başka geliştiricilerin kodlarını inceliyor ve yorumlar yapıyor.
    Aşağıda, kullanıcının yaptığı yorumlara başka bir yapay zeka tarafından verilen eleştiri ve geri bildirimler yer alıyor.
    Bu geri bildirimler, kullanıcının gözden kaçırdığı hataları veya yanlış tespitlerini içerir.

    Geçmiş Hatalar ve Dönütler:
    {feedbacks_str}

    GÖREVİN:
    Yukarıdaki dönütleri analiz ederek kullanıcıya özel, Markdown formatında, Türkçe bir "Yazılım Gelişim Programı" hazırla.
    - Hangi konularda eksiği olduğunu tespit et (Örn: Döngüler, Hata Yönetimi, Temiz Kod).
    - Hangi konulara çalışması gerektiğini belirle.
    - Motive edici ve destekleyici bir dil kullan.
    - Çıktıyı maddeler halinde ve okuması kolay, kısa tut (Maksimum 3-4 paragraf/başlık).
    """
    
    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a helpful coding mentor. Output in Turkish Markdown."},
                {"role": "user", "content": prompt}
            ],
            model="llama-3.3-70b-versatile"
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"AI Plan Hatası: {e}")
        return "Yapay zeka ile plan oluşturulurken bir hata oluştu. Daha sonra tekrar dene."
=======
def generate_mentor_advice(ai_feedbacks: list):
    """
    Kullanıcının aldığı eski AI geri bildirimlerini okuyarak, 
    gelişmesi gereken 3 ana konuyu belirler.
    """
    if not ai_feedbacks:
        return ["Henüz yeterli verimiz yok. Gelişim analizin için önce birkaç kod incelemesi (Code Review) yapmalısın!"]

    # Geri bildirimleri tek bir metinde birleştir
    feedbacks_text = "\n".join([f"- {f}" for f in ai_feedbacks])

    # prompt = f"""
    # Sen, yazılım geliştiricilere eğitim tavsiyesi veren uzman bir mentorsun.
    # Aşağıda, bir kullanıcının geçmişte yaptığı kod incelemelerine karşılık AI Hakem'den aldığı geri bildirimler var:
    
    # {feedbacks_text}

    # Görev: Bu metinleri analiz et. Kullanıcının hangi konularda (örneğin; Hata Yönetimi, Performans, Clean Code, Güvenlik vb.) eksik olduğunu tespit et. Ona çalışması gereken 3 adet konu başlığı çıkar.
    
    # SADECE geçerli bir JSON formatında şu yapıyla cevap ver:
    # {{
    #     "topics": [
    #         "Konu Başlığı 1: Neden bunu çalışmalı ve nasıl geliştirebilir (1 cümlelik kısa açıklama).",
    #         "Konu Başlığı 2: Neden bunu çalışmalı ve nasıl geliştirebilir (1 cümlelik kısa açıklama).",
    #         "Konu Başlığı 3: Neden bunu çalışmalı ve nasıl geliştirebilir (1 cümlelik kısa açıklama)."
    #     ]
    # }}
    # """

    prompt = f"""
    Sen bir "Kod İnceleme (Code Review) Mentoru"sun.
    Görevin: Aşağıdaki geçmiş değerlendirme notlarını analiz ederek kullanıcının KOD OKUMA ve HATA YAKALAMA yeteneğindeki yapısal zayıflıkları bulmak.

    GEÇMİŞ DEĞERLENDİRMELER (Kullanıcının yaptığı incelemelere verilen dönütler):
    {feedbacks_text}

    KURALLAR:
    1. Geçmiş değerlendirmelerde tekrarlayan tespit hatalarını veya sürekli gözden kaçırılan kavramları bul.
    2. SADECE geçmiş değerlendirmelerde bahsedilen konular üzerinden çıkarım yap. Kendi kendine yeni kavramlar uydurma.
    3. Kullanıcıya kod yazma tavsiyesi VERME. Sadece başkalarının kodunu okurken/incelerken neye dikkat etmesi gerektiği konusunda yönlendir.
    
    SADECE geçerli JSON formatında şu yapıyla cevap ver:
    {{
        "topics": [
            {{
                "title": "Tespit Edilen Zayıf Konsept Başlığı (Örn: Hata Yönetimi)",
                "description": "Bu konuda kod okurken neyi gözden kaçırıyor ve ileride neye dikkat etmeli? (1-2 cümle)"
            }},
            {{
                "title": "Tespit Edilen Zayıf Konsept Başlığı",
                "description": "Bu konuda kod okurken neyi gözden kaçırıyor ve ileride neye dikkat etmeli? (1-2 cümle)"
            }}
        ]
    }}
    """

    try:
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "Sen kıdemli bir yazılım mentorusun. Yalnızca JSON formatında yanıt ver."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model="llama-3.1-8b-instant",
            response_format={"type": "json_object"}
        )

        result = json.loads(response.choices[0].message.content)
        return result.get("topics", ["Gelişim başlıkları şu an oluşturulamadı, lütfen tekrar dene."])

    except Exception as e:
        print(f"Mentor AI Hatası: {e}")
        return ["Yapay zeka analizi şu an yapılamadı."]
>>>>>>> 740a2996774bab3222cab9d29e6a8692df3ab82f
