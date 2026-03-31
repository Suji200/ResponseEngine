import spacy
from typing import List
import sys
import os


# from models.message_models import Entity

# Add parent directory to path to allow imports when running directly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from models.message_models import Entity
except ImportError:
    # Fallback for when running as standalone script
    from dataclasses import dataclass
    from typing import Optional
    
    @dataclass
    class Entity:
        text: str
        label: str
        start_char: int
        end_char: int
        confidence: float = 1.0
        description: Optional[str] = None

class EntityExtractor:
    """Extracts named entities from text"""
    
    def __init__(self, nlp):
        self.nlp = nlp
    
    def process(self, doc) -> List[Entity]:
        """Extract entities with their metadata"""
        entities = []
        for ent in doc.ents:
            entities.append(Entity(
                text=ent.text,
                label=ent.label_,
                start_char=ent.start_char,
                end_char=ent.end_char,
                confidence=1.0,  # spaCy doesn't provide confidence
                description=spacy.explain(ent.label_)
            ))
        return entities

# For backward compatibility
def extract_entities(nlp, text: str) -> List[Entity]:
    """Helper function for backward compatibility"""
    extractor = EntityExtractor(nlp)
    doc = nlp(text)
    return extractor.process(doc)


# Add this at the end of entity_extractor.py for quick testing
if __name__ == "__main__":
    import spacy
    
    try:
        # Load spaCy model
        nlp = spacy.load("en_core_web_sm")
    except OSError:
        print("Downloading spaCy model...")
        spacy.cli.download("en_core_web_sm")
        nlp = spacy.load("en_core_web_sm")
    
    # Create extractor
    extractor = EntityExtractor(nlp)
    
    # Test texts
    test_texts = [
        "i am sujit and i am happy to going to bangalore",
        "I live in New York and work at Google",
        "Apple Inc. is planning to open a store in Mumbai next year",
        "My name is John and I'm from Paris"
    ]
    
    for text in test_texts:
        print(f"\n{'='*50}")
        print(f"Text: {text}")
        print(f"{'='*50}")
        
        # Process
        doc = nlp(text)
        entities = extractor.process(doc)
        
        # Print entities
        if entities:
            for entity in entities:
                print(f"Entity: {entity.text}")
                print(f"  Label: {entity.label}")
                print(f"  Description: {entity.description}")
                print(f"  Position: {entity.start_char}-{entity.end_char}")
        else:
            print("No entities found")
            


# import spacy
# from typing import List
# from models.message_models import Entity

# class EntityExtractor:
#     """Extracts named entities from text"""
    
#     def __init__(self, nlp):
#         self.nlp = nlp
    
#     def process(self, doc) -> List[Entity]:
#         """Extract entities with their metadata"""
#         entities = []
#         for ent in doc.ents:
#             entities.append(Entity(
#                 text=ent.text,
#                 label=ent.label_,
#                 start_char=ent.start_char,
#                 end_char=ent.end_char,
#                 confidence=1.0,  # spaCy doesn't provide confidence
#                 description=spacy.explain(ent.label_)
#             ))
#         return entities
