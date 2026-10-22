"""Stage 1: dump text + tables from every PDF to JSON cache (independent re-read)."""
import json, os, sys, glob, traceback
import pdfplumber
from pypdf import PdfReader

PDF_DIR = "/home/claude/kn0wledgebfre3-sys/compute-ledger/pipeline/pdfs_va"
OUT = "/home/claude/review/va_reread/raw"
os.makedirs(OUT, exist_ok=True)

def extract(path):
    rec = {"file": os.path.basename(path), "pages": [], "error": None, "backend": "pdfplumber"}
    try:
        with pdfplumber.open(path) as pdf:
            for i, pg in enumerate(pdf.pages):
                txt = pg.extract_text() or ""
                try:
                    tables = pg.extract_tables() or []
                except Exception as e:
                    tables = []
                # also try text-strategy tables for borderless layouts
                try:
                    tables_txt = pg.extract_tables({"vertical_strategy": "text", "horizontal_strategy": "text"}) or []
                except Exception:
                    tables_txt = []
                rec["pages"].append({"i": i, "text": txt, "tables": tables, "tables_text": tables_txt})
        if sum(len(p["text"]) for p in rec["pages"]) < 200:
            raise RuntimeError("pdfplumber produced near-empty text")
    except Exception as e:
        rec["error"] = f"pdfplumber: {e}"
        try:
            r = PdfReader(path)
            rec["pages"] = [{"i": i, "text": (p.extract_text() or ""), "tables": [], "tables_text": []} for i, p in enumerate(r.pages)]
            rec["backend"] = "pypdf"
            rec["error"] = None if sum(len(p["text"]) for p in rec["pages"]) >= 200 else rec["error"] + " ; pypdf also near-empty"
        except Exception as e2:
            rec["error"] += f" ; pypdf: {e2}"
    return rec

if __name__ == "__main__":
    files = sorted(glob.glob(os.path.join(PDF_DIR, "*.pdf")))
    for f in files:
        reg = os.path.basename(f)[:-4]
        outp = os.path.join(OUT, reg + ".json")
        if os.path.exists(outp):
            continue
        rec = extract(f)
        json.dump(rec, open(outp, "w"))
        print(reg, rec["backend"], len(rec["pages"]), "pages", "ERR" if rec["error"] else "", rec["error"] or "", flush=True)
