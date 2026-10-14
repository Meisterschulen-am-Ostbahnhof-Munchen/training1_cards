"""
Renders one or all Markdown files to styled PDF using the project's house style.
Automates preprocessing, HTML rendering, and headless Chrome/Edge PDF printing.

Usage:
    python render_pdf.py <path/to/doc.md> [<path/to/output.pdf>]
    python render_pdf.py --all
"""
import os
import sys
import shutil
import tempfile
import subprocess
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[3]

BROWSER_CANDIDATES = [
    Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
    Path(r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"),
    Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
    Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
    shutil.which("google-chrome"),
    shutil.which("chrome"),
    shutil.which("msedge"),
    shutil.which("chromium"),
]

def find_browser():
    for candidate in BROWSER_CANDIDATES:
        if candidate and Path(candidate).is_file():
            return str(candidate)
    raise FileNotFoundError("Kein unterstützter Browser (Chrome oder Edge) für PDF-Rendering gefunden.")

def render_md_to_pdf(md_file: Path, pdf_file: Path = None, browser_exe: str = None):
    if not browser_exe:
        browser_exe = find_browser()
    
    md_file = md_file.resolve()
    if pdf_file is None:
        pdf_file = md_file.with_suffix(".pdf")
    else:
        pdf_file = pdf_file.resolve()
    
    print(f"--> Verarbeite: {md_file.relative_to(REPO_ROOT) if md_file.is_relative_to(REPO_ROOT) else md_file}")
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        pre_md = tmp_path / f"{md_file.stem}.pre.md"
        html_file = md_file.parent / f"{md_file.stem}.tmp.html"
        user_data = tmp_path / "browser_profile"
        user_data.mkdir(parents=True, exist_ok=True)
        
        # 1. Preprocess Markdown
        subprocess.run(
            [sys.executable, str(SCRIPT_DIR / "preprocess_md.py"), str(md_file), str(pre_md)],
            check=True
        )
        
        # 2. Render to HTML (place in same folder so relative assets/images resolve)
        subprocess.run(
            [sys.executable, str(SCRIPT_DIR / "render_html.py"), str(pre_md), str(html_file)],
            check=True
        )
        
        # 3. Print to PDF via Chrome/Edge
        html_uri = html_file.as_uri()
        cmd = [
            browser_exe,
            "--headless=new",
            "--disable-gpu",
            "--no-sandbox",
            "--no-pdf-header-footer",
            f"--user-data-dir={user_data}",
            f"--print-to-pdf={pdf_file}",
            html_uri,
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if not pdf_file.is_file() or pdf_file.stat().st_size == 0:
                raise RuntimeError(f"PDF-Generierung fehlgeschlagen. Output: {result.stderr or result.stdout}")
            print(f"    [OK] PDF erstellt: {pdf_file.name} ({pdf_file.stat().st_size} Bytes)")
        finally:
            if html_file.exists():
                html_file.unlink()

def render_all():
    browser = find_browser()
    print(f"Verwende Browser: {browser}")
    
    # Collect project Markdown files, excluding .claude skill files
    md_files = []
    for md in REPO_ROOT.rglob("*.md"):
        if ".claude" in md.parts:
            continue
        md_files.append(md)
    
    if not md_files:
        print("Keine Markdown-Dateien gefunden.")
        return
    
    print(f"Gefundene Markdown-Dateien: {len(md_files)}")
    for md in md_files:
        try:
            render_md_to_pdf(md, browser_exe=browser)
        except Exception as e:
            print(f"    [FEHLER] bei {md.name}: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--all":
        render_all()
    elif len(sys.argv) > 1:
        target_md = Path(sys.argv[1])
        target_pdf = Path(sys.argv[2]) if len(sys.argv) > 2 else None
        render_md_to_pdf(target_md, target_pdf)
    else:
        render_all()
