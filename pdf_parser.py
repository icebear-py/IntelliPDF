import pdfplumber
import re

def extract_text_from_pdf(pdf_path: str) -> str:
	text = []
	with pdfplumber.open(pdf_path) as pdf:
		for page in pdf.pages:
			content = page.extract_text()
			if content:
				text.append(content)
	raw_text = "\n".join(text)
	cleaned = re.sub(r'\s+', ' ', raw_text).strip()
	return cleaned

def extract_text_by_pages(pdf_path: str) -> list:
	pages = []
	with pdfplumber.open(pdf_path) as pdf:
		for i, page in enumerate(pdf.pages):
			content = page.extract_text()
			if content:
				cleaned = re.sub(r'\s+', ' ', content).strip()
				pages.append(f"[PAGE_{i+1}] {cleaned}")
	return pages

def chunk_text(text: str, max_words: int = 500, overlap_words: int = 50) -> list:
	words = text.split()
	chunks = []
	for i in range(0, len(words), max_words - overlap_words):
		chunk = " ".join(words[i:i+max_words])
		chunks.append(chunk)
	return chunks

def chunk_by_pages(pages: list, pages_per_chunk: int = 2, max_words: int = 500) -> list:
	chunks = []
	for i in range(0, len(pages), pages_per_chunk):
		chunk_pages = pages[i:i+pages_per_chunk]
		chunk_text = " ".join(chunk_pages)
		words = chunk_text.split()
		if len(words) > max_words:
			chunk_text = " ".join(words[:max_words])
		chunks.append(chunk_text)
	return chunks