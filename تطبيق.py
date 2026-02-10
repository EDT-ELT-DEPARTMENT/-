import streamlit as st

# --- إعدادات الصفحة ---
st.set_page_config(
    page_title="بَرَاعِم لُغَتي",
    page_icon="🎓",
    layout="centered"
)

# --- تنسيق CSS (عنابي وذهبي - نمط أكاديمي) ---
st.markdown("""
    <style>
    :root {
        --bordeaux: #800000;
        --gold: #d4af37;
        --bg-color: #fdfaf6;
    }
    .main { background-color: var(--bg-color); }
    
    /* إطار العنوان */
    .header-box {
        border-bottom: 3px solid var(--gold);
        margin-bottom: 20px;
        padding-bottom: 10px;
        text-align: center;
    }
    
    h1 { color: var(--bordeaux); font-family: 'Amiri', serif; }

    /* قسم الفيديو */
    .video-section {
        background: #000;
        width: 100%;
        height: 250px;
        border-radius: 15px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        margin-bottom: 20px;
        border: 2px solid var(--bordeaux);
    }

    /* صندوق الكلمة */
    .word-box { 
        font-size: 70px; text-align: center; padding: 25px;
        background: white; border-radius: 20px; 
        box-shadow: 0 4px 15px rgba(0,0,0,0.1); margin: 20px 0;
        border: 1px solid #eee;
        font-weight: bold;
    }

    /* تنسيق الأزرار */
    .stButton>button { 
        background-color: var(--bordeaux); color: white; 
        font-size: 28px; border-radius: 12px; width: 100%;
        border: 2px solid var(--gold); height: 70px;
        transition: 0.3s;
    }
    .stButton>button:hover { background-color: var(--gold); color: black; transform: scale(1.05); }
    </style>
    """, unsafe_allow_html=True)

# --- تهيئة متغيرات الجلسة ---
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'step' not in st.session_state:
    st.session_state.step = 0

# --- قاعدة بيانات التحديات (المستوى 3 و 4) ---
defis = [
    {"mot": "سُـ?ـال", "options": ["ؤ", "ئ", "أ"], "correct": "ؤ", "explication": "الضمة أقوى من الفتحة!"},
    {"mot": "بِـ?ـر", "options": ["ئ", "ؤ", "أ"], "correct": "ئ", "explication": "الكسرة هي الملكة، هي الأقوى دائماً!"},
    {"mot": "رَ?َس", "options": ["أ", "ؤ", "ئ"], "correct": "أ", "explication": "الفتحة تغلبت على السكون."},
    {"mot": "مُـ?ـمِن", "options": ["ؤ", "أ", "ئ"], "correct": "ؤ", "explication": "الضمة تسبق السكون."}
]

# --- عرض الواجهة ---

# العنوان الرئيسي
st.markdown("""
    <div class="header-box">
        <h1>🎓 منصة بَرَاعِم لُغَتي</h1>
        <p style="color: #555;"><b>مشروع شركة ناشئة - كلية الآداب والفنون - UDL-SBA</b></p>
    </div>
    """, unsafe_allow_html=True)

# قسم الفيديو (Placeholder)
st.markdown("""
    <div class="video-section">
        <div style="text-align:center;">
            <p style="font-size: 20px;">📽️ فيديو تعليمي</p>
            <p style="font-style: italic; color: #bdc3c7; font-size: 14px;">"صراع الأقوياء على كرسي الهمزة"</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

# شريط التقدم
progression = st.session_state.step / len(defis)
st.progress(progression)

# منطقة اللعب
if st.session_state.step < len(defis):
    actuel = defis[st.session_state.step]
    
    st.info("تحدي مبارزة الحركات 🤺: اختر الكرسي المناسب للهزة")
    
    # عرض الكلمة مع علامة الاستشهاد بالذهبي
    st.markdown(f'<div class="word-box">{actuel["mot"].replace("?", "<span style=\"color:#d4af37\">؟</span>")}</div>', unsafe_allow_html=True)
    
    # خيارات الإجابة
    cols = st.columns(3)
    for i, opt in enumerate(actuel["options"]):
        if cols[i].button(opt, key=f"btn_{st.session_state.step}_{opt}"):
            if opt == actuel["correct"]:
                st.success(f"✅ أحسنتِ! {actuel['explication']}")
                st.balloons()
                st.session_state.score += 10
                st.session_state.step += 1
                st.rerun()
            else:
                st.error("❌ حاولي مرة أخرى، تذكري سلم قوة الحركات!")

else:
    # نهاية التحدي
    st.balloons()
    st.markdown(f'<div class="word-box" style="font-size:30px;">🎉 مبروك يا بطلة!<br>لقد أنهيتِ التحدي بنجاح</div>', unsafe_allow_html=True)
    if st.button("إعادة التحدي من جديد"):
        st.session_state.score = 0
        st.session_state.step = 0
        st.rerun()

# --- القائمة الجانبية (Sidebar) ---
st.sidebar.header("📊 لوحة التحكم")
st.sidebar.metric("النقاط المستحقة", st.session_state.score)
st.sidebar.write("---")
st.sidebar.write("**إعداد الطالبة:**")
st.sidebar.subheader("عبو ماجدة")
st.sidebar.write("**إشراف:**")
st.sidebar.subheader("الأستاذ ميلوى فريد")
st.sidebar.caption("© 2026 جميع الحقوق محفوظة")
