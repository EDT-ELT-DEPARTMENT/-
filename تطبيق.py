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

def appliquer_structure_pages_sans_ref(doc):
    """Configure les marges globales et le pied de page strict (SANS référence fixe, Page à droite)."""
    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)
        
        section.different_first_page_header_footer = False
        
        footer = section.footer
        footer_p = footer.paragraphs[0]
        footer_p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        
        footer_pPr = footer_p._p.get_or_add_pPr()
        tabs = OxmlElement('w:tabs')
        
        # Un unique taquet à l'extrême droite pour les numéros de page (9936 dxa = ~6.9 pouces)
        tab_droite = OxmlElement('w:tab')
        tab_droite.set(qn('w:val'), 'right')
        tab_droite.set(qn('w:pos'), '9936')
        tabs.append(tab_droite)
        footer_pPr.append(tabs)
        
        # Saut par tabulation vers l'extrême droite pour insérer la pagination
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
    p_logo.alignment = WD_ALIGN_PARAGRAPH.LEFT
    
    nom_fichier_logo = "logo.PNG"
    if os.path.exists(nom_fichier_logo):
        p_logo.add_run().add_picture(nom_fichier_logo, width=Inches(0.833))
    else:
        r_alt = p_logo.add_run("[LOGO UNIVERSITÉ]")
        r_alt.font.name = 'Calibri'
        r_alt.font.size = Pt(8)
        r_alt.font.italic = True

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

# ==========================================
# GÉNÉRATEUR : JUSTIFICATION D'ABSENCE
# ==========================================
def generer_justificatif_iso(departement, donnees):
    doc = Document()
    appliquer_structure_pages_sans_ref(doc)
    
    # Création d'une grille matricielle rigide à 3 lignes pour éviter l'erreur de rectangle
    grid_table = doc.add_table(rows=3, cols=3)
    grid_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    grid_table.autofit = False
    
    # Largeurs des colonnes fixes (Somme = 6.9 pouces)
    widths = [Inches(1.3), Inches(3.9), Inches(1.7)]
    for row in grid_table.rows:
        for i, w in enumerate(widths):
            row.cells[i].width = w

    # Fusion des cellules de la ligne inférieure pour le titre cartouché
    cell_titre_bas = grid_table.cell(2, 0)
    cell_titre_bas.merge(grid_table.cell(2, 1)).merge(grid_table.cell(2, 2))
    
    # Fusion verticale de la colonne du logo (Lignes 0 et 1)
    cell_logo = grid_table.cell(0, 0)
    cell_logo.merge(grid_table.cell(1, 0))
    
    # Fusion des blocs centraux et droits pour assurer une géométrie rectangulaire parfaite
    cell_etab = grid_table.cell(0, 1)
    cell_etab.merge(grid_table.cell(1, 1))
    
    cell_meta = grid_table.cell(0, 2)
    cell_meta.merge(grid_table.cell(1, 2))
    
    # Application des paddings et des contours noirs
    for row in grid_table.rows:
        for cell in row.cells:
            set_cell_margins(cell, top=110, bottom=110, left=120, right=120)
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            appliquer_bordure_cellule_noire(cell)

    # Insertion du contenu - Logo
    p_logo = cell_logo.paragraphs[0]
    p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
    nom_fichier_logo = "logo.PNG"
    if os.path.exists(nom_fichier_logo):
        p_logo.add_run().add_picture(nom_fichier_logo, width=Inches(0.85))
    else:
        r_alt = p_logo.add_run("[ LOGO ]")
        r_alt.font.name = 'Calibri'
        r_alt.font.size = Pt(9)
        r_alt.font.italic = True

    # Insertion du contenu - Établissement
    p_etab = cell_etab.paragraphs[0]
    p_etab.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    re1 = p_etab.add_run("Université Djillali Liabes\n")
    re1.bold = True
    re1.font.name = 'Calibri'
    re1.font.size = Pt(13)
    
    re2 = p_etab.add_run("Sidi Bel Abbes")
    re2.font.name = 'Calibri'
    re2.font.size = Pt(11)

    # Insertion du contenu - Métadonnées Qualité
    p_meta = cell_meta.paragraphs[0]
    p_meta.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_meta.paragraph_format.space_after = Pt(1)
    
    rm1 = p
