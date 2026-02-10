import streamlit as st

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="بَرَاعِم لُغَتي",
    page_icon="🎓",
    layout="centered"
)

# --- STYLE CSS (Police large et Couleurs Académiques) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&family=Cairo:wght@400;700&display=swap');

    :root {
        --bordeaux: #800000;
        --gold: #d4af37;
        --bg-color: #fdfaf6;
    }
    
    .main { background-color: var(--bg-color); }
    
    /* Titres */
    h1 { color: var(--bordeaux); font-family: 'Amiri', serif; font-size: 50px !important; text-align: center; }
    h2 { color: var(--bordeaux); font-family: 'Cairo', sans-serif; font-size: 35px !important; border-bottom: 2px solid var(--gold); }
    h3 { font-family: 'Cairo', sans-serif; font-size: 30px !important; color: #333; text-align: center; }

    /* Boîte du mot (Très grande pour l'élève) */
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

    /* Boutons de réponse */
    .stButton>button { 
        background-color: var(--bordeaux); 
        color: white !important; 
        font-size: 45px !important; 
        font-family: 'Amiri', serif !important;
        border-radius: 15px; 
        width: 100%;
        height: 100px;
        border: 3px solid var(--gold);
        transition: 0.3s;
    }
    .stButton>button:hover { 
        background-color: var(--gold); 
        color: black !important; 
        transform: scale(1.05); 
    }

    /* Texte des règles */
    .rule-text {
        font-size: 24px !important;
        line-height: 1.6;
        font-family: 'Cairo', sans-serif;
        text-align: right;
        background: #fff;
        padding: 20px;
        border-radius: 15px;
        border-right: 5px solid var(--gold);
    }
    </style>
    """, unsafe_allow_html=True)

# --- INITIALISATION DES VARIABLES ---
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'step' not in st.session_state:
    st.session_state.step = 0

# --- BASE DE DONNÉES DES DÉFIS ---
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

# --- INTERFACE PRINCIPALE ---

st.markdown("<h1>🎓 منصة بَرَاعِم لُغَتي</h1>", unsafe_allow_html=True)
st.markdown("<h3>مشروع شركة ناشئة - الطالبة: عبو ماجدة</h3>", unsafe_allow_html=True)

# --- SECTION DES RÈGLES (NOUVEAU) ---
with st.sidebar:
    st.markdown("<h2 style='text-align:center;'>📚 دليل القواعد</h2>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="rule-text">
    <b>قاعدة أقوى الحركات:</b><br>
    ننظر إلى حركة الهمزة وحركة الحرف الذي قبلها، ونكتبها على ما يناسب الحركة الأقوى:<br><br>
    1️⃣ <b>الكسرة:</b> هي الأقوى وتناسبها <b>الياء (ئ)</b>.<br>
    2️⃣ <b>الضمة:</b> تليها في القوة وتناسبها <b>الواو (ؤ)</b>.<br>
    3️⃣ <b>الفتحة:</b> تليها في القوة وتناسبها <b>الألف (أ)</b>.<br>
    4️⃣ <b>السكون:</b> هو الأضعف.
    </div>
    """, unsafe_allow_html=True)
    
    st.write("---")
    st.metric("نقاطك الحالية 🌟", st.session_state.score)
    st.markdown(f"<p style='text-align:center; color:maroon;'><b>الأستاذ المشرف:<br>ميلوى فريد</b></p>", unsafe_allow_html=True)

# --- CONTENU DU JEU ---

tab1, tab2 = st.tabs(["🎮 ابدأ التحدي", "📖 مراجعة القواعد"])

with tab1:
    # Barre de Progression
    prog = st.session_state.step / len(defis)
    st.progress(prog)
    st.write(f"📊 التحدي الحالي: {st.session_state.step + 1} / {len(defis)}")

    if st.session_state.step < len(defis):
        actuel = defis[st.session_state.step]
        
        # Affichage du mot
        st.markdown(f'<div class="word-box">{actuel["mot"].replace("?", "<span style=\"color:var(--gold)\">؟</span>")}</div>', unsafe_allow_html=True)
        
        st.info("💡 ركّز جيداً في حركة الهمزة والحرف الذي قبلها!")

        # Boutons de réponse
        cols = st.columns(3)
        for i, opt in enumerate(actuel["options"]):
            if cols[i].button(opt, key=f"btn_{st.session_state.step}_{opt}"):
                if opt == actuel["correct"]:
                    st.balloons()
                    st.success(f"✅ مذهل! {actuel['exp']}")
                    st.session_state.score += 10
                    st.session_state.step += 1
                    st.rerun()
                else:
                    st.error("❌ حاولي مرة أخرى! ارجعي لدليل القواعد في الجانب.")
    else:
        st.balloons()
        st.markdown('<div class="word-box" style="font-size:40px !important;">🎊 أحسنتِ يا بطلة!<br>أكملتِ كل التمارين بنجاح</div>', unsafe_allow_html=True)
        st.metric("النتيجة النهائية", f"{st.session_state.score} نقطة")
        if st.button("🔄 إعادة التحدي"):
            st.session_state.score = 0
            st.session_state.step = 0
            st.rerun()

with tab2:
    st.markdown("## 📖 قواعد رسم الهمزة المتوسطة")
    st.video("https://www.youtube.com/watch?v=R9P_O1A6A_I")
    st.markdown("""
    ### كيف أحدد كرسي الهمزة؟
    1. حدد حركة الهمزة (مثلاً: سُـؤَال -> الهمزة مفتوحة).
    2. حدد حركة الحرف قبلها (مثلاً: سُـؤَال -> السين مضمومة).
    3. قارن بين الحركتين: الضمة أقوى من الفتحة، إذاً نختار **الواو**.
    
    ### أمثلة للتدريب:
    * **بِئْر:** كسرة + سكون = الكسرة تفوز (ئ).
    * **رَأْس:** فتحة + سكون = الفتحة تفوز (أ).
    * **مُؤْمِن:** ضمة + سكون = الضمة تفوز (ؤ).
    """)

# Footer
st.markdown("---")
st.caption("© 2026 جميع الحقوق محفوظة لمنصة بَرَاعِم لُغَتي - جامعة سيدي بلعباس")
