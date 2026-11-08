"""Create five small academic fixtures, including a known fact on PDF page 2."""
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
TARGET=ROOT/'examples'

def make_documents(target=TARGET):
    target.mkdir(parents=True,exist_ok=True)
    import pymupdf as fitz
    pdf=fitz.open()
    page=pdf.new_page()
    page.insert_text((60,80),'Agent-Based Modeling: Course Notes',fontsize=19)
    page.insert_text((60,120),'Agents are autonomous entities that follow local rules and interact with an environment.')
    page=pdf.new_page()
    page.insert_text((60,80),'Sable Simulation Experiment',fontsize=19)
    page.insert_textbox(fitz.Rect(60,120,530,680),'In the fictional Sable simulation, there are exactly 37 agents.\nEach agent starts with 12 energy units.\nThe simulation runs for 80 ticks.\nEmergent behavior is a system-level pattern arising from local agent interactions.',fontsize=12)
    pdf.save(target/'01-agent-modeling.pdf')
    pdf.close()
    from docx import Document
    doc=Document()
    doc.add_heading('Feedback and Emergence',0)
    doc.add_paragraph('Positive feedback reinforces an initial change. Negative feedback counteracts a change and can stabilize a system. Emergence is a collective pattern produced by local interactions, such as flocking birds.')
    doc.save(target/'02-feedback.docx')
    from pptx import Presentation
    presentation=Presentation()
    slide=presentation.slides.add_slide(presentation.slide_layouts[1])
    slide.shapes.title.text='Model Verification and Validation'
    slide.placeholders[1].text='Verification checks whether a model implementation matches its specification.\nValidation checks whether the model adequately represents the real system for its purpose.'
    presentation.save(target/'03-validation.pptx')
    (target/'04-probability.txt').write_text('Probability Basics\nA probability ranges from 0 to 1. The expected value of a fair six-sided die is 3.5. Independent events satisfy P(A and B) = P(A)P(B). A Bernoulli trial has two possible outcomes.',encoding='utf-8')
    (target/'05-networks.txt').write_text('Network Science\nA network is a set of nodes and edges. Degree counts the number of neighbors of a node. In a small-world network, most nodes are not direct neighbors but can be reached through a small number of hops. Network structure can influence diffusion between agents.',encoding='utf-8')
    return sorted(target.iterdir())

if __name__=='__main__':
    for p in make_documents():
        print(p.name)
