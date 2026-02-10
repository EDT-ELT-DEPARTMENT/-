import streamlit as st

# --- 1. إعدادات الصفحة الأساسية ---
st.set_page_config(
    page_title="بَرَاعِم لُغَتي - تحدي الصور",
    page_icon="🎨",
    layout="centered"
)

# --- 2. وظيفة النطق الصوتي بالعربية ---
def speak_arabic(text):
    """تحويل النص إلى كلام مسموع للمتصفح"""
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

# --- 3. تصميم الواجهة (CSS) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&family=Cairo:wght@400;700&display=swap');

    :root {
        --bordeaux: #800000;
        --gold: #d4af37;
        --bg-color: #fdfaf6;
    }
    
    .main { background-color: var(--bg-color); }
    
    /* العناوين */
    h1 { color: var(--bordeaux); font-family: 'Amiri', serif; font-size: 50px !important; text-align: center; }
    h3 { font-family: 'Cairo', sans-serif; font-size: 26px !important; color: #333; text-align: center; }

    /* صندوق الصورة والكلمة */
    .image-exercise-container {
        background: white;
        padding: 30px;
        border-radius: 25px;
        border: 3px solid var(--gold);
        text-align: center;
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }

    .word-box { 
        font-size: 90px !important; 
        color: var(--bordeaux);
        font-family: 'Amiri', serif;
        font-weight: bold;
        margin: 20px 0;
    }

    /* الأزرار الكبيرة */
    .stButton>button { 
        background-color: var(--bordeaux); 
        color: white !important; 
        font-size: 45px !important; 
        font-family: 'Amiri', serif !important;
        border-radius: 20px; 
        width: 100%;
        height: 100px;
        border: 4px solid var(--gold);
        transition: 0.3s;
    }
    .stButton>button:hover { 
        background-color: var(--gold); 
        color: black !important; 
        transform: scale(1.05); 
    }

    /* دليل القواعد في الجانب */
    .rule-card {
        background-color: white;
        padding: 15px;
        border-radius: 12px;
        border-right: 6px solid var(--gold);
        margin-bottom: 10px;
        text-align: right;
        direction: rtl;
        font-family: 'Cairo', sans-serif;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. تهيئة المتغيرات ---
if 'step_image' not in st.session_state:
    st.session_state.step_image = 0
if 'score_image' not in st.session_state:
    st.session_state.score_image = 0

# --- 5. قاعدة بيانات تمارين الصور ---
# ملاحظة: استخدمت روابط صور تعليمية واضحة
defis_images = [
    {
        "img": "https://img.freepik.com/free-vector/fountain-pen-concept-illustration_114360-12347.jpg", 
        "mot": "بِـ?ـر", 
        "options": ["ئ", "ؤ", "أ"], 
        "correct": "ئ", 
        "hint": "الصورة لبئر ماء. الكسرة تحت الباء قوية جداً!"
    },
    {
        "img": "https://img.freepik.com/free-vector/human-head-with-brain-concept_23-2148450123.jpg", 
        "mot": "رَ?َس", 
        "options": ["أ", "ؤ", "ئ"], 
        "correct": "أ", 
        "hint": "هذا رأس إنسان. الفتحة فوق الراء تناسب الألف."
    },
    {
        "img": "https://img.freepik.com/free-vector/flat-question-mark-background_23-2148149830.jpg", 
        "mot": "سُـ?ـال", 
        "options": ["ؤ", "ئ", "أ"], 
        "correct": "ؤ", 
        "hint": "هذه علامة سؤال. الضمة فوق السين تناسب الواو."
    },
    {
        "img": "https://img.freepik.com/free-vector/wolf-concept-illustration_114360-16576.jpg", 
        "mot": "ذِ?ْب", 
        "options": ["ئ", "ؤ", "أ"], 
        "correct": "ئ", 
        "hint": "هذا ذئب بري. الكسرة تحت الذال تناسب النبرة."
    }
]

# --- 6. القائمة الجانبية (Sidebar) ---
with st.sidebar:
    st.markdown("<h2 style='text-align:right;'>📚 قاموس القواعد</h2>", unsafe_allow_html=True)
    st.markdown("""
    <div class="rule-card">
        <b>تذكر يا بطل:</b><br>
        • الكسرة (ئ) ⬅️ الأقوى<br>
        • الضمة (ؤ) ⬅️ قوية<br>
        • الفتحة (أ) ⬅️ أقل قوة
    </div>
    """, unsafe_allow_html=True)
    st.write("---")
    st.metric("نقاط تحدي الصور 🎨", st.session_state.score_image)
    st.markdown(f"<p style='text-align:center;'>المشرف: <b>الأستاذ ميلوى فريد</b></p>", unsafe_allow_html=True)

# --- 7. الواجهة الرئيسية ---
st.markdown("<h1>🎨 تحدي الصور والكلمات</h1>", unsafe_allow_html=True)
st.markdown("<h3>انظر إلى الصورة، ثم أكمل الكلمة بالهمزة الصحيحة</h3>", unsafe_allow_html=True)

# شريط التقدم
prog = st.session_state.step_image / len(defis_images)
st.progress(prog)

if st.session_state.step_image < len(defis_images):
    current = defis_images[st.session_state.step_image]
    
    # حاوية التمرين
    st.markdown('<div class="image-exercise-container">', unsafe_allow_html=True)
    
    # عرض الصورة
    st.image(current["img"], width=300)
    
    # عرض الكلمة الناقصة
    st.markdown(f'<div class="word-box">{current["mot"].replace("?", "؟")}</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # أزرار الخيارات
    cols = st.columns(3)
    for i, opt in enumerate(current["options"]):
        if cols[i].button(opt, key=f"img_btn_{opt}_{st.session_state.step_image}"):
            if opt == current["correct"]:
                st.balloons()
                speak_arabic("أحسنتِ، إجابة صحيحة")
                st.success(f"✅ رائع! {current['hint']}")
                st.session_state.score_image += 25
                st.session_state.step_image += 1
                st.rerun()
            else:
                speak_arabic("خطأ، حاولي مرة أخرى")
                st.error("❌ ركزي في الصورة وفي حركة الحرف الأول!")

else:
    # شاشة النهاية
    st.balloons()
    speak_arabic("عمل رائع، لقد أنهيتِ تحدي الصور")
    st.markdown('<div class="image-exercise-container">', unsafe_allow_html=True)
    st.markdown('<div class="word-box" style="font-size:40px !important;">🎊 أحسنتِ يا بطلة الصور!</div>', unsafe_allow_html=True)
    st.metric("النتيجة النهائية", f"{st.session_state.score_image} نقطة")
    
    if st.button("🔄 إعادة تحدي الصور"):
        st.session_state.step_image = 0
        st.session_state.score_image = 0
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- 8. التذييل ---
st.markdown("---")
st.caption("© 2026 منصة بَرَاعِم لُغَتي - إعداد الطالبة: عبو ماجدة - كلية الآداب والفنون")
