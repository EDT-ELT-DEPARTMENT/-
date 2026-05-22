import streamlit as st
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn, nsdecls
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
        
        # Saut vers l'extrême droite pour insérer la pagination
        footer_p.add
