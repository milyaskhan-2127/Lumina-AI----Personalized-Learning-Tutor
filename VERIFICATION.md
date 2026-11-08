# Lumina AI verification — November 8, 2026

## Automated results

- **Production frontend build:** passed (TypeScript and Vite).
- **Backend regression suite:** 8 passed. Covers math sandboxing, API and memory validation, private quiz keys, idempotent results, bounded retrieval refusal, NVIDIA rate-limit retry, empty streaming metadata events, server-timed focus completion, document-based quiz retrieval, and answer-format validation.
- **Mascot state tests:** passed for real-event transitions, priorities, task completion, global cursor normalization, and microphone/speech cleanup.
- **Robot workflow integration:** passed for PDF ingestion, a cited explanation, actual MCP quiz generation, and saved grading results.
- **Real integration demonstration:** 10 checks passed using isolated data, real NVIDIA responses and embeddings, actual MCP stdio processes, and a backend process restart.
- **Supplemental live checks:** 4 passed: MCP short-answer quiz/semantic grading, regeneration without duplicate turns, Roman Urdu personalization, MCP difficulty-memory write.
- **Local exposure checks:** frontend/backend respond; API.txt, .env and the SQLite path are blocked by the development server; foreign-origin mutations are blocked; the NVIDIA key is absent from the production assets.

Detailed machine-readable evidence:

- `output/live-033424c5/verification.json`
- `output/live-9231a8ca/verification.json`
- `output/live-bae013f6/verification.json`
- `output/live-9f827807/verification.json`

## Real-service evidence

The five-document run ingested PDF, DOCX, PPTX and two TXT files. A question across the selected collection retrieved the fictional Sable experiment on **PDF page 2**, and the answer correctly reported **37 agents with 12 energy units** using a real source reference. Retrieval worked again after restarting the test backend.

The calculator was discovered and invoked through MCP and returned **20** for `sqrt(144) + 2**3`. Quiz generation stored a private answer key, submission produced real feedback, and the agent used MCP to retrieve the saved progress. A fresh conversation after a process restart recalled the test student's explicitly saved name and robotics interest. Test preferences and scores were isolated from the actual workspace.

## Browser observations

- Desktop dashboard and tutor layouts inspected at 1440px.
- Mobile dashboard inspected around 445px; tutor and document selector inspected at 390px.
- A generated sample PDF uploaded through the actual browser file chooser and reached **Ready to explore** with two page-aware chunks.
- Browser chat answered the Sable question with **37**, **12**, and a clickable **page 2** reference.
- Mobile document-selection dialog displayed the selected lecture and working selection controls.
- Screenshots: `output/screenshots/tutor-citations.jpg`, `output/screenshots/mobile-documents.jpg`.
- Redesigned dashboard, expandable source evidence, real quiz celebration and MCP workflow screenshots: `docs/report-assets/`.
- Sidebar checked at 1440 × 640: its middle section scrolls while the profile stays within the viewport.
- A real one-minute focus session completed in the browser and saved 60 seconds in analytics.
- Word report includes the repository link, screenshots and architecture. Its final Word pagination review was interrupted by the user and remains unverified.

## Reproduce

Follow README setup instructions. Run `npm run build`, `.\.venv\Scripts\python.exe -m pytest -q`, then the live verification scripts. Live tests require valid NVIDIA access and use API credits. They reserve port 8002, store a new evidence folder, and stop only their own test process.

## Verification limits

This verifies the local single-student application, not a public multi-user deployment. Optional local embedding weights and OCR were not tested; OCR is not implemented. Source locations are validated against supplied fixtures; model answer quality and semantic grading still require normal human review. DOCX/TXT sources use section labels rather than invented page numbers.
