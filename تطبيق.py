import streamlit as st

# --- إعدادات الصفحة ---
st.set_page_config(
    page_title="بَرَاعِم لُغَتي",
    page_icon="🎓",
    layout="centered"
)

# --- وظيفة النطق الصوتي بالعربية (JavaScript) ---
def speak_arabic(text):
    """وظيفة تجعل المتصفح ينطق النص العربي"""
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

# --- تنسيق CSS (نفس الواجهة الكبيرة والألوان) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&family=Cairo:wght@400;700&display=swap');

    :root {
        --bordeaux: #800000;
        --gold: #d4af37;
        --bg-color: #fdfaf6;
    }
    
    .main { background-color: var(--bg-color); }
    
    h1 { color: var(--bordeaux); font-family: 'Amiri', serif; font-size: 50px !important; text-align: center; }
    h3 { font-family: 'Cairo', sans-serif; font-size: 30px !important; color: #333; text-align: center; }

    .word-box { 
        font-size: 100px !important; 
        text-align: center; 
        padding: 40px;
        background: white; 
        border-radius: 25px; 
        box-shadow: 0 8px 20px rgba(0,0,0,0.1); 
        margin: 30px 0;
        border: 2px solid var(--gold);
        font-family: 'Amiri', serif;
        font-weight: bold;
    }

    .stButton>button { 
        background-color: var(--bordeaux); 
        color: white !important; 
        font-size: 45px !important; 
        font-family: 'Amiri', serif !important;
        border-radius: 15px; 
        width: 100%;
        height: 100px;
        border: 3px solid var(--gold);
    }
    .stButton>button:hover { 
        background-color: var(--gold); 
        color: black !important; 
    }

    .rule-text {
        font-size: 24px !important;
        font-family: 'Cairo', sans-serif;
        text-align: right;
        background: #fff;
        padding: 20px;
        border-radius: 15px;
        border-right: 5px solid var(--gold);
    }
    </style>
    """, unsafe_allow_html=True)

# --- تهيئة المتغيرات ---
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'step' not in st.session_state:
    st.session_state.step = 0

# --- قاعدة البيانات (10 تمارين) ---
defis = [
    {"mot": "سُـ?ـال", "options": ["ؤ", "ئ", "أ"], "correct": "ؤ", "exp": "الضمة أقوى من الفتحة"},
    {"mot": "بِـ?ـر", "options": ["ئ", "ؤ", "أ"], "correct": "ئ", "exp": "الكسرة هي الأقوى دائماً"},
    {"mot": "رَ?َس", "options": ["أ", "ؤ", "ئ"], "correct": "أ", "exp": "الفتحة تغلبت على السكون"},
    {"mot": "مُـ?ـمِن", "options": ["ؤ", "أ", "ئ"], "correct": "ؤ", "exp": "الضمة أقوى من السكون"},
    {"mot": "ذِ?ْب", "options": ["ئ", "أ", "ؤ"], "correct": "ئ", "exp": "الكسرة تناسبها النبرة"},
    {"mot": "سَـ?َـلَ", "options": ["أ", "ئ", "ؤ"], "correct": "أ", "exp": "فتحة مع فتحة تناسب الألف"},
    {"mot": "رِ?َة", "options": ["ئ", "ؤ", "أ"], "correct": "ئ", "exp": "الكسرة أقوى من الفتحة"},
    {"mot": "فَـ?ْس", "options": ["أ", "ؤ", "ئ"], "correct": "أ", "exp": "الفتحة أقوى من السكون"},
    {"mot": "مُـ?َـذِّن", "options": ["ؤ", "أ", "ئ"], "correct": "ؤ", "exp": "الضمة أقوى من الفتحة"},
    {"mot": "بِيـ?َـة", "options": ["ئ", "أ", "ؤ"], "correct": "ئ", "exp": "بعد الياء الساكنة ترسم على النبرة"}
]

# --- الواجهة ---
st.markdown("<h1>🎓 منصة بَرَاعِم لُغَتي</h1>", unsafe_allow_html=True)
st.markdown("<h3>مشروع شركة ناشئة - الطالبة: عبو ماجدة</h3>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("<h2 style='text-align:center;'>📚 دليل القواعد</h2>", unsafe_allow_html=True)
    st.markdown('<div class="rule-text"><b>سلم قوة الحركات:</b><br>1️⃣ الكسرة (ئ)<br>2️⃣ الضمة (ؤ)<br>3️⃣ الفتحة (أ)<br>4️⃣ السكون</div>', unsafe_allow_html=True)
    st.write("---")
    st.metric("نقاطك الحالية 🌟", st.session_state.score)
    st.markdown(f"<p style='text-align:center; color:maroon;'><b>الأستاذ المشرف:<br>ميلوى فريد</b></p>", unsafe_allow_html=True)

# --- منطقة التحدي ---
prog = st.session_state.step / len(defis)
st.progress(prog)

if st.session_state.step < len(defis):
    actuel = defis[st.session_state.step]
    st.markdown(f'<div class="word-box">{actuel["mot"].replace("?", "<span style=\"color:var(--gold)\">؟</span>")}</div>', unsafe_allow_html=True)
    
    cols = st.columns(3)
    for i, opt in enumerate(actuel["options"]):
        if cols[i].button(opt, key=f"btn_{st.session_state.step}_{opt}"):
            if opt == actuel["correct"]:
                st.balloons()
                speak_arabic("إجابة صحيحة، أحسنتِ") # نطق بالعربي
                st.success(f"✅ مذهل! {actuel['exp']}")
                st.session_state.score += 10
                st.session_state.step += 1
                st.rerun()
            else:
                speak_arabic("إجابة خاطئة، حاولي مرة أخرى") # نطق بالعربي
                st.error("❌ حاولي مرة أخرى!")
else:
    st.balloons()
    speak_arabic("تهانينا، لقد أكملت التحدي بنجاح")
    st.markdown('<div class="word-box" style="font-size:40px !important;">🎊 أحسنتِ يا بطلة!</div>', unsafe_allow_html=True)
    if st.button("🔄 إعادة التحدي"):
        st.session_state.score = 0
        st.session_state.step = 0
        st.rerun()

st.markdown("---")
st.caption("© 2026 جميع الحقوق محفوظة لمنصة بَرَاعِم لُغَتي - جامعة سيدي بلعباس")
