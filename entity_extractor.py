import spacy

try:
	nlp = spacy.load("en_core_web_sm")
except Exception as e:
	raise RuntimeError("spaCy model 'en_core_web_sm' not installed. Run: python -m spacy download en_core_web_sm")

def extract_entities(text: str):
	doc = nlp(text)
	ents = {"PERSON": [], "ORG": [], "GPE": []}
	for e in doc.ents:
		if e.label_ in ents:
			ents[e.label_].append(e.text)
	return ents

def entities_must_include(ents, k=12):
	from collections import Counter
	bag = Counter()
	for key in ["PERSON","ORG","GPE"]:
		for v in ents.get(key, []):
			if v:
				bag[v.strip()] += 1
	return [e for e, _ in bag.most_common(k)]

def compute_context_budget(entity_count: int,
						   base: int = 1500,
						   boost_per: int = 10,
						   boost_cap: int = 1000,
						   hard_cap: int = 2500) -> int:
	entity_boost = min(entity_count * boost_per, boost_cap)
	return min(base + entity_boost, hard_cap)

