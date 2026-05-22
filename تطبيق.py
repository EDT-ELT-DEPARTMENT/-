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
    """Applique une bordure fine noire standard autour d'une cellule."""
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
    """Configure les marges globales et la pagination épurée à droite dans le pied de page."""
    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)
        
        section.different_first_page_header_footer = False
        
        footer = section.footer
        footer_p = footer.paragraphs[0]
        initialiser_paragraphe_strict(footer_p)
        footer_p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        
        footer_pPr = footer_p._p.get_or_add_pPr()
        tabs = OxmlElement('w:tabs')
        
        tab_droite = OxmlElement('w:tab')
        tab_droite.set(qn('w:val'), 'right')
        tab_droite.set(qn('w:pos'), '9936')
        tabs.append(tab_droite)
        footer_pPr.append(tabs)
        
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

def inserer_bloc_en_tete_bordereau(doc, departement):
    """Génère l'en-tête standard classique avec logo pour le Bordereau d'envoi."""
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

    p_logo = cell_logo.paragraphs[0]
    initialiser_paragraphe_strict(p_logo)
    p_logo.alignment = WD_ALIGN_PARAGRAPH.LEFT
    
    nom_fichier_logo = "logo.PNG"
    if os.path.exists(nom_fichier_logo):
        p_logo.add_run().add_picture(nom_fichier_logo, width=Inches(0.833))
    else:
        r_alt = p_logo.add_run("[LOGO UNIVERSITÉ]")
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
    
    # Grille à 2 lignes et 3 colonnes pour supprimer la ligne inférieure vide
    grid_table = doc.add_table(rows=2, cols=3)
    grid_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    grid_table.autofit = False
    
    widths = [Inches(1.5), Inches(3.7), Inches(1.8)]
    for row in grid_table.rows:
        for i, w in enumerate(widths):
            row.cells[i].width = w

    cell_logo_haut = grid_table.cell(0, 0)
    cell_logo_bas = grid_table.cell(1, 0)
    
    cell_univ_haut = grid_table.cell(0, 1)
    cell_titre_bas = grid_table.cell(1, 1)
    
    cell_meta_haut = grid_table.cell(0, 2)
    cell_meta_bas = grid_table.cell(1, 2)
    
    # 1. Bloc Gauche : Fusion verticale de la colonne du Logo (Lignes 0 et 1)
    cell_logo_haut.merge(cell_logo_bas)
    
    # 2. Bloc Droit : Fusion verticale de la colonne des Métadonnées (Lignes 0 et 1)
    cell_meta_haut.merge(cell_meta_bas)
    
    # Configuration stricte de chaque cellule : pas d'espace entre lignes, police 11 Calibri
    for row in grid_table.rows:
        for cell in row.cells:
            set_cell_margins(cell, top=60, bottom=60, left=100, right=100)
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            appliquer_bordure_cellule_noire(cell)
            for p in cell.paragraphs:
                initialiser_paragraphe_strict(p)

    # Insertion du contenu - Cellule Logo
    p_logo = cell_logo_haut.paragraphs[0]
    p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
    nom_fichier_logo = "logo.PNG"
    if os.path.exists(nom_fichier_logo):
        p_logo.add_run().add_picture(nom_fichier_logo, width=Inches(0.85))
    else:
        r_alt = p_logo.add_run("[ LOGO ]")
        r_alt.font.name = 'Calibri'
        r_alt.font.size = Pt(11)
        r_alt.font.italic = True

    # Insertion du contenu - Université (Cellule centrale supérieure)
    p_univ = cell_univ_haut.paragraphs[0]
    p_univ.alignment = WD_ALIGN_PARAGRAPH.CENTER
    re1 = p_univ.add_run("Université Djillali Liabes\n")
    re1.bold = True
    re2 = p_univ.add_run("Sidi Bel Abbes")
    for re in [re1, re2]:
        re.font.name = 'Calibri'
        re.font.size = Pt(11)

    # Insertion du contenu - Titre (Cellule centrale inférieure fractionnée sans ligne en dessous)
    p_titre = cell_titre_bas.paragraphs[0]
    p_titre.alignment = WD_ALIGN_PARAGRAPH.CENTER
    rc = p_titre.add_run("JUSTIFICATION D’ABSENCE")
    rc.font.name = 'Calibri'
    rc.font.size = Pt(11)
    rc.bold = True

    # Insertion du contenu - Métadonnées ISO (Cellule droite)
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
    
    p_cloture = doc.add_paragraph()
    initialiser_paragraphe_strict(p_cloture)
    r_cloture = p_cloture.add_run("La présente attestation est délivrée à l’intéressé(e) pour servir et valoir ce que de droit.")
    r_cloture.font.name = 'Calibri'
    r_cloture.font.size = Pt(11)
    r_cloture.font.italic = True
    
    p_esp6 = doc.add_paragraph()
    initialiser_paragraphe_strict(p_esp6)
    
    # Bloc visa / signature de l'autorité
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
    r_ref = p_ref.add_run(f"N° : {donnees
