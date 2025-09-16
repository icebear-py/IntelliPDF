import os, yaml, glob
from pdf_parser import extract_text_from_pdf, chunk_text, extract_text_by_pages, chunk_by_pages
from entity_extractor import extract_entities, entities_must_include, compute_context_budget
from summarizer import  summarize_chunk, summarize_sections
from pdf_writer import write_summary_pdf

def process_inputs(input_folder="data/input_pdfs", config_path="configs/settings.yaml"):
	with open(config_path) as f:
		cfg = yaml.safe_load(f)

	pdfs = glob.glob(os.path.join(input_folder, "*.pdf"))
	print(f"Found {len(pdfs)} PDFs in '{input_folder}'")

	results = []
	for pdf in pdfs:
		print(f"\nProcessing: {os.path.basename(pdf)}")
		print("Step 1/8: Extracting text by pages...")
		pages = extract_text_by_pages(pdf)
		print(f"  Extracted {len(pages)} pages")
		
		print("Step 2/8: Creating page-aware chunks...")
		chunks = chunk_by_pages(pages, 
								pages_per_chunk=cfg.get("pages_per_chunk", 2),
								max_words=cfg.get("chunk_max_words", 500))
		print(f"  Created {len(chunks)} page-aware chunks")

		print("Step 3/8: Running NER over chunks...")
		chunk_entities = [extract_entities(ch) for ch in chunks]
		print("  NER completed")

		print("Step 4/8: Computing context budget and selecting balanced chunks...")
		total_entity_count = sum(len(v) for ce in chunk_entities for v in ce.values())
		budget_words = compute_context_budget(
			entity_count=total_entity_count,
			base=cfg.get("context_base", 1500),
			boost_per=cfg.get("context_boost_per", 10),
			boost_cap=cfg.get("context_boost_cap", 1000),
			hard_cap=cfg.get("context_hard_cap", 2500),
		)
		print(f"  Budget words: {budget_words}")

	
		chunks_per_page_range = max(1, budget_words // (len(chunks) * cfg.get("chunk_max_words", 500)))
		selected_chunks = []
		for i in range(0, len(chunks), cfg.get("pages_per_chunk", 2)):
			page_range_chunks = chunks[i:i+cfg.get("pages_per_chunk", 2)]
			page_range_entities = chunk_entities[i:i+cfg.get("pages_per_chunk", 2)]
			scored = []
			for ch, ents in zip(page_range_chunks, page_range_entities):
				score = sum(len(v) for v in ents.values())
				scored.append((ch, score, len(ch.split())))
			scored.sort(key=lambda x: x[1], reverse=True)
			
		
			taken = 0
			for ch, _, w in scored:
				if taken >= chunks_per_page_range:
					break
				if w > 0:
					selected_chunks.append(ch)
					taken += 1

		print(f"  Selected {len(selected_chunks)} chunks from {len(chunks)} total (~{sum(len(ch.split()) for ch in selected_chunks)} words)")

		if not selected_chunks:
			selected_chunks = chunks[:3]
			print("  Fallback: no selected chunks; using first 3 chunks")

	
		merged_ents = {"PERSON": [], "ORG": [], "GPE": [], "SCAM": []}
		for ents in chunk_entities:
			for k,v in ents.items():
				if k in merged_ents:
					merged_ents[k].extend(v)
		must_include = entities_must_include(merged_ents,k=cfg.get("must_include_topk", 12))
		print(f"Step 5/8: Must-include entities (top {len(must_include)}): {', '.join(must_include)}")

		print("Step 6/8: First pass - Summarizing individual chunks...")
		chunk_summaries = []
		for i, chunk in enumerate(selected_chunks):
			print(f"  Processing chunk {i+1}/{len(selected_chunks)}...")
			chunk_summary = summarize_chunk(chunk, must_include, cfg.get("model", "gpt-4o-mini"))
			chunk_summaries.append(chunk_summary)

		print("Step 7/8: Second pass - Combining chunk summaries into balanced sections...")
		section_summary = summarize_sections(
			chunk_summaries, 
			must_include, 
			cfg.get("target_words", 800),
			cfg.get("model", "gpt-4o-mini")
		)
		print("  Hierarchical summarization completed")

		print("Step 8/8: Saving outputs...")
		results.append({
			"pdf": os.path.basename(pdf),
			"entities": must_include,
			"chunk_summaries": chunk_summaries,
			"final_summary": section_summary
		})
		
		os.makedirs("data/outputs", exist_ok=True)
		out_pdf = os.path.join("data/outputs", os.path.splitext(os.path.basename(pdf))[0] + "_summary.pdf")
		write_summary_pdf(summary_markdown=section_summary, output_path=out_pdf)
		print(f"Saved: {out_pdf}")
	return results

if __name__ == "__main__":
	print("Starting processing...")
	process_inputs()
	print("All PDFs processed successfully.")