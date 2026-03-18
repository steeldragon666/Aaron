# AI Integration Research for OmniscientAI

## Key Findings

### 1. OpenAI Realtime API — Voice AI Agent
- OpenAI's Realtime API enables speech-to-speech interactions via WebRTC in the browser
- Uses the Agents SDK for TypeScript with RealtimeAgent and RealtimeSession
- Supports multimodal inputs (audio, images, text) and outputs (audio, text)
- Can be customised with specific instructions/persona
- Connection methods: WebRTC (browser), WebSocket (server), SIP (telephony)
- Requires API key (can use ephemeral keys for client-side)
- Use case: A live "Talk to our AI Consultant" voice agent on the website

### 2. AI-Powered Document/Data Analysis
- Multiple approaches: RAG chatbots, document Q&A, data visualisation
- OpenAI Vision API can analyse uploaded images/documents
- Vercel AI SDK provides useChat hook for streaming chatbot UI
- Replicate and Hugging Face offer embeddable model demos
- Use case: Upload a business document and get AI-powered insights

### 3. AI Image/Content Generation Playground
- Replicate API offers text-to-image (FLUX, Stable Diffusion)
- Black Forest Labs (FLUX) has state-of-the-art image generation
- Hugging Face Spaces can be embedded via iframe
- Use case: Interactive AI playground where visitors can try AI tools

### Industry Trends from Webstacks Research
- Dark mode with colorful backgrounds is standard for AI companies
- Product-led demos that let visitors try AI without converting are highly effective
- Interactive product demonstrations are the #1 differentiator
- Trust signals (logos, testimonials, G2 ratings) are critical
- Developer resources and educational content build authority
- Deepgram lets users try voice models directly on the website
- Cohere has motion backgrounds and unique navigation
- OpenAI showcases AI-generated artwork as marketing

### Technologies Available
- OpenAI Realtime API (voice agents, WebRTC)
- OpenAI Chat Completions API (text chat, vision)
- OpenAI Whisper (speech-to-text)
- Replicate API (image generation, video)
- Hugging Face Spaces (embeddable demos)
- Vercel AI SDK (streaming chat UI)
- NotebookLM Enterprise API (podcast generation)
- Google Gemini API (multimodal)

### Feasibility for OmniscientAI (Static Frontend)
- Need web-db-user upgrade for API proxying (hide API keys)
- OpenAI Realtime API needs ephemeral key generation (server-side)
- Simpler options: embed Hugging Face Spaces, client-side demos with user's own keys
- Best approach: upgrade to full-stack, add OpenRouter/OpenAI proxy
