def select_balanced_context(section_text, ents, budget_words=500, chunk_size=200):
	words = section_text.split()
	chunks = []
	for start_index in range(0, len(words), chunk_size):
		end_index = start_index + chunk_size
		chunk_words = words[start_index:end_index]
		chunk_text = " ".join(chunk_words)
		chunks.append(chunk_text)

	chunk_scores = []
	for chunk_text in chunks:
		total_entity_hits = 0
		for entity_list in ents.values():
			for entity in entity_list:
				total_entity_hits += chunk_text.count(entity)
		chunk_scores.append((chunk_text, total_entity_hits))

	chunk_scores.sort(key=lambda x: x[1], reverse=True)

	selected, total = [], 0
	for ch, _ in chunk_scores:
		w = len(ch.split())
		if total + w > budget_words:
			break
		selected.append(ch)
		total += w

	return " ".join(selected)
