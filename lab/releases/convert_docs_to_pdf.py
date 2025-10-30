#!/usr/bin/env python3
"""
Convert all markdown documentation to PDFs in the standalone release
"""
import subprocess
import sys
from pathlib import Path

RELEASE_DIR = Path('lab/releases/RLE_Standalone_v1.0')
PDF_DIR = RELEASE_DIR / 'pdf'
PDF_DIR.mkdir(parents=True, exist_ok=True)

def convert_md_to_pdf(md_path, output_dir):
    """Convert markdown to PDF using pandoc or markdown-pdf"""
    try:
        import markdown
        from weasyprint import HTML, CSS
    except ImportError:
        print("Installing markdown-pdf dependencies...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'markdown', 'weasyprint', '--quiet'])
        import markdown
        from weasyprint import HTML, CSS
    
    print(f"Converting: {md_path.name}")
    
    # Read markdown
    md_content = md_path.read_text(encoding='utf-8')
    
    # Convert to HTML
    html_body = markdown.markdown(md_content, extensions=['tables', 'fenced_code', 'codehilite'])
    
    # Wrap in full HTML document
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
        pre {{ background: #f4f4f4; padding: 10px; border-radius: 5px; overflow-x: auto; }}
        code {{ background: #f4f4f4; padding: 2px 4px; border-radius: 3px; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #4CAF50; color: white; }}
        h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
        h2 {{ color: #34495e; margin-top: 30px; }}
    </style>
</head>
<body>
{html_body}
</body>
</html>"""
    
    # Convert HTML to PDF
    output_path = output_dir / f"{md_path.stem}.pdf"
    HTML(string=html).write_pdf(output_path)
    
    print(f"  -> {output_path.name}")

def main():
    print("\n" + "="*70)
    print("CONVERTING DOCUMENTATION TO PDF")
    print("="*70 + "\n")
    
    # Find all markdown files in the release
    md_files = []
    for pattern in ['*.md', 'README.md', 'REPRODUCE.md']:
        md_files.extend(RELEASE_DIR.rglob(pattern))
    
    # Add specific reports from archive
    archive_files = [
        Path('lab/sessions/archive/CROSS_DEVICE_RLE_COMPREHENSIVE.md'),
        Path('lab/sessions/archive/CROSS_DEVICE_RLE_SUMMARY.md'),
    ]
    
    for f in archive_files:
        if f.exists():
            md_files.append(f)
    
    # Remove duplicates
    md_files = list(set(md_files))
    
    print(f"Found {len(md_files)} markdown files to convert\n")
    
    for md_file in md_files:
        if md_file.exists():
            try:
                convert_md_to_pdf(md_file, PDF_DIR)
            except Exception as e:
                print(f"  [FAIL] {e}")
    
    # Copy existing PDFs
    print("\nCopying existing PDFs...")
    for pdf_src in RELEASE_DIR.rglob('*.pdf'):
        if 'pdf' not in str(pdf_src):  # Don't copy from our pdf dir
            shutil.copy2(pdf_src, PDF_DIR / pdf_src.name)
            print(f"Copied: {pdf_src.name}")
    
    print("\n" + "="*70)
    print("PDF CONVERSION COMPLETE")
    print("="*70)
    print(f"\nPDFs saved to: {PDF_DIR}")
    print(f"Total PDFs: {len(list(PDF_DIR.glob('*.pdf')))}")
    print()

if __name__ == '__main__':
    import shutil
    main()

