import streamlit as st

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="بَرَاعِم لُغَتي",
    page_icon="🎓",
    layout="centered"
)

# --- STYLE CSS AMÉLIORÉ (Police large et Couleurs Pro) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&family=Cairo:wght@400;700&display=swap');

    :root {
        --bordeaux: #800000;
        --gold: #d4af37;
        --bg-color: #fdfaf6;
    }
    
    .main { background-color: var(--bg-color); }
    
    /* Titres et Textes */
    h1 { color: var(--bordeaux); font-family: 'Amiri', serif; font-size: 50px !important; text-align: center; }
    h3 { font-family: 'Cairo', sans-serif; font-size: 30px !important; color: #333; text-align: center; }
    p, .stText { font-size: 24px !important; font-family: 'Cairo', sans-serif; }

    /* Zone de la vidéo */
    .video-container {
        background-color: #000;
        border-radius: 20px;
        padding: 10px;
        border: 3px solid var(--gold);
        margin-bottom: 25px;
    }

    /* Boîte du mot (TRÈS GRANDE) */
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

    /* Boutons de réponse (LARGES) */
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

    /* Alertes et Info */
    .stAlert { font-size: 22px !important; border-radius: 15px; }
    </style>
    """, unsafe_allow_html=True)

# --- INITIALISATION ---
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'step' not in st.session_state:
    st.session_state.step = 0

# --- BASE DE DONNÉES ÉTENDUE (10 EXERCICES) ---
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

# --- INTERFACE ---

st.markdown("<h1>🎓 منصة بَرَاعِم لُغَتي</h1>", unsafe_allow_html=True)
st.markdown("<h3>مشروع شركة ناشئة - الطالبة: عبو ماجدة</h3>", unsafe_allow_html=True)

# Section Vidéo
with st.expander("📽️ شاهد درس الهمزة أولاً (صراع الأقوياء)"):
    st.video("https://www.youtube.com/watch?v=R9P_O1A6A_I") # Lien exemple sur la Hamza

# Progression
prog = st.session_state.step / len(defis)
st.progress(prog)
st.write(f"📊 التحدي الحالي: {st.session_state.step + 1} / {len(defis)}")

if st.session_state.step < len(defis):
    actuel = defis[st.session_state.step]
    
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
                st.error("❌ حاولي مرة أخرى! تذكّري أن الكسرة أقوى من الضمة، والضمة أقوى من الفتحة.")

else:
    st.balloons()
    st.markdown('<div class="word-box" style="font-size:40px !important;">🎊 أحسنتِ يا بطلة!<br>أكملتِ كل التمارين بنجاح</div>', unsafe_allow_html=True)
    st.metric("النتيجة النهائية", f"{st.session_state.score} نقطة")
    if st.button("🔄 إعادة التحدي"):
        st.session_state.score = 0
        st.session_state.step = 0
        st.rerun()

# --- SIDEBAR ---
st.sidebar.markdown(f"<h2 style='text-align:center; color:maroon;'>الأستاذ المشرف:<br>ميلوى فريد</h2>", unsafe_allow_html=True)
st.sidebar.write("---")
st.sidebar.metric("نقاطك الحالية 🌟", st.session_state.score)
st.sidebar.markdown("""
**سلم قوة الحركات:**
1. الكسرة (أقوى شيء) ⬅️ **ئ**
2. الضمة ⬅️ **ؤ**
3. الفتحة ⬅️ **أ**
4. السكون (الأضعف)
""")
