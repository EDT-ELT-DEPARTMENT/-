import streamlit as st

# Configuration de la page
st.set_page_config(page_title="بَرَاعِم لُغَتي", layout="centered")

# CSS pour garder votre style visuel (Bordeaux et Or)
st.markdown("""
    <style>
    :root {
        --bordeaux: #800000;
        --gold: #d4af37;
    }
    .main { background-color: #fdfaf6; }
    h1 { color: var(--bordeaux); text-align: center; font-family: 'Amiri', serif; }
    .stButton>button { 
        background-color: var(--bordeaux); color: white; 
        font-size: 24px; border-radius: 12px; width: 100%;
        border: 2px solid var(--gold); transition: 0.3s;
    }
    .stButton>button:hover { background-color: var(--gold); color: black; }
    .word-box { 
        font-size: 60px; text-align: center; padding: 20px;
        background: white; border-radius: 15px; 
        box-shadow: 0 4px 15px rgba(0,0,0,0.1); margin: 20px 0;
    }
    </style>
    """, unsafe_allow_html=True)

# En-tête de la Startup
st.title("🎓 منصة بَرَاعِم لُغَتي")
st.markdown("<p style='text-align:center;'>مشروع شركة ناشئة - كلية الآداب والفنون - UDL-SBA</p>", unsafe_allow_html=True)

# Initialisation du score
if 'score' not in st.session_state:
    st.session_state.score = 0

# Contenu pédagogique (Niveau 3 & 4)
st.info("تحدي مبارزة الحركات 🤺: اختر الكرسي المناسب للهزة")

# Affichage du mot
st.markdown('<div class="word-box">سُـ<span style="color:#d4af37">؟</span>ال</div>', unsafe_allow_html=True)

# Options de réponse
cols = st.columns(3)

if cols[0].button("ؤ"):
    st.success("✅ أحسنت! الضمة أقوى من الفتحة.")
    st.balloons()
    st.session_state.score += 10
    
if cols[1].button("ئ"):
    st.error("❌ خطأ! الكسرة غير موجودة هنا.")

if cols[2].button("أ"):
    st.error("❌ خطأ! الفتحة أضعف من الضمة.")

# Tableau de bord
st.sidebar.header("📊 لوحة التحكم")
st.sidebar.metric("النقاط المستحقة", st.session_state.score)
st.sidebar.write("---")
st.sidebar.write("**إعداد:** الأستاذ ميلوعة فريد")
st.sidebar.caption("© 2026 جميع الحقوق محفوظة")
