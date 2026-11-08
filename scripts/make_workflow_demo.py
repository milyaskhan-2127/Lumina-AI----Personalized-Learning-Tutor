from pathlib import Path
import pymupdf as fitz
root=Path(__file__).resolve().parent.parent
target=root/'examples'/'06-agent-workflows.pdf'
target.parent.mkdir(exist_ok=True)
doc=fitz.open()
p=doc.new_page()
p.insert_text((50,65),'Agent Workflows and Personalized Learning',fontsize=19,color=(.02,.22,.43))
p.insert_textbox(fitz.Rect(50,100,545,760),'''An agent workflow is the ordered process an intelligent agent follows to achieve a user's goal. A learning tutor can use a hybrid workflow with sequential steps, conditional routing, and a bounded retry.

1. Understand the student's request and identify the current learning goal.
2. Load short-term conversation context and relevant long-term student preferences.
3. Plan a suitable route. A general academic question can go directly to the language model. A question about uploaded course material should use retrieval-augmented generation (RAG).
4. Retrieve relevant document chunks using semantic embeddings and a vector database. Preserve page or slide metadata so the response can cite its evidence.
5. If the request needs a specialized action, use a tool. The Model Context Protocol (MCP) provides a standard client-server connection for discovering and calling tools such as quiz generation, safe calculation, and progress lookup.
6. Evaluate the available evidence or tool result. If retrieval is insufficient, reformulate the query and retry once. If evidence remains unavailable, explain that limitation instead of inventing a document answer.
7. Generate an explanation adapted to the student's saved level, preferred language, and learning goals. Stream the final response and show source references.
8. Save the conversation, explicit durable preferences, and real quiz results. Keep student memory separate from the document vector database.

Example: A student uploads lecture notes and asks, "Explain Agent Workflows." The tutor retrieves these notes, explains the steps with citations, and then invokes a real MCP quiz tool when the student requests practice. After submission, the application grades the answers, shows feedback, and stores the score in persistent memory.

Observable execution events describe actions such as memory loading, retrieval, and tool invocation. They are not private model reasoning and should never be fabricated.''',fontsize=11,color=(.12,.2,.28))
doc.save(target)
doc.close()
print(target.name)
