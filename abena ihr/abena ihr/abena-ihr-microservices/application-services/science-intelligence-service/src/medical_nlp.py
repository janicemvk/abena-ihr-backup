import spacy
from fastapi import FastAPI, Request
from typing import List, Dict

try:
    import scispacy
    from scispacy.linking import EntityLinker
except ImportError:
    scispacy = None
    EntityLinker = None

app = FastAPI(title="Medical NLP Service")

class MedicalNLP:
    def __init__(self, model_name: str = "en_core_sci_sm"):
        self.model_name = model_name
        self.nlp = spacy.load(model_name)
        if EntityLinker:
            self.linker = EntityLinker(resolve_abbreviations=True, name="umls")
            self.nlp.add_pipe(self.linker)
        else:
            self.linker = None

    def extract_entities(self, text: str) -> List[Dict]:
        doc = self.nlp(text)
        entities = []
        for ent in doc.ents:
            entity = {
                "text": ent.text,
                "label": ent.label_,
                "start_char": ent.start_char,
                "end_char": ent.end_char
            }
            if self.linker and ent._.kb_ents:
                entity["umls_concepts"] = [
                    {"concept_id": c[0], "score": c[1]} for c in ent._.kb_ents
                ]
            entities.append(entity)
        return entities

    def detect_negation(self, text: str) -> List[Dict]:
        # Simple negation detection (placeholder)
        doc = self.nlp(text)
        results = []
        for ent in doc.ents:
            negated = "no " in text.lower() or "denies " in text.lower()
            results.append({
                "text": ent.text,
                "label": ent.label_,
                "negated": negated
            })
        return results

    def normalize_concepts(self, text: str) -> List[Dict]:
        doc = self.nlp(text)
        concepts = []
        if self.linker:
            for ent in doc.ents:
                for umls_ent in ent._.kb_ents:
                    concepts.append({
                        "text": ent.text,
                        "umls_id": umls_ent[0],
                        "score": umls_ent[1]
                    })
        return concepts

nlp_engine = MedicalNLP()

@app.post("/nlp/entities")
async def extract_entities(request: Request):
    data = await request.json()
    text = data.get("text", "")
    return {"entities": nlp_engine.extract_entities(text)}

@app.post("/nlp/negation")
async def detect_negation(request: Request):
    data = await request.json()
    text = data.get("text", "")
    return {"negation": nlp_engine.detect_negation(text)}

@app.post("/nlp/normalize")
async def normalize_concepts(request: Request):
    data = await request.json()
    text = data.get("text", "")
    return {"concepts": nlp_engine.normalize_concepts(text)} 