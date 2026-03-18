# AI Integrations TODO

## Infrastructure
- [x] Upgrade to web-db-user (full-stack)
- [x] Create leads DB table (email, name, company, toolUsed, timestamp)
- [x] Create lead capture tRPC procedure
- [x] Build shared LeadGate component (email/name/company form)

## Prompt Engineering Playground (open access)
- [x] Create /playground route and page
- [x] Build split-pane UI (prompt editor left, response right)
- [x] Add model selector (GPT-4o, Claude, Gemini via built-in LLM)
- [x] Implement streaming responses via tRPC
- [x] Add pre-loaded prompt templates by category
- [x] Add "Prompt Score" feature
- [x] Add to navigation

## Live AI Voice Consultant (email-gated)
- [x] Create /voice-consultant route and page
- [x] Implement lead gate (email/name/company required before access)
- [x] Build streaming chat-based voice consultant using invokeLLM
- [x] Configure AI persona with OmniscientAI knowledge + cross-promote other tools
- [x] Build voice-style UI with animated visualisation
- [x] Voice agent instructs users to try Playground and Document Analyser

## AI Document Analyser (email-gated)
- [x] Create /document-analyser route and page
- [x] Implement lead gate (email/name/company required before access)
- [x] Build drag-and-drop file upload UI
- [x] Implement backend document processing via invokeLLM with vision
- [x] Build animated results dashboard with scores
- [x] Add workshop recommendation mapping

## Polish
- [x] Add "AI Tools" dropdown to navbar with all 5 tools
- [x] Write vitest tests for all server routes (11 tests passing)
- [x] Owner notification on new lead capture
- [x] TypeScript clean build (zero errors)
