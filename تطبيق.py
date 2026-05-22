import streamlit as st
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
import io
import os
import pandas as pd
from datetime import datetime

# ==========================================
# CONFIGURATION ET CONSTANTES
# ==========================================
TITRE_PLATEFORME = "Plateforme de gestion des EDTs-S2-2026-Département d'Électrotechnique-Faculté de génie électrique-UDL-SBA"

DEPARTEMENTS = [
    "Département d'Électrotechnique",
    "Département d'Électronique",
    "Département d'Automatique",
    "Département de Télécommunications"
]

TYPES_DOCUMENTS = [
    "Bordereau d'envoi",
    "Procès-verbal (PV) de réunion",
    "PV de surveillance",
    "PV du Comité Pédagogique",
    "Réunion du Conseil de Discipline"
]

OPTIONS_DESTINATAIRES = [
    "Le Doyen de la faculté",
    "Le vice Doyen de la Post graduation",
    "Le vice Doyen de la graduation",
    "Autres"
]

# ==========================================
# FONCTIONS TECHNIQUES DE STRUCTURE
# ==========================================
def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    """Définit l'espacement interne (padding) des cellules d'un tableau."""
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('w:top', top), ('w:bottom', bottom), ('w:left', left), ('w:right', right)]:
        node = OxmlElement(m)
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def ajouter_champ_page(run, type_champ):
    """Injecte un champ de numérotation dynamique (PAGE ou NUMPAGES) dans un paragraphe Word."""
    fldChar1 = OxmlElement('w:fldChar')
    fldChar1.set(qn('w:fldCharType'), 'begin')
    instrText = OxmlElement('w:instrText')
    instrText.set(qn('xml:space'), 'preserve')
    instrText.text = type_champ
    fldChar2 = OxmlElement('w:fldChar')
    fldChar2.set(qn('w:fldCharType'), 'separate')
    fldChar3 = OxmlElement('w:fldChar')
    fldChar3.set(qn('w:fldCharType'), 'end')
    
    run._r.append(fldChar1)
    run._r.append(instrText)
    run._r.append(fldChar2)
    run._r.append(fldChar3)

# ==========================================
# GÉNÉRATEUR DE BORDEREAU ISO STRICT
# ==========================================
def generer_bordereau_iso(departement, donnees):
    doc = Document()
    
    # Configuration des marges globales de la page (0.8 pouce partout)
    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)
        
        # Propagation du pied de page sur toutes les pages
        section.different_first_page_header_footer = False
        
        # Structure du pied de page rectifié
        footer = section.footer
        footer_p = footer.paragraphs[0]
        
        footer_p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        footer_pPr = footer_p._p.get_or_add_pPr()
        tabs = OxmlElement('w:tabs')
        
        # 1. Taquet au centre pour la référence (Centre à ~ 3.45 pouces = 4968 dxa)
        tab_centre = OxmlElement('w:tab')
        tab_centre.set(qn('w:val'), 'center')
        tab_centre.set(qn('w:pos'), '4968')
        tabs.append(tab_centre)
        
        # 2. Taquet à l'extrême droite pour les numéros de page (Extrémité à 6.9 pouces = 9936 dxa)
        tab_droite = OxmlElement('w:tab')
        tab_droite.set(qn('w:val'), 'right')
        tab_droite.set(qn('w:pos'), '9936')
        tabs.append(tab_droite)
        
        footer_pPr.append(tabs)
        
        # Premier saut vers le centre pour y écrire le code de référence
        footer_p.add_run("\t")
        r_ref_fixe = footer_p.add_run("Réf : UDL-GEL-ER-004-2026")
        r_ref_fixe.font.name = 'Calibri'
        r_ref_fixe.font.size = Pt(11)
        
        # Deuxième saut vers l'extrême droite pour y loger la pagination automatique
        footer_p.add_run("\t")
        
        r_page_actuelle = footer_p.add_run()
        r_page_actuelle.font.name = 'Calibri'
        r_page_actuelle.font.size = Pt(11)
        ajouter_champ_page(r_page_actuelle, "PAGE")
        
        r_separateur = footer_p.add_run("/")
        r_separateur.font.name = 'Calibri'
        r_separateur.font.size = Pt(11)
        
        r_total_pages = footer_p.add_run()
        r_total_pages.font.name = 'Calibri'
        r_total_pages.font.size = Pt(11)
        ajouter_champ_page(r_total_pages, "NUMPAGES")

    # 1. STRUCTURE DE L'EN-TÊTE VIA UN TABLEAU INVISIBLE
    header_table = doc.add_table(rows=1, cols=2)
    header_table.alignment = WD_ALIGN_PARAGRAPH.CENTER
    header_table.autofit = False
    
    header_table.columns[0].width = Inches(1.2)
    header_table.columns[1].width = Inches(5.7)
    
    cell_logo = header_table.rows[0].cells[0]
    cell_texte = header_table.rows[0].cells[1]
    
    tblPr = header_table._tbl.tblPr
    tblBorders = OxmlElement('w:tblBorders')
    for border_name in ['top', 'left', 'bottom', 'right', 'insideH', 'insideV']:
        border = OxmlElement(f'w:{border_name}')
        border.set(qn('w:val'), 'none')
        tblBorders.append(border)
    tblPr.append(tblBorders)

    # Insertion du Logo (Largeur 80 pixels = 0.833 pouces)
    p_logo = cell_logo.paragraphs[0]
    p_logo.alignment = WD_ALIGN_PARAGRAPH.LEFT
    
    nom_fichier_logo = "logo.PNG"
    if os.path.exists(nom_fichier_logo):
        p_logo.add_run().add_picture(nom_fichier_logo, width=Inches(0.833))
    else:
        r_alt = p_logo.add_run("[LOGO UNIVERSITÉ]")
        r_alt.font.name = 'Calibri'
        r_alt.font.size = Pt(8)
        r_alt.font.italic = True

    # Insertion des textes officiels de l'en-tête (Calibri)
    p_en_tete = cell_texte.paragraphs[0]
    p_en_tete.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    r1 = p_en_tete.add_run("RÉPUBLIQUE ALGÉRIENNE DÉMOCRATIQUE ET POPULAIRE\n")
    r1.bold = True
    r1.font.size = Pt(11)
    r1.font.name = 'Calibri'
    
    r2 = p_en_tete.add_run(
        "Ministère de l'Enseignement Supérieur et de la Recherche Scientifique\n"
        "Université Djillali Liabes - Sidi Bel Abbès\n"
        "Faculté de Génie Électrique\n"
    )
    r2.font.size = Pt(10)
    r2.font.name = 'Calibri'
    
    r_dept = p_en_tete.add_run(f"{departement.upper()}\n")
    r_dept.bold = True
    r_dept.font.size = Pt(11)
    r_dept.font.name = 'Calibri'

    doc.add_paragraph("\n")

    # 2. RÉFÉRENCE CHRONOLOGIQUE
    p_ref = doc.add_paragraph()
    p_ref.alignment = WD_ALIGN_PARAGRAPH.LEFT
    r_ref = p_ref.add_run(f"N° : {donnees['num_reference']}/ F.G.E/ V.D.E.Q.L.E/2026")
    r_ref.font.size = Pt(10)
    r_ref.font.name = 'Calibri'
    r_ref.bold = True

    doc.add_paragraph("\n")

    # 3. TITRE DU BORDEREAU (Taille 36, Calibri, Italique, Souligné)
    p_titre = doc.add_paragraph()
    p_titre.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_titre = p_titre.add_run("BORDEREAU D’ENVOI")
    r_titre.font.name = 'Calibri'
    r_titre.font.size = Pt(36)
    r_titre.italic = True
    r_titre.underline = True
    r_titre.bold = True
    
    doc.add_paragraph("\n")

    # 4. DESTINATAIRE CONSTRUIT DYNAMIQUEMENT (Calibri)
    p_dest = doc.add_paragraph()
    p_dest.alignment = WD_ALIGN_PARAGRAPH.LEFT
    r_dest = p_dest.add_run(f"A monsieur : {donnees['destinataire']}")
    r_dest.bold = True
    r_dest.font.size = Pt(12)
    r_dest.font.name = 'Calibri'

    doc.add_paragraph("\n")

    # 5. TABLEAU DE TRANSMISSION MULTI-LIGNES
    liste_pieces = donnees['liste_pieces']
    nb_lignes_totatles = 2 + len(liste_pieces)
    
    table = doc.add_table(rows=nb_lignes_totatles, cols=3)
    table.style = 'Table Grid'
    
    table.columns[0].width = Inches(4.5)
    table.columns[1].width = Inches(0.8)
    table.columns[2].width = Inches(1.7)

    # Ligne 1 : En-têtes fixes
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = "Désignation des pièces"
    hdr_cells[1].text = "Nbre"
    hdr_cells[2].text = "Observations"
    
    for cell in hdr_cells:
        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        cell.paragraphs[0].runs[0].font.bold = True
        cell.paragraphs[0].runs[0].font.name = 'Calibri'
        cell.paragraphs[0].runs[0].font.size = Pt(10)
        set_cell_margins(cell, top=120, bottom=120)

    # Ligne 2 : Formule d'accompagnement
    row_joint = table.rows[1].cells
    row_joint[0].text = "Veuillez trouver ci-joint :"
    row_joint[0].paragraphs[0].runs[0].font.italic = True
    row_joint[0].paragraphs[0].runs[0].font.name = 'Calibri'
    row_joint[0].paragraphs[0].runs[0].font.size = Pt(10)
    set_cell_margins(row_joint[0], top=80, bottom=80)

    # Lignes Dynamiques
    for index, piece in enumerate(liste_pieces):
        row_idx = 2 + index
        current_row = table.rows[row_idx].cells
        
        current_row[0].text = str(piece["Désignation des pièces"])
        current_row[1].text = str(piece["Nbre"])
        current_row[2].text = str(piece["Observations"])
        
        for i, cell in enumerate(current_row):
            set_cell_margins(cell, top=150, bottom=300)
            if len(cell.paragraphs[0].runs) > 0:
                cell.paragraphs[0].runs[0].font.name = 'Calibri'
                cell.paragraphs[0].runs[0].font.size = Pt(10)
            if i == 1:
                cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

    doc.add_paragraph("\n\n")

    # 6. SIGNATURES ET ACCUSÉ DE RÉCEPTION
    p_signatures = doc.add_paragraph()
    p_signatures.alignment = WD_ALIGN_PARAGRAPH.LEFT
    date_texte = donnees['date_creation'].strftime('%d/%m/%Y')
    run_sig = p_signatures.add_run(f"Sidi bel Abbès le : {date_texte}\t\t\t\tChef de département")
    run_sig.font.name = 'Calibri'
    run_sig.font.size = Pt(11)
    run_sig.bold = True

    doc.add_paragraph("\n\n\n\n")

    p_accuse = doc.add_paragraph()
    p_accuse.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run_accuse = p_accuse.add_run("Accusé de réception    ")
    run_accuse.font.name = 'Calibri'
    run_accuse.font.size = Pt(10)
    run_accuse.font.underline = True
    run_accuse.bold = True

    return doc

def generer_pv_generique(departement, type_pv, donnees):
    """Générateur secondaire de secours (Calibri)."""
    doc = Document()
    p = doc.add_paragraph()
    run = p.add_run(f"{type_pv} - {departement}\nDocument en cours.")
    run.font.name = 'Calibri'
    return doc

# ==========================================
# INTERFACE UTILISATEUR STREAMLIT
# ==========================================
st.set_page_config(page_title="Générateur ISO Destinataire Dynamique", layout="wide")

st.caption(TITRE_PLATEFORME)
st.title("Gestion Administrative - Bordereaux & PVs")

col_dept, col_doc = st.columns(2)
with col_dept:
    dept_choisi = st.selectbox("Département émetteur :", DEPARTEMENTS)
with col_doc:
    doc_choisi = st.selectbox("Nature du document à générer :", TYPES_DOCUMENTS)

st.divider()
st.subheader(f"Formulaire d'édition - {doc_choisi}")

donnees_doc = {}

if doc_choisi == "Bordereau d'envoi":
    col_ref, col_date = st.columns(2)
    with col_ref:
        donnees_doc['num_reference'] = st.text_input("Référence séquentielle (Ex: 27)", value="27")
    with col_date:
        donnees_doc['date_creation'] = st.date_input("Date d'édition", datetime.now())
        
    # ----------------------------------------------------
    # ZONE DESTINATAIRE : SÉLECTEUR ET CHAMP LIBRE DYNAMIQUE
    # ----------------------------------------------------
    st.markdown("##### Destinataire officiel")
    choix_dest = st.selectbox(
        "Sélectionnez le destinataire dans la liste :", 
        OPTIONS_DESTINATAIRES,
        index=0
    )
    
    if choix_dest == "Autres":
        donnees_doc['destinataire'] = st.text_input("Veuillez saisir la destination personnalisée :", value="")
    else:
        donnees_doc['destinataire'] = choix_dest
        
    st.markdown("---")
    st.write("**Configuration du Tableau de Transmission**")
    
    df_initial = pd.DataFrame([
        {"Désignation des pièces": "Fiches de vœux du second semestre", "Nbre": 12, "Observations": "Pour examen"},
        {"Désignation des pièces": "Procès-verbal de délibération", "Nbre": 2, "Observations": "Pour affichage"}
    ])
    
    df_edite = st.data_editor(
        df_initial, 
        num_rows="dynamic", 
        use_container_width=True,
        column_config={
            "Désignation des pièces": st.column_config.TextColumn(width="medium", required=True),
            "Nbre": st.column_config.NumberColumn(width="small", min_value=1, required=True),
            "Observations": st.column_config.TextColumn(width="medium")
        }
    )
    donnees_doc['liste_pieces'] = df_edite.to_dict(orient="records")

else:
    with st.form("form_autres"):
        donnees_doc['date_creation'] = st.date_input("Date", datetime.now())
        donnees_doc['contenu'] = st.text_area("Contenu textuel")
        st.form_submit_button("Valider")

# Action finale de compilation
if doc_choisi == "Bordereau d'envoi":
    if st.button("Compiler et Générer le Bordereau Officiel"):
        # Blocage de sécurité si le choix "Autres" est laissé vide
        if not donnees_doc['destinataire'].strip():
            st.error("Erreur : Le champ de destination personnalisée ne peut pas être vide.")
        else:
            try:
                document_final = generer_bordereau_iso(dept_choisi, donnees_doc)
                
                output_stream = io.BytesIO()
                document_final.save(output_stream)
                output_stream.seek(0)
                
                st.success("✓ Bordereau généré avec succès avec le destinataire sélectionné.")
                
                nom_fichier_export = f"Bordereau_{dept_choisi.replace(' ', '_')}.docx"
                st.download_button(
                    label="⬇️ Télécharger le document (.docx)",
                    data=output_stream,
                    file_name=nom_fichier_export,
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
            except Exception as error:
                st.error(f"Échec de l'opération de génération : {str(error)}")
