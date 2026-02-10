import streamlit as st

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="بَرَاعِم لُغَتي",
    page_icon="🎓",
    layout="centered"
)

# --- FONCTION DE SYNTHÈSE VOCALE (ARABE) ---
def speak_arabic(text):
    """Utilise l'API Web Speech du navigateur pour parler en arabe"""
    js_code = f"""
        <script>
        var msg = new SpeechSynthesisUtterance();
        msg.text = "{text}";
        msg.lang = "ar-SA";
        msg.rate = 0.9; 
        window.speechSynthesis.speak(msg);
        </script>
    """
    st.components.v1.html(js_code, height=0)

# --- STYLE CSS (Interface large, Couleurs Bordeaux et Or) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&family=Cairo:wght@400;700&display=swap');

    :root {
        --bordeaux: #800000;
        --gold: #d4af37;
        --bg-color: #fdfaf6;
    }
    
    .main { background-color: var(--bg-color); }
    
    /* Titres principaux */
    h1 { color: var(--bordeaux); font-family: 'Amiri', serif; font-size: 55px !important; text-align: center; margin-bottom: 0px; }
    h3 { font-family: 'Cairo', sans-serif; font-size: 28px !important; color: #333; text-align: center; margin-top: 0px; }
    h2 { color: var(--bordeaux); font-family: 'Cairo', sans-serif; font-size: 32px !important; border-bottom: 3px solid var(--gold); padding-bottom: 10px; }

    /* Boîte du mot à deviner (Très grande police) */
    .word-box { 
        font-size: 110px !important; 
        text-align: center; 
        padding: 45px;
        background: white; 
        border-radius: 30px; 
        box-shadow: 0 10px 25px rgba(0,0,0,0.1); 
        margin: 35px 0;
        border: 3px solid var(--gold);
        font-family: 'Amiri', serif;
        font-weight: bold;
    }

    /* Boutons de réponse (Style Bordeaux & Or) */
    .stButton>button { 
        background-color: var(--bordeaux); 
        color: white !important; 
        font-size: 50px !important; 
        font-family: 'Amiri', serif !important;
        border-radius: 20px; 
        width: 100%;
        height: 110px;
        border: 4px solid var(--gold);
        transition: 0.4s;
    }
    .stButton>button:hover { 
        background-color: var(--gold); 
        color: black !important; 
        transform: scale(1.05); 
    }

    /* Style du Guide des Règles dans la Sidebar */
    .rule-card {
        background-color: white;
        padding: 15px;
        border-radius: 15px;
        border-right: 8px solid var(--gold);
        margin-bottom: 15px;
        font-family: 'Cairo', sans-serif;
        font-size: 18px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        text-align: right;
        direction: rtl;
    }
    .rule-title { color: var(--bordeaux); font-weight: bold; font-size: 22px; margin-bottom: 5px; }

    /* Style pour le lien vidéo direct */
    .video-link {
        display: inline-block;
        padding: 10px 20px;
        background-color: var(--bordeaux);
        color: white !important;
        text-decoration: none;
        border-radius: 10px;
        font-family: 'Cairo', sans-serif;
        font-weight: bold;
        margin-top: 10px;
        border: 2px solid var(--gold);
    }
    </style>
    """, unsafe_allow_html=True)

# --- INITIALISATION DES VARIABLES DE SESSION ---
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'step' not in st.session_state:
    st.session_state.step = 0

# --- BASE DE DONNÉES DES EXERCICES (10 défis) ---
defis = [
    {"mot": "سُـ?ـال", "options": ["ؤ", "ئ", "أ"], "correct": "ؤ", "exp": "الضمة أقوى من الفتحة"},
    {"mot": "بِـ?ـر", "options": ["ئ", "ؤ", "أ"], "correct": "ئ", "exp": "الكسرة هي الأقوى دائماً"},
    {"mot": "رَ?َس", "options": ["أ", "ؤ", "ئ"], "correct": "أ", "exp": "الفتحة تغلبت على السكون"},
    {"mot": "مُـ?ـمِن", "options": ["ؤ", "أ", "ئ"], "correct": "ؤ", "exp": "الضمة أقوى من السكون"},
    {"mot": "ذِ?ْب", "options": ["ئ", "أ", "ؤ"], "correct": "ئ", "exp": "الكسرة تناسبها النبرة"},
    {"mot": "سَـ?َـلَ", "options": ["أ", "ئ", "ؤ"], "correct": "أ", "exp": "فتحة مع فتحة تناسب الألف"},
    {"mot": "رِ?َة", "options": ["ئ", "ؤ", "أ"], "correct": "ئ", "exp": "الكسرة أقوى من الفتحة"},
    {"mot": "فَـ?ْس", "options": ["أ", "ؤ", "ئ"], "correct": "أ", "exp": "الفتحة أقوى من السكون"},
    {"mot": "مُـ?َـذِّن", "options": ["ؤ", "أ", "ئ"], "correct": "ؤ", "exp": "الضمة أقوى من الفتحة"},
    {"mot": "بِيـ?َـة", "options": ["ئ", "أ", "ؤ"], "correct": "ئ", "exp": "بعد الياء الساكنة ترسم على النبرة"}
]

# --- AFFICHAGE DU GUIDE DES RÈGLES (SIDEBAR) ---
with st.sidebar:
    st.markdown("<h2>📚 دليل القواعد</h2>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="rule-card">
        <div class="rule-title">⚖️ قاعدة الميزان</div>
        لرسم الهمزة المتوسطة، نقارن بين <b>حركتها</b> و <b>حركة الحرف الذي قبلها</b>.
    </div>
    
    <div class="rule-card">
        <div class="rule-title">🥇 سلم القوة</div>
        1. <b>الكسرة:</b> الأقوى (تناسبها الياء ئ)<br>
        2. <b>الضمة:</b> (تناسبها الواو ؤ)<br>
        3. <b>الفتحة:</b> (تناسبها الألف أ)<br>
        4. <b>السكون:</b> الأضعف دائمًا.
    </div>
    """, unsafe_allow_html=True)
    
    st.write("---")
    st.metric("نقاطك الحالية 🌟", st.session_state.score)
    st.markdown(f"<p style='text-align:center; color:maroon;'><b>الأستاذ المشرف:<br>ميلوى فريد</b></p>", unsafe_allow_html=True)

# --- ZONE PRINCIPALE ---
st.markdown("<h1>🎓 منصة بَرَاعِم لُغَتي</h1>", unsafe_allow_html=True)
st.markdown("<h3>مشروع شركة ناشئة - الطالبة: عبو ماجدة</h3>", unsafe_allow_html=True)

# --- ركن الفيديو التعليمي (NOUVEAU) ---
with st.expander("📽️ ركن المشاهدة: تعلم قاعدة الهمزة بالفيديو"):
    st.write("شاهد هذا الفيديو الممتع لفهم صراع الحركات وقوة الهمزة:")
    # عرض الفيديو مباشرة في الصفحة
    st.video("https://www.youtube.com/watch?v=R9P_O1A6A_I")
    # وضع رابط مباشر للضغط عليه
    st.markdown("""
        <div style="text-align: center;">
            <a href="https://www.youtube.com/watch?v=R9P_O1A6A_I" target="_blank" class="video-link">
                🔗 اضغط هنا لفتح الفيديو في صفحة جديدة
            </a>
        </div>
    """, unsafe_allow_html=True)

st.write("---")

# Barre de progression
prog = st.session_state.step / len(defis)
st.progress(prog)
st.write(f"📊 التمرين رقم {st.session_state.step + 1} من {len(defis)}")

if st.session_state.step < len(defis):
    actuel = defis[st.session_state.step]
    
    # Affichage du mot
    st.markdown(f'<div class="word-box">{actuel["mot"].replace("?", "<span style=\"color:var(--gold)\">؟</span>")}</div>', unsafe_allow_html=True)
    
    st.info("💡 انظر إلى حركة الهمزة وما قبلها، ثم اختر الكرسي الصحيح!")

    # Boutons de réponse
    cols = st.columns(3)
    for i, opt in enumerate(actuel["options"]):
        if cols[i].button(opt, key=f"btn_{st.session_state.step}_{opt}"):
            if opt == actuel["correct"]:
                st.balloons()
                speak_arabic("إجابة صحيحة، أحسنتِ")
                st.success(f"✅ مذهل! {actuel['exp']}")
                st.session_state.score += 10
                st.session_state.step += 1
                st.rerun()
            else:
                speak_arabic("إجابة خاطئة، حاولي مرة أخرى")
                st.error("❌ إجابة غير صحيحة. راجعي دليل القواعد وحاولي مجدداً!")

else:
    # Fin du parcours
    st.balloons()
    speak_arabic("مبروك يا بطلة، لقد أكملت التحدي بنجاح")
    st.markdown('<div class="word-box" style="font-size:45px !important;">🎊 أحسنتِ يا بطلة!<br>لقد أتقنتِ قواعد الهمزة</div>', unsafe_allow_html=True)
    st.metric("مجموع نقاطك النهائي", f"{st.session_state.score} / 100")
    
    if st.button("🔄 إعادة التحدي من جديد"):
        st.session_state.score = 0
        st.session_state.step = 0
        st.rerun()

# Pied de page
st.markdown("---")
st.caption("© 2026 جميع الحقوق محفوظة لمنصة بَرَاعِم لُغَتي - كلية الآداب والفنون - UDL-SBA")
