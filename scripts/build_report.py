from pathlib import Path
from PIL import Image
from docx import Document
from docx.shared import Inches,Pt,RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

ROOT=Path(__file__).resolve().parents[1];ASSETS=ROOT/'docs'/'report-assets';OUT=ROOT/'docs'/'report';OUT.mkdir(parents=True,exist_ok=True)
doc=Document();section=doc.sections[0]
section.page_width=Inches(8.27);section.page_height=Inches(11.69)
section.top_margin=Inches(.62);section.bottom_margin=Inches(.58);section.left_margin=Inches(.68);section.right_margin=Inches(.68)
section.header_distance=Inches(.22);section.footer_distance=Inches(.23)
for name in ['Normal','Title','Subtitle','Heading 1','Heading 2','Heading 3','Caption']:
 st=doc.styles[name];st.font.name='Calibri';st.font.color.rgb=RGBColor(0,0,0)
 st.paragraph_format.space_after=Pt(6)
doc.styles['Normal'].font.size=Pt(10.5);doc.styles['Normal'].paragraph_format.line_spacing=1.1
doc.styles['Title'].font.size=Pt(25);doc.styles['Title'].font.bold=True
doc.styles['Subtitle'].font.size=Pt(12)
for name,size in [('Heading 1',17),('Heading 2',12),('Heading 3',11)]:
 doc.styles[name].font.size=Pt(size);doc.styles[name].font.bold=True
 doc.styles[name].paragraph_format.space_before=Pt(10);doc.styles[name].paragraph_format.space_after=Pt(6)
doc.styles['Caption'].font.size=Pt(9);doc.styles['Caption'].font.italic=True;doc.styles['Caption'].font.color.rgb=RGBColor.from_string('526777')
doc.core_properties.title='Lumina AI Personalized Learning Tutor Project Report'
doc.core_properties.subject='Features technology architecture and verified learning workflow'
doc.core_properties.author=''
doc.core_properties.keywords='Lumina AI, Agent Based Modeling, LangGraph, RAG, MCP, 3D robot'

def para(text='',boldlead=None):
 p=doc.add_paragraph()
 if boldlead and text.startswith(boldlead):p.add_run(boldlead).bold=True;p.add_run(text[len(boldlead):])
 else:p.add_run(text)
 return p
def heading(text):doc.add_heading(text,1)
def sub(text):doc.add_heading(text,2)
def image(name,caption,width=6.86):
 path=ASSETS/name if isinstance(name,str) else name
 with Image.open(path) as asset:
  width=min(width,3.45*asset.width/asset.height)
 p=doc.add_paragraph();p.paragraph_format.space_before=Pt(5);p.paragraph_format.space_after=Pt(3)
 p.alignment=WD_ALIGN_PARAGRAPH.CENTER
 p.paragraph_format.keep_with_next=True
 shape=p.add_run().add_picture(str(path),width=Inches(width));shape._inline.docPr.set('descr',caption)
 p=doc.add_paragraph(caption,'Caption');p.paragraph_format.space_after=Pt(8)
def bullet(lead,text):
 p=doc.add_paragraph(style='List Bullet');p.paragraph_format.space_after=Pt(5);p.paragraph_format.line_spacing=1.06
 p.add_run(lead+' ').bold=True;p.add_run(text)
def table(headers,rows,widths):
 t=doc.add_table(rows=1,cols=len(headers));t.autofit=False
 for i,w in enumerate(widths):t.columns[i].width=Inches(w)
 for cell,title,w in zip(t.rows[0].cells,headers,widths):
  cell.width=Inches(w);cell.text=title
  shading=OxmlElement('w:shd');shading.set(qn('w:fill'),'DDEFFC');cell._tc.get_or_add_tcPr().append(shading)
  for r in cell.paragraphs[0].runs:r.bold=True
 repeat=OxmlElement('w:tblHeader');t.rows[0]._tr.get_or_add_trPr().append(repeat)
 for n,row in enumerate(rows):
  cells=t.add_row().cells
  for i,(cell,value,w) in enumerate(zip(cells,row,widths)):
   cell.width=Inches(w);cell.text=value
   if n%2==1:
    shade=OxmlElement('w:shd');shade.set(qn('w:fill'),'F4F9FC');cell._tc.get_or_add_tcPr().append(shade)
 for row in t.rows:
  trpr=row._tr.get_or_add_trPr();cant=OxmlElement('w:cantSplit');trpr.append(cant)
  for cell in row.cells:
   cell.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
   tcpr=cell._tc.get_or_add_tcPr();borders=OxmlElement('w:tcBorders')
   for side in ['top','left','bottom','right']:
    edge=OxmlElement('w:'+side);edge.set(qn('w:val'),'single');edge.set(qn('w:sz'),'4');edge.set(qn('w:color'),'D9D9D9');borders.append(edge)
   tcpr.append(borders);margins=OxmlElement('w:tcMar')
   for side in ['top','left','bottom','right']:
    m=OxmlElement('w:'+side);m.set(qn('w:w'),'75' if side in ['top','bottom'] else '100');m.set(qn('w:type'),'dxa');margins.append(m)
   tcpr.append(margins)
   for p in cell.paragraphs:
    p.paragraph_format.space_after=Pt(0);p.paragraph_format.line_spacing=1.04
    for r in p.runs:r.font.size=Pt(9);r.font.color.rgb=RGBColor(0,0,0)
 return t
def new_page():doc.add_page_break()

doc.add_paragraph('Lumina AI Personalized Learning Tutor','Title')
doc.add_paragraph('Agent Based Modeling Project Report','Subtitle')
para('This report explains the features, technologies and complete learning workflow of Lumina AI, a local personalized tutor with document knowledge, quizzes and an interactive 3D robot. A LangGraph agent combines NVIDIA models, persistent memory and real MCP tools to teach from course material and save progress. The screenshots show actual application activity.')
p=para('Source code  ')
link=OxmlElement('w:hyperlink');link.set(qn('r:id'),p.part.relate_to('https://github.com/milyaskhan-2127/Lumina-AI----Personalized-Learning-Tutor','http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink',is_external=True))
run=OxmlElement('w:r');props=OxmlElement('w:rPr');color=OxmlElement('w:color');color.set(qn('w:val'),'0074B8');props.append(color);run.append(props);label=OxmlElement('w:t');label.text='Lumina AI GitHub repository';run.append(label);link.append(run);p._p.append(link)
image('dashboard.jpg','Figure 1  The redesigned learning dashboard with a live 3D robot and statistics from saved activity.')
sub('Application features')
bullet('Dashboard','Shows actual documents, practiced topics, quiz results, streaks and completed focus time, with a learning path and quick actions.')
bullet('AI Tutor and Library','Provides streaming chat, saved conversations, Markdown, equations and expandable citations. PDF, DOCX, PPTX and TXT files can be uploaded, searched, previewed or deleted.')
bullet('Quiz Studio and Analytics','Creates MCQ or short-answer practice, checks submissions, explains answers and displays persistent performance and weak topics.')
bullet('Profile and Agent Insights','Allows preferences and memories to be edited or forgotten. Clickable workflow nodes show recorded routing, retrieval and MCP activity.')

new_page();heading('System architecture and technologies')
para('The frontend sends local API requests to FastAPI. The agent chooses a general answer, document retrieval or an educational tool. Its observable events drive the robot, while SQLite and ChromaDB preserve separate kinds of knowledge.')
image(ROOT/'docs'/'assets'/'architecture.png','Figure 2  The same architecture is included as an image and Mermaid diagram in the README.')
table(['Layer','Technology','Role'],[
 ('Interface','React, Vite, TypeScript, Tailwind','Reusable pages, typed interactions and responsive glass styling.'),
 ('Interaction','Framer Motion, Recharts','Transitions, card effects, animated counters and real score charts.'),
 ('Robot','Three.js, React Three Fiber, Drei','Custom 3D geometry with separately animated head, eyes, arms and book.'),
 ('Robot state','Zustand, Canvas Confetti','Priority-based task states and celebrations for real achievements.'),
 ('Backend','FastAPI, Pydantic, Uvicorn','Validated local endpoints, uploads and streaming responses.'),
 ('Agent and models','LangGraph, NVIDIA, HTTPX','Conditional orchestration, live LLM responses and semantic embeddings.'),
 ('Document extraction','PyMuPDF, python-docx, python-pptx','Extract text and retain PDF page or presentation slide locations.'),
 ('Knowledge and memory','ChromaDB, SQLite','Semantic document search; persistent profiles, chats, scores and focus sessions.'),
 ('Tool protocol','Official Python MCP SDK, FastMCP','Real stdio tool discovery, invocation and results.'),
 ('Optional voice','Browser Web Speech APIs','Speech recognition and read-aloud with available browser voices.')
],[1.06,2.14,3.66])

new_page();heading('How the tutor and document knowledge work')
image('rag-chat.jpg','Figure 3  A live document-grounded explanation with an expandable reference to the uploaded lecture.')
sub('From question to explanation')
para('The request enters FastAPI, which restores recent conversation turns and the saved student profile. LangGraph asks the LLM to select a route. General questions use model knowledge; selected-document questions use semantic retrieval; quizzes, calculations and progress queries use MCP tools. The final explanation streams into the chat and is saved with its source metadata.')
sub('The RAG pipeline')
para('Upload and validate -> extract text -> create overlapping chunks -> embed passages -> store in ChromaDB -> embed the question -> retrieve relevant excerpts -> answer with citations. The agent filters low-relevance results and can reformulate once. If evidence is still unavailable, it explains the limitation instead of inventing an answer. PDF pages and PPTX slides are preserved; DOCX and TXT use section labels.')
sub('Three distinct memory concepts')
bullet('Agent state','The current goal, route, retrieved evidence, tool result and response exist within the LangGraph run.')
bullet('Short term memory','Up to 16 recent messages from the selected conversation resolve follow-ups such as “make it easier.”')
bullet('Long term memory','SQLite stores explicit student preferences, conversations, quiz results and completed focus time across new sessions and backend restarts. Chroma document knowledge stays separate.')
para('The system prompt contains the requested 12 teaching rules: use the saved name, interests, level, goals and language; apply RAG and truthful citations; use both memory types and MCP; teach with simple examples; ask when clarification is needed; never fabricate facts or sources.')

new_page();heading('How the robot and practice tools work')
image('robot-quiz.jpg','Figure 4  The robot companion works alongside the actual quiz and learning workflow.')
para('The robot is an original Three.js model assembled from primitives. Its head, LED eyes, arms, chest light and holographic book move independently. The eyes and head follow the cursor across the whole application viewport with smooth, bounded movement. Blinking, waving and hover reactions run alongside task states. The generated robot illustration is the explicit lightweight fallback.')
table(['Real trigger','Robot response'],[
 ('Document request is processing','Reading pose, opening holographic book and actual transfer or indexing status.'),
 ('Agent planning or retrieving evidence','Thinking expression and task-specific status.'),
 ('Final explanation is streaming','Teaching gestures while the text appears.'),
 ('Microphone or speech playback is active','Listening or talking only while the browser feature is active.'),
 ('Quiz result is returned and saved','Celebrate a strong score; encourage the learner after weaker results.'),
 ('Request fails','Show the actual error and allow retry; hover cannot hide an important task state.')
],[2.85,4.01])
sub('Practice voice and focus controls')
para('Quiz requests run through an actual MCP client and server. Answer keys stay in the backend; MCQs use deterministic grading and short answers use semantic LLM grading. Results update analytics and weak topics. Teach Me requests a level-appropriate lesson with examples and an understanding check, using selected documents when supplied.')
para('The floating companion shares the tutor conversation. Optional browser recognition places speech into editable text; read-aloud offers play, pause, stop, speed and voice controls. Browser support and permission determine availability. Speaking motion is approximate, not audio-amplitude analysis. The focus timer supports start, pause, resume and reset; the server counts only genuinely completed intervals toward saved learning time.')

new_page();heading('Demonstration and verification')
image('agent-insights.jpg','Figure 5  Recorded backend events can be inspected by run and workflow stage.')
sub('Recommended university demonstration')
for i,(lead,body) in enumerate([
 ('Personalize the tutor','Save a name, field, learning level and preferred language in Profile and Memory.'),
 ('Upload the lecture','Use examples/06-agent-workflows.pdf. The robot reads while extraction, embedding and indexing actually run.'),
 ('Ask for an explanation','Select the document and ask “Explain Agent Workflows.” Show the retrieved answer and original page reference.'),
 ('Request a quiz','Ask the agent to generate an easy three-question MCQ quiz. Show the actual MCP invocation in Agent Insights.'),
 ('Answer and inspect progress','Open Quiz Studio, submit answers, inspect explanations and watch genuine achievement feedback. Show the saved score in Analytics.'),
 ('Prove persistent memory','Restart the backend and start a new chat. Ask for the saved name and field; documents, preferences and results remain available.'),
 ('Show optional interactions','Open the floating companion, Teach Me, browser voice controls or the one-minute focus demonstration.')],1):
 p=para();p.paragraph_format.space_after=Pt(5);p.add_run(f'{i}. {lead}. ').bold=True;p.add_run(body)
sub('Verified behavior')
para('The production frontend build and eight Python regression tests passed. Real integration checks covered five-document ingestion, correct page citations, multi-turn context, MCP calculation and quizzes, saved progress, and name and field recall after a backend restart. Mascot state tests verified task priorities, completion, errors and microphone or speech cleanup. A real one-minute focus session completed and appeared in learning-time statistics.')
para('The application runs at http://localhost:5173 with FastAPI at http://localhost:8000. Run setup.cmd once, keep the NVIDIA key in API.txt or the backend environment, then use start.cmd. Credentials are not included in React or the production bundle. This is a local single-student project; OCR and public multi-user authentication are outside its current scope. Voice capture and audio playback depend on the browser and were not used as evidence for the text-model connection.')

footer=section.footer.paragraphs[0];footer.alignment=WD_ALIGN_PARAGRAPH.RIGHT
r=footer.add_run('Lumina AI  |  ');r.font.size=Pt(8);r.font.color.rgb=RGBColor.from_string('6C7B86')
field=OxmlElement('w:fldSimple');field.set(qn('w:instr'),'PAGE');footer._p.append(field)
target=OUT/'Lumina_AI_Project_Report.docx';doc.save(target)
print(target)
