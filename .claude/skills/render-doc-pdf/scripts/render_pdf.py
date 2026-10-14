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

if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from preprocess_md import preprocess_markdown
from render_html import render_markdown_to_html

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
        import uuid
        unique_token = uuid.uuid4().hex[:8]
        pre_md = tmp_path / f"{md_file.stem}.pre.md"
        html_file = md_file.parent / f".tmp_{md_file.stem}_{unique_token}.html"
        tmp_pdf = tmp_path / "output.pdf"
        user_data = tmp_path / "browser_profile"
        user_data.mkdir(parents=True, exist_ok=True)
        
        # 1. Preprocess Markdown (in-process)
        preprocess_markdown(md_file, pre_md)
        
        # 2. Render to HTML (in-process, placed beside source file so relative assets resolve)
        render_markdown_to_html(pre_md, html_file)
        
        # 3. Print to PDF via Chrome/Edge into a temporary PDF first
        html_uri = html_file.as_uri()
        cmd = [
            str(Path(browser_exe).resolve()),
            "--headless=new",
            "--disable-gpu",
            "--no-sandbox",
            "--no-pdf-header-footer",
            f"--user-data-dir={user_data}",
            f"--print-to-pdf={tmp_pdf}",
            html_uri,
        ]
        
        try:
            result = subprocess.run(  # nosec B603
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                shell=False,
                check=False
            )
            if result.returncode != 0 or not tmp_pdf.is_file() or tmp_pdf.stat().st_size == 0:
                raise RuntimeError(f"PDF-Generierung fehlgeschlagen (code {result.returncode}). Output: {result.stderr or result.stdout}")
            import shutil
            shutil.move(str(tmp_pdf), str(pdf_file))
            print(f"    [OK] PDF erstellt: {pdf_file.name} ({pdf_file.stat().st_size} Bytes)")
        finally:
            if html_file.is_file():
                try:
                    html_file.unlink()
                except OSError:
                    pass

def render_all() -> int:
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
        return 0
    
    print(f"Gefundene Markdown-Dateien: {len(md_files)}")
    failed_count = 0
    for md in md_files:
        try:
            render_md_to_pdf(md, browser_exe=browser)
        except Exception as e:
            failed_count += 1
            print(f"    [FEHLER] bei {md.name}: {e}")
    
    return 1 if failed_count > 0 else 0

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--all":
        sys.exit(render_all())
    elif len(sys.argv) > 1:
        target_md = Path(sys.argv[1])
        target_pdf = Path(sys.argv[2]) if len(sys.argv) > 2 else None
        render_md_to_pdf(target_md, target_pdf)
    else:
        sys.exit(render_all())
