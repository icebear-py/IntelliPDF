from openai import OpenAI
import os
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')

def summarize_chunk(chunk_text: str, must_include: list, model: str) -> str:
	mi = ", ".join(must_include) if must_include else "None"
	
	prompt = f"""
Summarize this newspaper chunk into exactly 2-3 bullet points.
Each bullet should be a complete sentence with key facts.
Include these entities if relevant: {mi}
Keep tone concise and factual.

Chunk:
{chunk_text}
"""
	client = OpenAI(api_key=api_key)
	r = client.chat.completions.create(
		model=model,
		messages=[{"role": "user", "content": prompt}],
		temperature=0.2
	)
	return r.choices[0].message.content.strip()

def summarize_sections(chunk_summaries: list, must_include: list, target_words: int, model: str) -> str:
	mi = ", ".join(must_include) if must_include else "None"
	combined_summaries = "\n\n".join([f"Chunk {i+1}:\n{summary}" for i, summary in enumerate(chunk_summaries)])
	
	prompt = f"""
You are creating a balanced newspaper summary from these chunk summaries.
Identify all the sections from data (e.g., Politics, Business, Sports, World, Tech, Miscellaneous).
Each section should be exactly {target_words} words (±20) and contain 8-12 bullet points.

CRITICAL: If one section has too many points, merge similar ones. If another has too few, expand it.
All sections must be equal length. Use these entities if relevant: {mi}
Do not duplicate the same point across multiple sections. Place each unique fact in the single most appropriate section; if needed, cross-reference briefly instead of repeating.

Return Markdown with level-3 headings and bullet points:
### Section Name
- bullet point 1
- bullet point 2

Chunk Summaries:
{combined_summaries}
"""
	client = OpenAI(api_key=api_key)
	r = client.chat.completions.create(
		model=model,
		messages=[{"role": "user", "content": prompt}],
		temperature=0.2
	)
	return r.choices[0].message.content.strip()

 