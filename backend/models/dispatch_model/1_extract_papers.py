#!/usr/bin/env python3
"""
Stage 1: Knowledge Extraction & Corpus Mining
Extracts text from all 13 PDF academic papers and government plans in `papers/`,
cleans formatting, categorizes by domain, and saves a structured corpus to `data/extracted_papers.json`.
"""

import os
import re
import json
import glob
from pathlib import Path

try:
    from pypdf import PdfReader
except ImportError:
    try:
        from PyPDF2 import PdfReader
    except ImportError:
        raise ImportError("Please install pypdf: pip install pypdf")

# Domain classification rules based on keywords in filename or text
DOMAIN_KEYWORDS = {
    "doctrinal": ["tamp", "afad", "ogm", "müdahale", "plan", "yönerge", "goverment", "turkey", "policy", "protocol"],
    "optimization": ["integer linear programming", "optimization", "spatial", "model-based", "linear programming", "ilp", "mathematical"],
    "scheduling_dispatch": ["scheduling", "dispatching", "allocation", "aerial", "routing", "initial attack", "resources", "suppression"]
}

def classify_paper(filename: str, sample_text: str) -> str:
    filename_lower = filename.lower()
    text_lower = sample_text.lower()[:2000]
    
    # Priority check for TAMP / Doctrinal
    if "tamp" in filename_lower or "afad" in text_lower or "türkiye afet" in text_lower:
        return "doctrinal"
    
    scores = {domain: 0 for domain in DOMAIN_KEYWORDS}
    for domain, keywords in DOMAIN_KEYWORDS.items():
        for kw in keywords:
            if kw in filename_lower:
                scores[domain] += 3
            if kw in text_lower:
                scores[domain] += 1
                
    best_domain = max(scores, key=scores.get)
    return best_domain

def clean_text(text: str) -> str:
    """Removes excessive whitespace, hyphenated line breaks, and page header junk."""
    if not text:
        return ""
    # Fix broken hyphenated words at line endings
    text = re.sub(r'(\w+)-\s*\n\s*(\w+)', r'\1\2', text)
    # Replace multiple newlines with double newline
    text = re.sub(r'\n{3,}', '\n\n', text)
    # Replace multiple spaces with single space
    text = re.sub(r'[ \t]+', ' ', text)
    return text.strip()

def chunk_text(text: str, chunk_size: int = 1200, overlap: int = 200) -> list:
    """Splits long text into overlapping word chunks for downstream dataset generation."""
    words = text.split()
    chunks = []
    if not words:
        return chunks
    step = max(1, chunk_size - overlap)
    for i in range(0, len(words), step):
        chunk_words = words[i:i + chunk_size]
        chunk_str = " ".join(chunk_words)
        if len(chunk_str.strip()) > 50:
            chunks.append(chunk_str)
    return chunks

def extract_pdf(pdf_path: str) -> dict:
    reader = PdfReader(pdf_path)
    full_text_pages = []
    
    for page_num, page in enumerate(reader.pages):
        try:
            txt = page.extract_text()
            if txt:
                full_text_pages.append(clean_text(txt))
        except Exception as e:
            print(f"  [WARN] Page {page_num+1} error in {os.path.basename(pdf_path)}: {e}")
            
    full_text = "\n\n".join(full_text_pages)
    domain = classify_paper(os.path.basename(pdf_path), full_text)
    chunks = chunk_text(full_text)
    
    return {
        "filename": os.path.basename(pdf_path),
        "filepath": os.path.abspath(pdf_path),
        "domain": domain,
        "page_count": len(reader.pages),
        "total_characters": len(full_text),
        "chunk_count": len(chunks),
        "chunks": chunks,
        "summary_snippet": full_text[:500].replace("\n", " ") + "..." if full_text else ""
    }

def main():
    base_dir = Path(__file__).resolve().parent
    papers_dir = base_dir / "papers"
    data_dir = base_dir / "data"
    data_dir.mkdir(exist_ok=True)
    
    output_path = data_dir / "extracted_papers.json"
    
    print("=" * 70)
    print("  FIREFL-AI: STAGE 1 - PDF KNOWLEDGE EXTRACTION & CORPUS MINING")
    print("=" * 70)
    print(f"Searching for PDF papers in: {papers_dir}")
    
    pdf_files = sorted(glob.glob(str(papers_dir / "*.pdf")))
    if not pdf_files:
        print(f"[ERROR] No PDF files found in {papers_dir}!")
        return

    print(f"Found {len(pdf_files)} PDF papers to extract.\n")
    
    corpus = []
    total_chars = 0
    total_chunks = 0
    
    for i, pdf_path in enumerate(pdf_files, 1):
        filename = os.path.basename(pdf_path)
        print(f"[{i:2d}/{len(pdf_files)}] Extracting: {filename} ...", end=" ")
        try:
            data = extract_pdf(pdf_path)
            corpus.append(data)
            total_chars += data["total_characters"]
            total_chunks += data["chunk_count"]
            print(f"OK ({data['page_count']} pages | {data['domain'].upper()} | {data['chunk_count']} chunks)")
        except Exception as e:
            print(f"FAILED ({e})")
            
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(corpus, f, ensure_ascii=False, indent=2)
        
    print("\n" + "=" * 70)
    print(f"  EXTRACTION COMPLETE: {len(corpus)} papers processed.")
    print(f"  Total Characters Extracted : {total_chars:,}")
    print(f"  Total Knowledge Chunks     : {total_chunks:,}")
    print(f"  Saved Corpus File          : {output_path}")
    print("=" * 70)

if __name__ == "__main__":
    main()
