from flask import Flask, render_template, jsonify

# Configuration de Flask pour reconnaître votre fichier HTML en arabe
app = Flask(__name__, template_folder='templates')

# Base de données de la Hamza (Niveaux 3AP et 4AP)
questions_hamza = [
    {"mot": "سـ?ـل", "choix": "أ", "complet": "سَأَلَ", "regle": "الفتحة تناسب الألف"},
    {"mot": "مـ?ـمن", "choix": "ؤ", "complet": "مُؤْمِن", "regle": "الضمة أقوى من السكون"},
    {"mot": "بـ?ـر", "choix": "ئ", "complet": "بِئْر", "regle": "الكسرة هي الأقوى"}
]

@app.route('/')
def home():
    return render_template('واجهة.html', questions=questions_hamza)

if __name__ == '__main__':
    app.run(debug=True)