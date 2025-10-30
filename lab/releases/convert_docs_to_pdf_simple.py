#!/usr/bin/env python3
"""
Convert markdown to PDF using lightweight approach
Uses reportlab for PDF generation (already installed)
"""
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
import re

RELEASE_DIR = Path('lab/releases/RLE_Standalone_v1.0')
PDF_DIR = RELEASE_DIR / 'pdf'
PDF_DIR.mkdir(parents=True, exist_ok=True)

def md_to_pdf(md_path, output_path):
    """Convert markdown to PDF using reportlab"""
    print(f"Converting: {md_path.name}")
    
    # Read markdown
    md_content = md_path.read_text(encoding='utf-8')
    
    # Create PDF
    doc = SimpleDocTemplate(str(output_path), pagesize=letter,
                          rightMargin=72, leftMargin=72,
                          topMargin=72, bottomMargin=18)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=30,
    )
    heading1_style = ParagraphStyle(
        'CustomH1',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#34495e'),
        spaceAfter=12,
    )
    heading2_style = ParagraphStyle(
        'CustomH2',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#34495e'),
        spaceAfter=10,
    )
    
    # Parse markdown line by line
    lines = md_content.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Skip empty lines
        if not line:
            i += 1
            continue
        
        # H1
        if line.startswith('# '):
            text = line[2:].strip()
            elements.append(Paragraph(text, title_style))
            elements.append(Spacer(1, 0.2*inch))
        
        # H2
        elif line.startswith('## '):
            text = line[3:].strip()
            elements.append(Paragraph(text, heading1_style))
            elements.append(Spacer(1, 0.15*inch))
        
        # H3
        elif line.startswith('### '):
            text = line[4:].strip()
            elements.append(Paragraph(text, heading2_style))
            elements.append(Spacer(1, 0.1*inch))
        
        # Bullet list
        elif line.startswith('- ') or line.startswith('* '):
            text = line[2:].strip()
            elements.append(Paragraph(f"• {text}", styles['Normal']))
            elements.append(Spacer(1, 0.05*inch))
        
        # Table (basic)
        elif line.startswith('|'):
            table_rows = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                cells = [c.strip() for c in lines[i].strip().split('|')]
                cells = [c for c in cells if c]  # Remove empty
                if cells and not all(c == '-' or c.startswith(':') for c in cells):
                    table_rows.append(cells)
                i += 1
            i -= 1  # Back up one
            
            if table_rows:
                t = Table(table_rows)
                t.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ]))
                elements.append(t)
                elements.append(Spacer(1, 0.2*inch))
        
        # Inline code
        elif '`' in line:
            text = line
            # Escape special chars and preserve code
            text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            elements.append(Paragraph(text, styles['Normal']))
            elements.append(Spacer(1, 0.05*inch))
        
        # Regular paragraph
        else:
            text = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            elements.append(Paragraph(text, styles['Normal']))
            elements.append(Spacer(1, 0.1*inch))
        
        i += 1
    
    # Build PDF
    doc.build(elements)
    print(f"  -> {output_path.name}")

def main():
    print("\n" + "="*70)
    print("CONVERTING DOCUMENTATION TO PDF (ReportLab)")
    print("="*70 + "\n")
    
    # Find all markdown files
    md_files = []
    for pattern in ['README.md', 'REPRODUCE.md']:
        md_files.extend(RELEASE_DIR.rglob(pattern))
    
    # Add specific reports
    archive_files = [
        Path('lab/sessions/archive/CROSS_DEVICE_RLE_COMPREHENSIVE.md'),
        Path('lab/sessions/archive/CROSS_DEVICE_RLE_SUMMARY.md'),
    ]
    
    for f in archive_files:
        if f.exists():
            md_files.append(f)
    
    md_files = list(set(md_files))
    
    print(f"Found {len(md_files)} markdown files to convert\n")
    
    for md_file in md_files:
        if md_file.exists():
            try:
                output_path = PDF_DIR / f"{md_file.stem}.pdf"
                md_to_pdf(md_file, output_path)
            except Exception as e:
                print(f"  [FAIL] {e}")
    
    # Copy existing PDFs from docs
    print("\nCopying existing PDFs...")
    for pdf_src in RELEASE_DIR.glob('docs/*.pdf'):
        import shutil
        shutil.copy2(pdf_src, PDF_DIR / pdf_src.name)
        print(f"Copied: {pdf_src.name}")
    
    print("\n" + "="*70)
    print("PDF CONVERSION COMPLETE")
    print("="*70)
    print(f"\nPDFs saved to: {PDF_DIR}")
    print(f"Total PDFs: {len(list(PDF_DIR.glob('*.pdf')))}")
    print()

if __name__ == '__main__':
    main()

