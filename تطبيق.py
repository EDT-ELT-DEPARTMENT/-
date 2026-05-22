import streamlit as st
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
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
    "Justification d'absence",
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

MOTIFS_ABSENCE = [
    "Personnel",
    "Médical",
    "Autre"
]

LISTE_SPECIALITES = [
    "Réseeaux électriques",
    "énergies renouvelables",
    "commendes électriques",
    "Master-MCIL",
    "Licence_MCIL",
    "Licence_ELT",
    "Ingénieur",
    "Ingénieur_EI",
    "Ingénieur_RSE"
]

LISTE_ANNEES_ETUDE = [
    "1ère Année Master",
    "2ème Année Master",
    "1ère Année",
    "2ème Année",
    "3ème Année",
    "4ème Année",
    "5ème Année"
]

# ==========================================
# FONCTIONS TECHNIQUES DE STRUCTURE
# ==========================================
def set_cell_margins(cell, top=60, bottom=60, left=120, right=120):
    """Définit l'espacement interne (padding) compact des cellules d'un tableau."""
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('w:top', top), ('w:bottom', bottom), ('w:left', left), ('w:right', right)]:
        node = OxmlElement(m)
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def appliquer_bordure_cellule_noire(cell):
    """Applique une bordure fine noire standard et complète sur tous les côtés d'une cellule."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcBorders = OxmlElement('w:tcBorders')
    for border_name in ['top', 'left', 'bottom', 'right']:
        b = OxmlElement(f'w:{border_name}')
        b.set(qn('w:val'), 'single')
        b.set(qn('w:sz'), '4')
        b.set(qn('w:space'), '0')
        b.set(qn('w:color'), '000000')
        tcBorders.append(b)
    tcPr.append(tcBorders)

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

def initialiser_paragraphe_strict(p):
    """Supprime totalement les espaces et configure un interligne simple strict."""
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.0

def appliquer_structure_pages_sans_ref(doc):
    """Configure les marges globales et positionne le numéro de page à l'extrémité droite du pied de page."""
    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)
        
        section.different_first_page_header_footer = False
        
        footer = section.footer
        footer_p = footer.paragraphs[0]
        initialiser_paragraphe_strict(footer_p)
        
        # Aligner à droite pour forcer l'écriture à l'extrémité droite absolue
        footer_p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        
        r_page_actuelle = footer_p.add_run()
        r_page_actuelle.font.name = 'Calibri'
        r_page_actuelle.font.size = Pt(11)
        ajouter_champ_page(r_page_actuelle, "PAGE")
        
        r_separateur = footer_p.add_run(" / ")
        r_separateur.font.name = 'Calibri'
        r_separateur.font.size = Pt(11)
        
        r_total_pages = footer_p.add_run()
        r_total_pages.font.name = 'Calibri'
        r_total_pages.font.size = Pt(11)
        ajouter_champ_page(r_total_pages, "NUMPAGES")

def inserer_bloc_en_tete_bordereau(doc, departement):
    """Génère l'en-tête standard classique avec logo redimensionné pour le Bordereau d'envoi."""
    header_table = doc.add_table(rows=1, cols=2)
    header_table.alignment = WD_ALIGN_PARAGRAPH.CENTER
    header_table.autofit = False
    header_table.columns[0].width = Inches(1.19)
    header_table.columns[1].width = Inches(5.1)
    
    cell_logo = header_table.rows[0].cells[0]
    cell_texte = header_table.rows[0].cells[1]
    
    tblPr = header_table._tbl.tblPr
    tblBorders = OxmlElement('w:tblBorders')
    for border_name in ['top', 'left', 'bottom', 'right', 'insideH', 'insideV']:
        border = OxmlElement(f'w:{border_name}')
        border.set(qn('w:val'), 'none')
        tblBorders.append(border)
    tblPr.append(tblBorders)

    p_logo = cell_logo.paragraphs[0]
    initialiser_paragraphe_strict(p_logo)
    p_logo.alignment = WD_ALIGN_PARAGRAPH.LEFT
    
    nom_fichier_logo = "logo.PNG"
    if os.path.exists(nom_fichier_logo):
        p_logo.add_run().add_picture(nom_fichier_logo, width=Inches(0.58), height=Inches(0.94))
    else:
        r_alt = p_logo.add_run("[LOGO]")
        r_alt.font.name = 'Calibri'
        r_alt.font.size = Pt(11)
        r_alt.font.italic = True

    p_en_tete = cell_texte.paragraphs[0]
    initialiser_paragraphe_strict(p_en_tete)
    p_en_tete.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    r1 = p_en_tete.add_run("RÉPUBLIQUE ALGÉRIENNE DÉMOCRATIQUE ET POPULAIRE\n")
    r1.bold = True
    
    r2 = p_en_tete.add_run(
        "Ministère de l'Enseignement Supérieur et de la Recherche Scientifique\n"
        "Université Djillali Liabes - Sidi Bel Abbès\n"
        "Faculté de Génie Électrique\n"
    )
    
    r_dept = p_en_tete.add_run(f"{departement.upper()}")
    r_dept.bold = True
    
    for r in [r1, r2, r_dept]:
        r.font.size = Pt(11)
        r.font.name = 'Calibri'
    
    p_espace = doc.add_paragraph()
    initialiser_paragraphe_strict(p_espace)

# ==========================================
# GÉNÉRATEUR : JUSTIFICATION D'ABSENCE
# ==========================================
def generer_justificatif_iso(departement, donnees):
    doc = Document()
    appliquer_structure_pages_sans_ref(doc)
    
    grid_table = doc.add_table(rows=2, cols=3)
    grid_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    
    grid_table.autofit = False
    grid_table.allow_autofit = False
    
    dxa_widths = [int(1.19 * 1440), int(3.70 * 1440), int(1.40 * 1440)]
    inch_widths = [Inches(1.19), Inches(3.70), Inches(1.40)]
    
    tblPr = grid_table._tbl.tblPr
    tblGrid = OxmlElement('w:tblGrid')
    for width_dxa in dxa_widths:
        gridCol = OxmlElement('w:gridCol')
        gridCol.set(qn('w:w'), str(width_dxa))
        tblGrid.append(gridCol)
    grid_table._tbl.insert(1, tblGrid)

    for row in grid_table.rows:
        for idx, width_inch in enumerate(inch_widths):
            cell = row.cells[idx]
            cell.width = width_inch
            
            tcPr = cell._tc.get_or_add_tcPr()
            tcW = OxmlElement('w:tcW')
            tcW.set(qn('w:w'), str(dxa_widths[idx]))
            tcW.set(qn('w:type'), 'dxa')
            tcPr.append(tcW)

    cell_logo_haut = grid_table.cell(0, 0)
    cell_logo_bas = grid_table.cell(1, 0)
    
    cell_univ_haut = grid_table.cell(0, 1)
    cell_titre_bas = grid_table.cell(1, 1)
    
    cell_meta_haut = grid_table.cell(0, 2)
    cell_meta_bas = grid_table.cell(1, 2)
    
    # Application obligatoire des bordures complètes sur chaque cellule constitutive AVANT fusion
    for row in grid_table.rows:
        for cell in row.cells:
            set_cell_margins(cell, top=60, bottom=60, left=100, right=100)
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            appliquer_bordure_cellule_noire(cell)
            for p in cell.paragraphs:
                initialiser_paragraphe_strict(p)

    # Fusion physique des rectangles latéraux (moteur Word)
    cell_logo_haut.merge(cell_logo_bas)
    cell_meta_haut.merge(cell_meta_bas)
    
    # Ré-application des bordures après fusion pour écraser les masquages du layout de Word
    appliquer_bordure_cellule_noire(cell_logo_haut)
    appliquer_bordure_cellule_noire(cell_logo_bas)
    appliquer_bordure_cellule_noire(cell_meta_haut)
    appliquer_bordure_cellule_noire(cell_meta_bas)

    # Insertion du contenu - Logo
    p_logo = cell_logo_haut.paragraphs[0]
    p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
    nom_fichier_logo = "logo.PNG"
    if os.path.exists(nom_fichier_logo):
        p_logo.add_run().add_picture(nom_fichier_logo, width=Inches(0.58), height=Inches(0.94))
    else:
        r_alt = p_logo.add_run("[ LOGO ]")
        r_alt.font.name = 'Calibri'
        r_alt.font.size = Pt(11)
        r_alt.font.italic = True

    # Insertion du contenu - Université
    p_univ = cell_univ_haut.paragraphs[0]
    p_univ.alignment = WD_ALIGN_PARAGRAPH.CENTER
    re1 = p_univ.add_run("Université Djillali Liabes\n")
    re1.bold = True
    re2 = p_univ.add_run("Sidi Bel Abbes")
    for re in [re1, re2]:
        re.font.name = 'Calibri'
        re.font.size = Pt(11)

    # Insertion du contenu - Titre (ARIAL 11 STRICT GRAS)
    p_titre = cell_titre_bas.paragraphs[0]
    p_titre.alignment = WD_ALIGN_PARAGRAPH.CENTER
    rc = p_titre.add_run("JUSTIFICATION D’ABSENCE")
    rc.font.name = 'Arial'
    rc.font.size = Pt(11)
    rc.bold = True

    # Insertion du contenu - Métadonnées ISO
    p_meta = cell_meta_haut.paragraphs[0]
    p_meta.alignment = WD_ALIGN_PARAGRAPH.LEFT
    rm1 = p_meta.add_run("Code : PPER.06\n")
    rm2 = p_meta.add_run("Révision : 00\n")
    rm3 = p_meta.add_run("Date : 16/05/2026\n")
    rm4 = p_meta.add_run("Pages : 1/1")
    for rm in [rm1, rm2, rm3, rm4]:
        rm.font.name = 'Calibri'
        rm.font.size = Pt(11)

    p_esp1 = doc.add_paragraph()
    initialiser_paragraphe_strict(p_esp1)
    
    # Bloc structure académique
    p_fac = doc.add_paragraph()
    initialiser_paragraphe_strict(p_fac)
    rfac = p_fac.add_run("Faculté de génie Electrique\n")
    rfac.bold = True
    rdept_txt = p_fac.add_run(f"{departement}")
    for rf in [rfac, rdept_txt]:
        rf.font.name = 'Calibri'
        rf.font.size = Pt(11)
        
    p_esp2 = doc.add_paragraph()
    initialiser_paragraphe_strict(p_esp2)
    
    p_corps = doc.add_paragraph()
    initialiser_paragraphe_strict(p_corps)
    p_corps.alignment = WD_ALIGN_PARAGRAPH.LEFT
    r_corps = p_corps.add_run(f"Le {departement} atteste par la présente que l'étudiant(e) :")
    r_corps.font.name = 'Calibri'
    r_corps.font.size = Pt(11)
    
    p_esp3 = doc.add_paragraph()
    initialiser_paragraphe_strict(p_esp3)
    
    # Formulaire d'identification de l'étudiant absent
    p_id = doc.add_paragraph()
    initialiser_paragraphe_strict(p_id)
    
    r_nom_lbl = p_id.add_run("Nom et prénom : ")
    r_nom_lbl.bold = True
    r_nom_val = p_id.add_run(f"{donnees['nom_prenom']}\n")
    
    r_annee_lbl = p_id.add_run("Année d’étude : ")
    r_annee_lbl.bold = True
    r_annee_val = p_id.add_run(f"{donnees['annee_etude']}\n")
    
    r_spec_lbl = p_id.add_run("Spécialité : ")
    r_spec_lbl.bold = True
    r_spec_val = p_id.add_run(f"{donnees['specialite']}\n")
    
    r_abs_lbl = p_id.add_run("a été absent(e) durant la période allant du : ")
    r_abs_lbl.bold = True
    date_deb_txt = donnees['date_debut'].strftime('%d/%m/%Y')
    date_fin_txt = donnees['date_fin'].strftime('%d/%m/%Y')
    r_abs_val = p_id.add_run(f"{date_deb_txt} au {date_fin_txt}")
    
    for run in [r_nom_lbl, r_nom_val, r_annee_lbl, r_annee_val, r_spec_lbl, r_spec_val, r_abs_lbl, r_abs_val]:
        run.font.name = 'Calibri'
        run.font.size = Pt(11)
        
    p_esp4 = doc.add_paragraph()
    initialiser_paragraphe_strict(p_esp4)
    
    # Grille des motifs réglementaires
    p_motif_titre = doc.add_paragraph()
    initialiser_paragraphe_strict(p_motif_titre)
    r_mot_titre = p_motif_titre.add_run("Pour le motif suivant :")
    r_mot_titre.bold = True
    r_mot_titre.font.name = 'Calibri'
    r_mot_titre.font.size = Pt(11)
    
    for motif in MOTIFS_ABSENCE:
        p_m = doc.add_paragraph()
        initialiser_paragraphe_strict(p_m)
        p_m.paragraph_format.left_indent = Inches(0.4)
        if motif == donnees['motif_selectionne']:
            r_box = p_m.add_run("[ X ]  ")
            r_box.bold = True
        else:
            r_box = p_m.add_run("[   ]  ")
        r_txt = p_m.add_run(motif)
        
        r_box.font.name = 'Calibri'
        r_box.font.size = Pt(11)
        r_txt.font.name = 'Calibri'
        r_txt.font.size = Pt(11)
        
    p_esp5 = doc.add_paragraph()
    initialiser_paragraphe_strict(p_esp5)
    
    # Clause finale
    p_cloture = doc.add_paragraph()
    initialiser_paragraphe_strict(p_cloture)
    r_cloture = p_cloture.add_run("La présente attestation est délivrée à l’intéressé(e) pour servir et valoir ce que de droit.")
    r_cloture.font.name = 'Calibri'
    r_cloture.font.size = Pt(11)
    r_cloture.font.italic = True
    
    p_esp6 = doc.add_paragraph()
    initialiser_paragraphe_strict(p_esp6)
    
    # Signature
    p_sig = doc.add_paragraph()
    initialiser_paragraphe_strict(p_sig)
    p_sig.alignment = WD_ALIGN_PARAGRAPH.LEFT
    date_edit_txt = donnees['date_edition'].strftime('%d/%m/%Y')
    run_sig = p_sig.add_run(f"Fait à : Sidi Bel Abbès.\t\tLe : {date_edit_txt}\n\n\t\t\t\t\t\tLe Chef de Département")
    run_sig.font.name = 'Calibri'
    run_sig.font.size = Pt(11)
    run_sig.bold = True
    
    return doc

# ==========================================
# GÉNÉRATEUR : BORDEREAU D'ENVOI
# ==========================================
def generer_bordereau_iso(departement, donnees):
    doc = Document()
    appliquer_structure_pages_sans_ref(doc)
    inserer_bloc_en_tete_bordereau(doc, departement)

    p_ref = doc.add_paragraph()
    initialiser_paragraphe_strict(p_ref)
    p_ref.alignment = WD_ALIGN_PARAGRAPH.LEFT
    r_ref = p_ref.add_run(f"N° : {donnees['num_reference']}/ F.G.E/ V.D.E.Q.L.E/2026")
    r_ref.font.size = Pt(11)
    r_ref.font.name = 'Calibri'
    r_ref.bold = True

    p_esp1 = doc.add_paragraph()
    initialiser_paragraphe_strict(p_esp1)

    p_titre = doc.add_paragraph()
    initialiser_paragraphe_strict(p_titre)
    p_titre.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_titre = p_titre.add_run("BORDEREAU D’ENVOI")
    r_titre.font.name = 'Calibri'
    r_titre.font.size = Pt(11)
    r_titre.underline = True
    r_titre.bold = True
    
    p_esp2 = doc.add_paragraph()
    initialiser_paragraphe_strict(p_esp2)

    p_dest = doc.add_paragraph()
    initialiser_paragraphe_strict(p_dest)
    p_dest.alignment = WD_ALIGN_PARAGRAPH.LEFT
    r_dest = p_dest.add_run(f"A monsieur : {donnees['destinataire']}")
    r_dest.bold = True
    r_dest.font.size = Pt(11)
    r_dest.font.name = 'Calibri'

    p_esp3 = doc.add_paragraph()
    initialiser_paragraphe_strict(p_esp3)

    liste_pieces = donnees['liste_pieces']
    nb_lignes_totatles = 2 + len(liste_pieces)
    
    table = doc.add_table(rows=nb_lignes_totatles, cols=3)
    table.style = 'Table Grid'
    table.columns[0].width = Inches(4.5)
    table.columns[1].width = Inches(0.8)
    table.columns[2].width = Inches(1.7)

    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = "Désignation des pièces"
    hdr_cells[1].text = "Nbre"
    hdr_cells[2].text = "Observations"
    
    for cell in hdr_cells:
        p_hdr = cell.paragraphs[0]
        initialiser_paragraphe_strict(p_hdr)
        p_hdr.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_hdr.runs[0].font.bold = True
        p_hdr.runs[0].font.name = 'Calibri'
        p_hdr.runs[0].font.size = Pt(11)
        set_cell_margins(cell, top=60, bottom=60)

    row_joint = table.rows[1].cells
    row_joint[0].text = "Veuillez trouver ci-joint :"
    p_j = row_joint[0].paragraphs[0]
    initialiser_paragraphe_strict(p_j)
    p_j.runs[0].font.italic = True
    p_j.runs[0].font.name = 'Calibri'
    p_j.runs[0].font.size = Pt(11)
    set_cell_margins(row_joint[0], top=60, bottom=60)

    for index, piece in enumerate(liste_pieces):
        row_idx = 2 + index
        current_row = table.rows[row_idx].cells
        current_row[0].text = str(piece["Désignation des pièces"])
        current_row[1].text = str(piece["Nbre"])
        current_row[2].text = str(piece["Observations"])
        
        for i, cell in enumerate(current_row):
            p_c = cell.paragraphs[0]
            initialiser_paragraphe_strict(p_c)
            set_cell_margins(cell, top=60, bottom=60)
            if len(p_c.runs) > 0:
                p_c.runs[0].font.name = 'Calibri'
                p_c.runs[0].font.size = Pt(11)
            if i == 1:
                p_c.alignment = WD_ALIGN_PARAGRAPH.CENTER

    p_esp4 = doc.add_paragraph()
    initialiser_paragraphe_strict(p_esp4)

    p_signatures = doc.add_paragraph()
    initialiser_paragraphe_strict(p_signatures)
    p_signatures.alignment = WD_ALIGN_PARAGRAPH.LEFT
    date_texte = donnees['date_creation'].strftime('%d/%m/%Y')
    run_sig = p_signatures.add_run(f"Chef de département\t\t\t\tSidi bel abbés le : {date_texte}")
    run_sig.font.name = 'Calibri'
    run_sig.font.size = Pt(11)
    run_sig.bold = True

    p_esp5 = doc.add_paragraph()
    initialiser_paragraphe_strict(p_esp5)

    p_accuse = doc.add_paragraph()
    initialiser_paragraphe_strict(p_accuse)
    p_accuse.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run_accuse = p_accuse.add_run("Accusé de réception    ")
    run_accuse.font.name = 'Calibri'
    run_accuse.font.size = Pt(11)
    run_accuse.font.underline = True
    run_accuse.bold = True

    return doc

def generer_pv_generique(departement, type_pv, donnees):
    """Générateur secondaire de secours (Calibri 11)."""
    doc = Document()
    p = doc.add_paragraph()
    initialiser_paragraphe_strict(p)
    run = p.add_run(f"{type_pv} - {departement}\nDocument en cours.")
    run.font.name = 'Calibri'
    run.font.size = Pt(11)
    return doc

# ==========================================
# INTERFACE UTILISATEUR STREAMLIT
# ==========================================
st.set_page_config(page_title="Générateur ISO Multi-Documents", layout="wide")

st.caption(TITRE_PLATEFORME)
st.title("Gestion Administrative - Générateurs de documents")

col_dept, col_doc = st.columns(2)
with col_dept:
    dept_choisi = st.selectbox("Département émetteur :", DEPARTEMENTS)
with col_doc:
    doc_choisi = st.selectbox("Nature du document à générer :", TYPES_DOCUMENTS, index=1)

st.divider()
st.subheader(f"Formulaire d'édition - {doc_choisi}")

donnees_doc = {}

# --- FORMULAIRE : BORDEREAU D'ENVOI ---
if doc_choisi == "Bordereau d'envoi":
    col_ref, col_date = st.columns(2)
    with col_ref:
        donnees_doc['num_reference'] = st.text_input("Référence séquentielle (Ex: 27)", value="27")
    with col_date:
        donnees_doc['date_creation'] = st.date_input("Date d'édition", datetime.now())
        
    st.markdown("##### Destinataire officiel")
    choix_dest = st.selectbox("Sélectionnez le destinataire dans la liste :", OPTIONS_DESTINATAIRES, index=0)
    
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

# --- FORMULAIRE : JUSTIFICATION D'ABSENCE ---
elif doc_choisi == "Justification d'absence":
    col_nom, col_annee = st.columns(2)
    with col_nom:
        donnees_doc['nom_prenom'] = st.text_input("Nom et prénom de l'étudiant(e) :", value="Benali Mohamed")
    with col_annee:
        donnees_doc['annee_etude'] = st.selectbox(
            "Année d'étude (Ex: 1ère Année Master) :", 
            LISTE_ANNEES_ETUDE, 
            index=1
        )
        
    col_spec, col_motif = st.columns(2)
    with col_spec:
        donnees_doc['specialite'] = st.selectbox(
            "Spécialité / Option :", 
            LISTE_SPECIALITES, 
            index=0
        )
    with col_motif:
        donnees_doc['motif_selectionne'] = st.selectbox("Motif réglementaire retenu :", MOTIFS_ABSENCE, index=0)
        
    col_d1, col_d2, col_d3 = st.columns(3)
    with col_d1:
        donnees_doc['date_debut'] = st.date_input("Date de début de l'absence", datetime.now())
    with col_d2:
        donnees_doc['date_fin'] = st.date_input("Date de fin de l'absence", datetime.now())
    with col_d3:
        donnees_doc['date_edition'] = st.date_input("Date de délivrance", datetime.now())

# --- FORMULAIRE : PAR DÉFAUT (PVs) ---
else:
    with st.form("form_autres"):
        donnees_doc['date_creation'] = st.date_input("Date", datetime.now())
        donnees_doc['contenu'] = st.text_area("Contenu textuel")
        st.form_submit_button("Valider la saisie")

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# GESTION DES ACTIONS FINALES
# ==========================================
if doc_choisi == "Bordereau d'envoi":
    if st.button("Compiler et Générer le Bordereau Officiel"):
        if not donnees_doc['destinataire'].strip():
            st.error("Erreur : Le champ de destination personnalisée ne peut pas être vide.")
        else:
            try:
                document_final = generer_bordereau_iso(dept_choisi, donnees_doc)
                output_stream = io.BytesIO()
                document_final.save(output_stream)
                output_stream.seek(0)
                
                st.success("✓ Bordereau d'envoi généré avec succès.")
                st.download_button(
                    label="⬇️ Télécharger le Bordereau d'envoi (.docx)",
                    data=output_stream,
                    file_name=f"Bordereau_{dept_choisi.replace(' ', '_')}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
            except Exception as error:
                st.error(f"Échec de l'opération de génération : {str(error)}")

elif doc_choisi == "Justification d'absence":
    if st.button("Compiler et Générer la Justification d'Absence"):
        if not donnees_doc['nom_prenom'].strip():
            st.error("Erreur : Le nom de l'étudiant ne peut pas être vide.")
        else:
            try:
                document_final = generer_justificatif_iso(dept_choisi, donnees_doc)
                output_stream = io.BytesIO()
                document_final.save(output_stream)
                output_stream.seek(0)
                
                st.success("✓ Justification d'absence générée avec succès (Quadrillage complet des rectangles & Pagination à l'extrémité droite).")
                st.download_button(
                    label="⬇️ Télécharger le justificatif (.docx)",
                    data=output_stream,
                    file_name=f"Justification_Absence_{donnees_doc['nom_prenom'].replace(' ', '_')}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
            except Exception as error:
                st.error(f"Échec de l'opération de génération : {str(error)}")
