# -*- coding: utf-8 -*-
"""
Render RESPONSE_TO_COMMENTS.md to a submittable PDF in the project house style.

A small Markdown subset is enough for that file: headings, paragraphs, bullets,
pipe tables, blockquotes, fenced code, horizontal rules, and inline bold/italic
/code. Rendering from the Markdown rather than duplicating the text means the
two deliverables cannot drift apart.

Run:  python build_response_pdf.py
Output: week12_response_to_comments.pdf
"""
import re
from pathlib import Path
from fpdf import FPDF
from fpdf.enums import XPos, YPos

HERE = Path(__file__).resolve().parent
SRC = HERE / 'RESPONSE_TO_COMMENTS.md'
OUT = HERE / 'week12_response_to_comments.pdf'

PURPLE = (69, 0, 132); GOLD = (203, 182, 119); DARK = (51, 51, 51)
GREY = (89, 89, 89); LINE = (214, 214, 214); ALTROW = (244, 239, 225)
CODEBG = (243, 243, 246)
PAGE_W = 190


def clean(s):
    """Map to what the built-in latin-1 core fonts can render.

    Greek letters appear throughout this document (alpha, tau, beta, gamma) and
    Helvetica cannot encode them, so they are spelled out. Anything still
    outside latin-1 after that is dropped rather than allowed to abort the
    build, and reported once at the end.
    """
    s = str(s)
    for a, b in (('—', ', '), ('–', '-'), ('−', '-'), ('’', "'"), ('‘', "'"),
                 ('“', '"'), ('”', '"'), ('→', '->'), ('±', '+/-'), ('×', 'x'),
                 ('≈', '~'), ('≤', '<='), ('≥', '>='), ('·', '.'),
                 ('α', 'alpha'), ('β', 'beta'), ('τ', 'tau'), ('γ', 'gamma'),
                 ('ρ', 'rho'), ('σ', 'sigma'), ('μ', 'mu'), ('Δ', 'delta'),
                 ('✅', '[done] '), ('❌', '[missing] '), ('🔄', '[running] '),
                 ('⚠️', '[note] '), ('⚠', '[note] '), ('•', '-'),
                 ('₉', '9'), ('₁₀', '10'), ('‑', '-'), (' ', ' ')):
        s = s.replace(a, b)
    out = s.encode('latin-1', 'ignore').decode('latin-1')
    if out != s:
        DROPPED.update(set(s) - set(out))
    return out


DROPPED = set()


class PDF(FPDF):
    def header(self):
        if self.page_no() == 1:
            return
        self.set_font('Helvetica', '', 7.5); self.set_text_color(*GREY)
        self.cell(0, 5, 'Response to Reviewer Comments  |  Group 1  |  '
                        'Trigger-Agnostic Behavioral Trust', align='L')
        self.ln(6)

    def footer(self):
        self.set_y(-11); self.set_font('Helvetica', '', 7.5); self.set_text_color(*GREY)
        self.cell(0, 5, f'Page {self.page_no()}', align='C')


pdf = PDF(format='A4')
pdf.set_auto_page_break(auto=True, margin=13)
pdf.set_margins(10, 11, 10)
pdf.add_page()

INLINE = re.compile(r'(\*\*.+?\*\*|\*[^*]+?\*|`[^`]+?`)')


def rich(text, size=9.1, lh=4.35, indent=0.0):
    """Write a paragraph honouring **bold**, *italic* and `code`."""
    pdf.set_text_color(*DARK)
    x_left = 10 + indent
    pdf.set_x(x_left)
    avail = PAGE_W - indent
    for tok in [t for t in INLINE.split(clean(text)) if t]:
        if tok.startswith('**') and tok.endswith('**'):
            style, body = 'B', tok[2:-2]
        elif tok.startswith('*') and tok.endswith('*'):
            style, body = 'I', tok[1:-1]
        elif tok.startswith('`') and tok.endswith('`'):
            style, body = 'code', tok[1:-1]
        else:
            style, body = '', tok
        pdf.set_font('Courier' if style == 'code' else 'Helvetica',
                     '' if style == 'code' else style,
                     size - 0.7 if style == 'code' else size)
        for i, word in enumerate(body.split(' ')):
            if word == '':
                continue
            w = pdf.get_string_width(word + ' ')
            if pdf.get_x() + w > 10 + PAGE_W:
                pdf.ln(lh); pdf.set_x(x_left)
            pdf.cell(w, lh, word + ' ')
    pdf.ln(lh)


def h1(t):
    if pdf.get_y() > 250:
        pdf.add_page()
    pdf.ln(1.4); pdf.set_font('Helvetica', 'B', 13.0); pdf.set_text_color(*PURPLE)
    pdf.multi_cell(0, 6.4, clean(t), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_draw_color(*PURPLE); pdf.set_line_width(0.45)
    y = pdf.get_y(); pdf.line(10, y + 0.4, 200, y + 0.4); pdf.ln(2.2)


def h2(t):
    if pdf.get_y() > 262:
        pdf.add_page()
    pdf.ln(0.9); pdf.set_font('Helvetica', 'B', 10.4); pdf.set_text_color(*PURPLE)
    pdf.multi_cell(0, 5.0, clean(t), new_x=XPos.LMARGIN, new_y=YPos.NEXT); pdf.ln(0.3)


def hr():
    pdf.ln(1.0); pdf.set_draw_color(*LINE); pdf.set_line_width(0.3)
    y = pdf.get_y(); pdf.line(10, y, 200, y); pdf.ln(1.6)


def quote(t):
    pdf.set_fill_color(*ALTROW); pdf.set_draw_color(*GOLD); pdf.set_line_width(0.9)
    x, y = 10, pdf.get_y()
    pdf.set_x(13)
    rich(t, size=8.9, lh=4.2, indent=3.0)
    pdf.line(x, y, x, pdf.get_y()); pdf.ln(1.0)


def bullet(t, level=0):
    ind = 3.0 + level * 4.0
    pdf.set_font('Helvetica', '', 9.1); pdf.set_text_color(*DARK)
    pdf.set_x(10 + ind)
    pdf.cell(3.6, 4.35, '-')
    rich(t, indent=ind + 3.6)


def codeblock(lines):
    pdf.set_fill_color(*CODEBG); pdf.set_font('Courier', '', 8.0)
    pdf.set_text_color(*DARK)
    for ln in lines:
        pdf.set_x(12)
        pdf.cell(PAGE_W - 4, 4.1, clean('  ' + ln), border=0, fill=True,
                 new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(1.2)


def table(rows):
    """Render a pipe table with wrapping in every column.

    Column widths are proportional to the widest content each column actually
    holds, rather than fixed by position: this document mixes tables whose first
    column is a long label with tables whose first column is a single digit, and
    a positional rule truncates one or the other. Every cell wraps; nothing is
    clipped.
    """
    if not rows:
        return
    ncol = max(len(r) for r in rows)
    rows = [(list(r) + [''] * ncol)[:ncol] for r in rows]
    hdr, body = rows[0], rows[1:]
    fs = 7.6 if ncol <= 4 else (7.0 if ncol == 5 else 6.4)
    lh = 3.7

    # width demand per column, from the longest single cell, then normalise
    pdf.set_font('Helvetica', '', fs)
    demand = []
    for ci in range(ncol):
        w = max([pdf.get_string_width(clean(r[ci]).replace('**', '')) for r in rows] + [8.0])
        demand.append(min(w + 4.0, PAGE_W * 0.55))
    total = sum(demand)
    widths = [d / total * PAGE_W for d in demand]
    # keep every column wide enough to fit a couple of words
    MINW = 13.0
    short = [i for i, w in enumerate(widths) if w < MINW]
    if short:
        need = sum(MINW - widths[i] for i in short)
        donors = [i for i in range(ncol) if i not in short]
        pool = sum(widths[i] for i in donors)
        for i in short:
            widths[i] = MINW
        for i in donors:
            widths[i] -= need * (widths[i] / pool)

    def cell_lines(txt, w):
        return pdf.multi_cell(w, lh, clean(txt).replace('**', ''), border=0,
                              dry_run=True, output='LINES')

    def render_header():
        pdf.set_font('Helvetica', 'B', fs); pdf.set_fill_color(*PURPLE)
        pdf.set_text_color(255, 255, 255)
        pdf.set_draw_color(*LINE); pdf.set_line_width(0.2)
        h = max(5.3, lh * max(len(cell_lines(c, w)) for c, w in zip(hdr, widths)) + 1.1)
        y0 = pdf.get_y(); x = 10.0
        for c, w in zip(hdr, widths):
            pdf.set_xy(x, y0)
            pdf.multi_cell(w, lh, clean(c), border=0, align='C', fill=True,
                           new_x=XPos.RIGHT, new_y=YPos.TOP, max_line_height=lh)
            pdf.set_xy(x, y0); pdf.cell(w, h, '', border=1)
            x += w
        pdf.set_xy(10, y0 + h)

    if pdf.get_y() + 5.3 * 3 > 297 - 15:
        pdf.add_page()
    render_header()
    for ri, row in enumerate(body):
        pdf.set_font('Helvetica', '', fs); pdf.set_text_color(*DARK)
        pdf.set_fill_color(*(ALTROW if ri % 2 else (255, 255, 255)))
        h = max(4.9, lh * max(len(cell_lines(c, w)) for c, w in zip(row, widths)) + 1.1)
        if pdf.get_y() + h > 297 - 15:
            pdf.add_page(); render_header()
        y0 = pdf.get_y(); x = 10.0
        for ci, (c, w) in enumerate(zip(row, widths)):
            pdf.set_xy(x, y0)
            pdf.multi_cell(w, lh, clean(c).replace('**', ''), border=0,
                           align='L' if ci == 0 else 'C', fill=True,
                           new_x=XPos.RIGHT, new_y=YPos.TOP, max_line_height=lh)
            pdf.set_xy(x, y0); pdf.cell(w, h, '', border=1)
            x += w
        pdf.set_xy(10, y0 + h)
    pdf.ln(1.4)


# ------------------------------------------------------------------ title block
pdf.set_font('Helvetica', 'B', 17); pdf.set_text_color(*PURPLE)
pdf.multi_cell(0, 8.0, 'Response to Reviewer Comments',
               new_x=XPos.LMARGIN, new_y=YPos.NEXT)

src = SRC.read_text(encoding='utf-8').split('\n')
i = 0
if src and src[0].startswith('# '):
    i = 1

pending_table = []
in_code, code_buf = False, []

while i < len(src):
    raw = src[i].rstrip()
    s = raw.strip()

    if s.startswith('```'):
        if in_code:
            codeblock(code_buf); code_buf, in_code = [], False
        else:
            in_code = True
        i += 1
        continue
    if in_code:
        code_buf.append(raw)
        i += 1
        continue

    is_row = s.startswith('|') and s.endswith('|')
    if is_row:
        cells = [c.strip() for c in s.strip('|').split('|')]
        if not all(set(c) <= set('-: ') for c in cells):      # skip separator row
            pending_table.append(cells)
        i += 1
        continue
    if pending_table:
        table(pending_table); pending_table = []

    if not s:
        pdf.ln(1.4)
    elif s.startswith('---'):
        hr()
    elif s.startswith('### '):
        h2(s[4:])
    elif s.startswith('## '):
        h1(s[3:])
    elif s.startswith('> '):
        block = []
        while i < len(src) and src[i].strip().startswith('>'):
            block.append(src[i].strip().lstrip('>').strip())
            i += 1
        quote(' '.join(block))
        continue
    elif re.match(r'^\d+\.\s', s):
        bullet(re.sub(r'^\d+\.\s', '', s))
    elif s.startswith('- ') or s.startswith('* '):
        bullet(s[2:], level=1 if raw.startswith('  ') else 0)
    else:
        rich(s)
    i += 1

if pending_table:
    table(pending_table)
if in_code and code_buf:
    codeblock(code_buf)

pdf.output(str(OUT))
print(f'wrote {OUT}')
if DROPPED:
    print('note: characters dropped as unrenderable in a core font:',
          ' '.join(sorted(DROPPED)))
