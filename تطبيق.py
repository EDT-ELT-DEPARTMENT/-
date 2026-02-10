import streamlit as st

# Configuration de l'interface aux couleurs de la Faculté (Bordeaux & Or)
st.set_page_config(page_title="بَرَاعِم لُغَتي", page_icon="🎓")

st.markdown("""
    <style>
    .main { background-color: #fdfaf6; }
    h1 { color: #800000; text-align: center; }
    .stButton>button { background-color: #800000; color: white; border-radius: 10px; height: 3em; font-size: 20px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎓 منصة بَرَاعِم لُغَتي")
st.write("### مشروع شركة ناشئة - قسم اللغة العربية - UDL-SBA")
st.divider()

# Logique de l'exercice sur la Hamza
st.write("#### تحدي الهمزة المتوسطة: اختر الرسم الصحيح للكلمة")

col1, col2 = st.columns([2, 1])

with col1:
    mot_a_completer = "بِـ...ـر"
    st.info(f"كيف نكتب الكلمة: **{mot_a_completer}** ؟")
    
    choix = st.columns(3)
    if choix[0].button("أ"):
        st.error("❌ خطأ! الفتحة أضعف من الكسرة.")
    if choix[1].button("ؤ"):
        st.error("❌ خطأ! الضمة أضعف من الكسرة.")
    if choix[2].button("ئ"):
        st.success("✅ ممتاز! الكسرة هي أقوى الحركات وتناسبها النبرة.")
        st.balloons()

with col2:
    st.metric("النقاط", "10")
    st.write("**القاعدة:**")
    st.caption("الكسرة ⬅️ ئ")
    st.caption("الضمة ⬅️ ؤ")
    st.caption("الفتحة ⬅️ أ")

st.sidebar.write("---")
st.sidebar.write("إشراف: الطالبة عبو ماجدة")

