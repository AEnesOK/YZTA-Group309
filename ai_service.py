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