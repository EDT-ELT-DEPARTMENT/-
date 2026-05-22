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
    "Réseaux électriques",
    "Energies renouvelables",
    "Commandes électriques",
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

NOM_FICHIER_EXCEL = "dataEDT-ELT-S2-2026.xlsx"

# ==========================================
# CHARGEMENT ET TRAITEMENT DU FICHIER SOURCE EXCEL
# ==========================================
@st.cache_data
def charger_base_enseignements(chemin_fichier):
    """
    Charge le fichier Excel source et structure un dictionnaire indexé par Enseignant.
    La disposition attendue est : Enseignements, Code, Enseignants, Horaire, Jours, Lieu, Promotion.
    """
    dict_enseignants = {}
    if os.path.exists(chemin_fichier):
        try:
            df = pd.read_excel(chemin_fichier)
            df.columns = [col.strip() for col in df.columns]
            
            if "Enseignants" in df.columns and "Enseignements" in df.columns and "Code" in df.columns:
                for _, row in df.iterrows():
                    nom_ens = str(row["Enseignants"]).strip()
                    matiere_nom = str(row["Enseignements"]).strip()
                    code_matiere = str(row["Code"]).strip()
                    
                    if nom_ens and nom_ens != "nan" and matiere_nom and matiere_nom != "nan":
                        libelle_matiere = f"{matiere_nom} ({code_matiere})"
                        
                        if nom_ens not in dict_enseignants:
                            dict_enseignants[nom_ens] = []
                        if libelle_matiere not in dict_enseignants[nom_ens]:
                            dict_enseignants[nom_ens].append(libelle_matiere)
            else:
                st.error("Format critique absent : Les colonnes 'Enseignants', 'Enseignements' ou 'Code' manquent dans le fichier Excel.")
        except Exception as e:
            st.error(f"Erreur lors de la lecture du fichier Excel source : {str(e)}")
            
    if not dict_enseignants:
        dict_enseignants = {
            "Zidi": ["Stabilité et dynamique des réseaux électriques (Cours-SDRE-RE)"],
            "Bermaki": ["Éclairage LED: Principes et applications (Cours-LEDPA-RE)"],
            "Touhami": ["Techniques d'intelligence artificielle (Cours-TIA-RE)"],
            "BENHAMIDA": ["Intégration des ressources renouvelables aux réseaux électriques (Cours-IRRRE-RE)"],
            "Rezoug": ["Dimensionnement des Réseaux électriques industriels (Cours-DREI-RE)"],
            "Bellebna": ["Technique de la haute tension (Cours-THT-RE)"],
            "Benhamida": ["Conduite des réseaux électriques (Cours-CdRE-RE)"],
            "Maamar": ["Réseaux électriques intelligents (Cours-REI-RE)"]
        }
    return dict_enseignants

DATA_ENSEIGNANTS = charger_base_enseignements(NOM_FICHIER_EXCEL)

# ==========================================
# INITIALISATION DU SUIVI ET HISTORIQUE (SESSION STATE)
# ==========================================
if "historique_justifications" not in st.session_state:
    st.session_state["historique_justifications"] = []

if "compteur_absences" not in st.session_state:
    st.session_state["compteur_absences"] = {}

# Dictionnaire pour mémoriser les dernières métadonnées de l'absence par étudiant
if "metadonnees_absences" not in st.session_state:
    st.session_state["metadonnees_absences"] = {}

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
    
    for row in grid_table.rows:
        for cell in row.cells:
            set_cell_margins(cell, top=60, bottom=60, left=100, right=100)
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            appliquer_bordure_cellule_noire(cell)
            for p in cell.paragraphs:
                initialiser_paragraphe_strict(p)

    cell_logo_haut.merge(cell_logo_bas)
    cell_meta_haut.merge(cell_meta_bas)
    
    appliquer_bordure_cellule_noire(cell_logo_haut)
    appliquer_bordure_cellule_noire(cell_logo_bas)
    appliquer_bordure_cellule_noire(cell_meta_haut)
    appliquer_bordure_cellule_noire(cell_meta_bas)

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

    p_univ = cell_univ_haut.paragraphs[0]
    p_univ.alignment = WD_ALIGN_PARAGRAPH.CENTER
    re1 = p_univ.add_run("Université Djillali Liabes\n")
    re1.bold = True
    re2 = p_univ.add_run("Sidi Bel Abbes")
    for re in [re1, re2]:
        re.font.name = 'Calibri'
        re.font.size = Pt(11)

    p_titre = cell_titre_bas.paragraphs[0]
    p_titre.alignment = WD_ALIGN_PARAGRAPH.CENTER
    rc = p_titre.add_run("JUSTIFICATION D’ABSENCE")
    rc.font.name = 'Arial'
    rc.font.size = Pt(11)
    rc.bold = True

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
    
    r_ens_lbl = p_id.add_run("Enseignant concerné : ")
    r_ens_lbl.bold = True
    r_ens_val = p_id.add_run(f"Pr. {donnees['enseignant']}\n")
    
    r_mat_lbl = p_id.add_run("Matière / Enseignement : ")
    r_mat_lbl.bold = True
    r_mat_val = p_id.add_run(f"{donnees['matiere']}\n")
    
    r_abs_lbl = p_id.add_run("a été absent(e) durant la période allant du : ")
    r_abs_lbl.bold = True
    date_deb_txt = donnees['date_debut'].strftime('%d/%m/%Y')
    date_fin_txt = donnees['date_fin'].strftime('%d/%m/%Y')
    r_abs_val = p_id.add_run(f"{date_deb_txt} au {date_fin_txt}")
    
    for run in [r_nom_lbl, r_nom_val, r_annee_lbl, r_annee_val, r_spec_lbl, r_spec_val, r_ens_lbl, r_ens_val, r_mat_lbl, r_mat_val, r_abs_lbl, r_abs_val]:
        run.font.name = 'Calibri'
        run.font.size = Pt(11)
        
    p_esp4 = doc.add_paragraph()
    initialiser_paragraphe_strict(p_esp4)
    
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
    
    p_cloture = doc.add_paragraph()
    initialiser_paragraphe_strict(p_cloture)
    r_cloture = p_cloture.add_run("La présente attestation est délivrée à l’intéressé(e) pour servir et valoir ce que de droit.")
    r_cloture.font.name = 'Calibri'
    r_cloture.font.size = Pt(11)
    r_cloture.font.italic = True
    
    p_esp6 = doc.add_paragraph()
    initialiser_paragraphe_strict(p_esp6)
    
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

tab_formulaire, tab_historique = st.tabs(["📝 Édition du Document", "📊 Historique & Compteur d'Exclusions"])

with tab_formulaire:
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
            
        st.markdown("##### Information Complémentaires (Enseignant & Enseignement)")
        col_ens, col_mat = st.columns(2)
        
        with col_ens:
            liste_nom_enseignants = sorted(list(DATA_ENSEIGNANTS.keys()))
            index_par_defaut = liste_nom_enseignants.index("Bellebna") if "Bellebna" in liste_nom_enseignants else 0
            enseignant_choisi = st.selectbox("Enseignant ayant déclaré l'absence :", liste_nom_enseignants, index=index_par_defaut)
            donnees_doc['enseignant'] = enseignant_choisi
            
        with col_mat:
            liste_matieres_disponibles = sorted(DATA_ENSEIGNANTS[enseignant_choisi])
            matiere_choisie = st.selectbox("Matière concernée :", liste_matieres_disponibles)
            donnees_doc['matiere'] = matiere_choisie

        col_d1, col_d2, col_d3 = st.columns(3)
        with col_d1:
            donnees_doc['date_debut'] = st.date_input("Date de début de l'absence", datetime.now())
        with col_d2:
            donnees_doc['date_fin'] = st.date_input("Date de fin de l'absence", datetime.now())
        with col_d3:
            donnees_doc['date_edition'] = st.date_input("Date de délivrance", datetime.now())

        nom_etudiant_clean = donnees_doc['nom_prenom'].strip()
        if nom_etudiant_clean:
            nb_absences_actuelles = st.session_state["compteur_absences"].get(nom_etudiant_clean, 0)
            if nb_absences_actuelles >= 5:
                st.error(f"⚠️ ATTENTION CRITIQUE : L'étudiant '{nom_etudiant_clean}' compte déjà {nb_absences_actuelles} absences justifiées. Il est déclaré EXCLU.")
            elif nb_absences_actuelles > 0:
                st.warning(f"Note : Cet étudiant possède actuellement {nb_absences_actuelles} absence(s) enregistrée(s).")

    else:
        with st.form("form_autres"):
            donnees_doc['date_creation'] = st.date_input("Date", datetime.now())
            donnees_doc['contenu'] = st.text_area("Contenu textuel")
            st.form_submit_button("Valider la saisie")

    st.markdown("<br>", unsafe_allow_html=True)

    # ==========================================
    # GESTION DES ACTIONS FINALES & COMPILATION
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
                    nom_etudiant = donnees_doc['nom_prenom'].strip()
                    
                    document_final = generer_justificatif_iso(dept_choisi, donnees_doc)
                    output_stream = io.BytesIO()
                    document_final.save(output_stream)
                    output_stream.seek(0)
                    
                    # Incrémentation du compteur global
                    st.session_state["compteur_absences"][nom_etudiant] = st.session_state["compteur_absences"].get(nom_etudiant, 0) + 1
                    total_absences = st.session_state["compteur_absences"][nom_etudiant]
                    
                    # Sauvegarde des métadonnées contextuelles de la dernière absence pour l'export des exclus
                    st.session_state["metadonnees_absences"][nom_etudiant] = {
                        "date_absence": donnees_doc['date_debut'].strftime('%d/%m/%Y'),
                        "date_delivrance": donnees_doc['date_edition'].strftime('%d/%m/%Y'),
                        "enseignant": donnees_doc['enseignant'],
                        "matiere": donnees_doc['matiere']
                    }
                    
                    # Insertion dans l'historique global de session
                    enregistrement_historique = {
                        "Date Opération": datetime.now().strftime("%d/%m/%Y %H:%M"),
                        "Étudiant": nom_etudiant,
                        "Année d'étude": donnees_doc['annee_etude'],
                        "Spécialité": donnees_doc['specialite'],
                        "Enseignant": donnees_doc['enseignant'],
                        "Matière": donnees_doc['matiere'],
                        "Motif": donnees_doc['motif_selectionne'],
                        "Total Absences Cumulées": total_absences,
                        "Statut": "EXCLU" if total_absences >= 5 else "Actif"
                    }
                    st.session_state["historique_justifications"].append(enregistrement_historique)
                    
                    st.success(f"✓ Justification validée (Absence n°{total_absences} enregistrée).")
                    
                    if total_absences >= 5:
                        st.error(f"🚨 Seuil critique atteint ou dépassé ! L'étudiant {nom_etudiant} est déclaré EXCLU.")
                        
                    st.download_button(
                        label="⬇️ Télécharger le justificatif (.docx)",
                        data=output_stream,
                        file_name=f"Justification_Absence_{nom_etudiant.replace(' ', '_')}.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
                except Exception as error:
                    st.error(f"Échec de l'opération de génération : {str(error)}")

with tab_historique:
    st.subheader("📋 Historique Global des Étudiants Justifiés")
    
    if len(st.session_state["historique_justifications"]) == 0:
        st.info("Aucune justification d'absence n'a encore été enregistrée lors de cette session.")
    else:
        df_historique = pd.DataFrame(st.session_state["historique_justifications"])
        st.dataframe(df_historique, use_container_width=True)
        
        st.divider()
        st.subheader("🚨 Tableau de suivi des Seuils d'Exclusion (>= 5 Absences)")
        
        donnees_compteur = []
        donnees_exclus_uniquement = []
        
        for etudiant, nb_abs in st.session_state["compteur_absences"].items():
            meta = st.session_state["metadonnees_absences"].get(etudiant, {"date_absence": "N/A", "date_delivrance": "N/A", "enseignant": "N/A", "matiere": "N/A"})
            
            situation = "❌ EXCLU DE LA MATIÈRE" if nb_abs >= 5 else "✅ En règle"
            
            ligne_complete = {
                "Nom & Prénom Étudiant": etudiant,
                "Date de l'absence": meta["date_absence"],
                "Date de délivrance": meta["date_delivrance"],
                "Enseignant": meta["enseignant"],
                "Matière": meta["matiere"],
                "Nombre d'absences comptabilisées": nb_abs,
                "Situation Réglementaire": situation
            }
            donnees_compteur.append(ligne_complete)
            
            # Filtrage pour la liste dédiée des exclus
            if nb_abs >= 5:
                donnees_exclus_uniquement.append(ligne_complete)
            
        df_compteur = pd.DataFrame(donnees_compteur)
        df_exclus = pd.DataFrame(donnees_exclus_uniquement)
        
        def styliser_tableau(val):
            color = 'background-color: #ffcccc; color: #cc0000; font-weight: bold;' if "EXCLU" in str(val) else ''
            return color
            
        st.dataframe(df_compteur.style.map(styliser_tableau, subset=["Situation Réglementaire"]), use_container_width=True)
        
        # --- SECTION EXPORTATION DES ETUDIANTS EXCLUS ---
        st.markdown("### 💾 Extraction et Téléchargement de la Liste des Exclus")
        
        if df_exclus.empty:
            st.info("Aucun étudiant n'a atteint le seuil d'exclusion (5 absences) pour le moment. Les fonctions d'exports s'activeront dès l'apparition d'un cas d'exclusion.")
        else:
            st.warning(f"Total détecté : {len(df_exclus)} étudiant(s) sous le coup d'une mesure d'exclusion réglementaire.")
            
            col_btn_excel, col_btn_html = st.columns(2)
            
            # Génération du flux Excel en mémoire
            with col_btn_excel:
                buffer_excel = io.BytesIO()
                with pd.ExcelWriter(buffer_excel, engine='openpyxl') as writer:
                    df_exclus.to_excel(writer, index=False, sheet_name='Liste_des_Exclus')
                buffer_excel.seek(0)
                
                st.download_button(
                    label="📥 Télécharger la Liste des Exclus en format Excel (.xlsx)",
                    data=buffer_excel,
                    file_name=f"Liste_Etudiants_Exclus_{datetime.now().strftime('%d_%m_%Y')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
                
            # Génération du fichier HTML stylisé en mémoire
            with col_btn_html:
                html_style = """
                <style>
                    table { border-collapse: collapse; width: 100%; font-family: 'Calibri', sans-serif; margin-top: 20px; }
                    th { background-color: #cc0000; color: white; padding: 10px; text-align: left; border: 1px solid #333; }
                    td { padding: 8px; border: 1px solid #666; }
                    tr:nth-child(even) { background-color: #f2f2f2; }
                    .title { font-family: 'Arial', sans-serif; color: #333; font-size: 18px; font-weight: bold; text-align: center; margin-bottom: 5px; }
                    .subtitle { font-family: 'Calibri', sans-serif; color: #555; text-align: center; font-size: 13px; margin-bottom: 25px; }
                    .badge-exclu { color: #cc0000; font-weight: bold; background-color: #ffcccc; padding: 4px; border-radius: 3px; }
                </style>
                """
                
                html_titre_bloc = f'<div class="title">RÉPUBLIQUE ALGÉRIENNE DÉMOCRATIQUE ET POPULAIRE</div>'
                html_titre_bloc += f'<div class="subtitle">{TITRE_PLATEFORME}<br>LISTE OFFICIELLE DES ÉTUDIANTS EXCLUS - SEMESTRE 2</div>'
                
                # Conversion du dataframe en table HTML brute puis injection des classes de style
                html_table_brute = df_exclus.to_html(index=False)
                html_table_brute = html_table_brute.replace('❌ EXCLU DE LA MATIÈRE', '<span class="badge-exclu">❌ EXCLU DE LA MATIÈRE</span>')
                
                html_document_complet = f"<html><head><meta charset='utf-8'>{html_style}</head><body>{html_titre_bloc}{html_table_brute}</body></html>"
                
                st.download_button(
                    label="🌐 Télécharger la Liste des Exclus en format HTML (.html)",
                    data=html_document_complet,
                    file_name=f"Liste_Etudiants_Exclus_{datetime.now().strftime('%d_%m_%Y')}.html",
                    mime="text/html",
                    use_container_width=True
                )
