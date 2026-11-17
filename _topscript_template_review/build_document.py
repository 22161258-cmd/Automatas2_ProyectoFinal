from pathlib import Path
from hashlib import sha256
import re
from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.shared import Inches, Pt, RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

root=Path(r'C:\Automatas')
source=Path(r'C:\Users\vicma\Downloads\video wong sistemas embebidos\Proyecto Integrador - Fase 1.docx')
expected='89e36ae25ed7d4b5bad21e4f4a211ce82379876129e4c3d9c2ccb4b415e6ba8a'
actual=sha256(source.read_bytes()).hexdigest()
if actual != expected:
    raise RuntimeError('El DOCX de referencia cambio desde la inspeccion; no se modificara.')
md=(root/'TopScript-Especificacion.md').read_text(encoding='utf-8-sig')
doc=Document(str(source))
body=doc._element.body
keep=set(p._p for p in doc.paragraphs[:22])
for child in list(body):
    if child.tag == qn('w:sectPr') or child in keep:
        continue
    body.remove(child)
paras=doc.paragraphs
paras[6].text='TopScript: Lenguaje para Presupuestos Personales'
paras[21].text='16 de noviembre de 2026'
# Add a clean body section after the preserved source cover.
section=doc.add_section(WD_SECTION.NEW_PAGE)
section.page_width=Inches(8.27); section.page_height=Inches(11.69)
section.left_margin=section.right_margin=section.top_margin=section.bottom_margin=Inches(1)
section.header_distance=section.footer_distance=Inches(.5)
TEAL=RGBColor(28,91,111); CYAN='159BC4'; PALE='D9EFF7'; INK=RGBColor(25,35,42)

def shade(cell, fill):
    pr=cell._tc.get_or_add_tcPr(); shd=OxmlElement('w:shd'); shd.set(qn('w:fill'),fill); pr.append(shd)
def set_cell_margins(cell, top=75, start=90, bottom=75, end=90):
    tc=cell._tc; pr=tc.get_or_add_tcPr(); m=OxmlElement('w:tcMar')
    for side,val in [('top',top),('start',start),('bottom',bottom),('end',end)]:
        node=OxmlElement('w:'+side); node.set(qn('w:w'),str(val)); node.set(qn('w:type'),'dxa'); m.append(node)
    pr.append(m)
def set_repeat_table_header(row):
    trPr=row._tr.get_or_add_trPr(); e=OxmlElement('w:tblHeader'); e.set(qn('w:val'),'true'); trPr.append(e)
def add_markup(p,text,code=False):
    pat=re.compile(r'(\*\*.*?\*\*|`.*?`)')
    pos=0
    for m in pat.finditer(text):
        if m.start()>pos: p.add_run(text[pos:m.start()])
        piece=m.group(0)
        if piece.startswith('**'):
            r=p.add_run(piece[2:-2]); r.bold=True
        else:
            r=p.add_run(piece[1:-1]); r.font.name='Consolas'; r.font.size=Pt(9); r.font.color.rgb=INK
        pos=m.end()
    if pos<len(text): p.add_run(text[pos:])
    for r in p.runs:
        if code: r.font.name='Consolas'; r.font.size=Pt(8.3)
        elif not r.font.name: r.font.name='Merriweather Light'
        if not r.font.size: r.font.size=Pt(10)
        r.font.color.rgb=r.font.color.rgb or INK

def body_para(text,style='Normal'):
    p=doc.add_paragraph(style=style); add_markup(p,text)
    p.paragraph_format.space_after=Pt(5); p.paragraph_format.line_spacing=1.12
    if style=='Normal': p.alignment=WD_ALIGN_PARAGRAPH.JUSTIFY
    return p

def add_table(rows):
    if not rows: return
    t=doc.add_table(rows=1,cols=len(rows[0])); t.autofit=True
    borders=OxmlElement('w:tblBorders')
    for edge in ('top','left','bottom','right','insideH','insideV'):
        el=OxmlElement('w:'+edge); el.set(qn('w:val'),'single'); el.set(qn('w:sz'),'4'); el.set(qn('w:color'),'159BC4'); borders.append(el)
    t._tbl.tblPr.append(borders)
    for i,val in enumerate(rows[0]):
        c=t.rows[0].cells[i]; c.text=''; shade(c,CYAN); c.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER; set_cell_margins(c)
        p=c.paragraphs[0]; p.paragraph_format.space_after=Pt(0); add_markup(p,val)
        for r in p.runs: r.font.color.rgb=RGBColor(255,255,255); r.bold=True; r.font.size=Pt(9)
    set_repeat_table_header(t.rows[0])
    for ri,row in enumerate(rows[1:]):
        cells=t.add_row().cells
        for ci,val in enumerate(row):
            cells[ci].text=''; cells[ci].vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.TOP; set_cell_margins(cells[ci])
            if ri%2==0: shade(cells[ci],PALE)
            p=cells[ci].paragraphs[0]; p.paragraph_format.space_after=Pt(0); p.paragraph_format.line_spacing=1.0; add_markup(p,val)
            for r in p.runs: r.font.size=Pt(8.7)
    doc.add_paragraph().paragraph_format.space_after=Pt(2)

lines=md.splitlines(); code=False; code_lines=[]; table_lines=[]; first_title=True

def flush_table():
    global table_lines
    if table_lines:
        rows=[]
        for line in table_lines:
            parts=[x.strip() for x in line.strip().strip('|').split('|')]
            if parts and all(re.fullmatch(r'[-: ]+',x or ' ') for x in parts): continue
            rows.append(parts)
        if rows: add_table(rows)
        table_lines=[]
def flush_code():
    global code_lines
    if code_lines:
        for line in code_lines:
            p=doc.add_paragraph(); p.paragraph_format.left_indent=Inches(.18); p.paragraph_format.space_after=Pt(0); p.paragraph_format.line_spacing=1.0
            add_markup(p,line or ' ',code=True)
        doc.add_paragraph().paragraph_format.space_after=Pt(3)
        code_lines=[]

for line in lines:
    if line.startswith('```'):
        flush_table()
        if code: flush_code(); code=False
        else: code=True
        continue
    if code: code_lines.append(line); continue
    if line.lstrip().startswith('|'):
        table_lines.append(line); continue
    flush_table()
    if not line.strip() or line.strip()=='---': continue
    if line.startswith('# '):
        p=doc.add_paragraph(style='Title' if first_title else 'Heading 1'); first_title=False
        p.paragraph_format.space_before=Pt(4); p.paragraph_format.space_after=Pt(10); p.paragraph_format.keep_with_next=True
        add_markup(p,line[2:]);
        for r in p.runs: r.font.name='Merriweather Light'; r.font.size=Pt(20 if p.style.name=='Title' else 17); r.font.color.rgb=TEAL
    elif line.startswith('## '):
        p=doc.add_paragraph(style='Heading 1'); p.paragraph_format.space_before=Pt(14); p.paragraph_format.space_after=Pt(5); p.paragraph_format.keep_with_next=True
        add_markup(p,line[3:]);
        for r in p.runs: r.font.name='Merriweather Light'; r.font.size=Pt(16); r.font.color.rgb=TEAL
    elif line.startswith('### '):
        p=doc.add_paragraph(style='Heading 2'); p.paragraph_format.space_before=Pt(10); p.paragraph_format.space_after=Pt(4); p.paragraph_format.keep_with_next=True
        add_markup(p,line[4:]);
        for r in p.runs: r.font.name='Merriweather Light'; r.font.size=Pt(12); r.font.color.rgb=TEAL
    elif line.startswith('- '):
        p=body_para('• '+line[2:])
    elif re.match(r'^\d+\. ',line):
        p=body_para(line)
    else: body_para(line)
flush_table(); flush_code()
# Define base style to match source report typography.
normal=doc.styles['Normal']; normal.font.name='Merriweather Light'; normal.font.size=Pt(10); normal.font.color.rgb=INK
for sty,size in [('Heading 1',16),('Heading 2',12),('Heading 3',11)]:
    doc.styles[sty].font.name='Merriweather Light'; doc.styles[sty].font.size=Pt(size); doc.styles[sty].font.color.rgb=TEAL
props=doc.core_properties; props.title='TopScript: Especificación del lenguaje, semántica e implementación'; props.subject='Proyecto Integrador de Lenguajes y Autómatas II'; props.keywords='TopScript, DSL, compilador, cuádruplos, autómatas'
out=root/'TopScript-Proyecto-Integrador.docx'; doc.save(str(out)); print(out)




