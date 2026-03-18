import { z } from "zod";
import { COOKIE_NAME } from "@shared/const";
import { getSessionCookieOptions } from "./_core/cookies";
import { systemRouter } from "./_core/systemRouter";
import { publicProcedure, router } from "./_core/trpc";
import { invokeLLM } from "./_core/llm";
import { insertLead } from "./db";
import { notifyOwner } from "./_core/notification";

// ─── OmniscientAI system prompt for the Prompt Playground scoring ───
const PROMPT_SCORER_SYSTEM = `You are an expert prompt engineer. Score the given prompt on a scale of 1-10 across these dimensions:
- Clarity (is the instruction unambiguous?)
- Specificity (does it define scope, format, constraints?)
- Context (does it provide relevant background?)
- Structure (is it well-organised with clear sections?)
- Effectiveness (will it produce a high-quality response?)

Return a JSON object with: { scores: { clarity: number, specificity: number, context: number, structure: number, effectiveness: number }, overall: number, suggestions: string[] }
where suggestions is an array of 2-3 specific improvements. Be constructive and educational.`;

// ─── OmniscientAI Voice Consultant persona ───
const VOICE_CONSULTANT_SYSTEM = `You are the OmniscientAI Virtual Consultant — a knowledgeable, friendly AI assistant for OmniscientAI, Melbourne's leading vendor-neutral AI training and consulting company.

YOUR KNOWLEDGE:
- OmniscientAI offers three core workshops:
  1. "AI for Business Leaders" (half-day, $2,500-4,500) — strategic AI literacy for executives and decision-makers
  2. "Hands-On Prompt Engineering" (full-day, $3,000-5,500) — practical prompt crafting across ChatGPT, Claude, Gemini, Copilot
  3. "AI-Powered Workflows" (full-day, $3,500-6,000) — building automated workflows with AI tools
- Custom workshops available, tailored to any industry
- Services: AI Strategy Consulting, AI Implementation Support
- Industries served: Legal, Healthcare, Manufacturing, Professional Services, Retail, Construction
- Based in Melbourne, Australia. Serves SMEs (5-200 employees)
- Vendor-neutral approach — we teach ALL major AI platforms, not just one
- Founded by an experienced AI practitioner with deep technical and business expertise

YOUR BEHAVIOUR:
- Be warm, professional, and concise
- Ask qualifying questions: team size, industry, current AI usage, goals
- Recommend specific workshops based on their needs
- Mention the AI Readiness Quiz at /ai-readiness-quiz for self-assessment
- IMPORTANT: Actively cross-promote the other tools on the website:
  * "Have you tried our Prompt Engineering Playground? It's a free tool at /playground where you can experiment with different AI models side by side."
  * "Our Document Analyser at /document-analyser can scan your business documents and identify AI automation opportunities."
  * "Take our AI Readiness Quiz at /ai-readiness-quiz to get a personalised score."
- Always offer to help them book a free strategy session at /book
- Keep responses under 150 words for conversational flow`;

// ─── Document Analyser system prompt ───
const DOC_ANALYSER_SYSTEM = `You are an AI Business Document Analyst for OmniscientAI, Melbourne's leading AI training company. Analyse the provided document/text and produce a comprehensive assessment.

Your analysis MUST include:
1. DOCUMENT SUMMARY: Brief description of what the document contains
2. AI AUTOMATION OPPORTUNITIES: Identify 3-5 specific processes that could be automated with AI
3. SCORES (each 1-100):
   - automationPotential: How much of this work could be automated
   - dataMaturity: Quality and structure of data practices evident
   - processEfficiency: Current efficiency of workflows described
   - aiReadiness: Overall readiness to adopt AI tools
4. TIME SAVINGS: Estimated hours per week that could be saved
5. RECOMMENDED WORKSHOPS: Which OmniscientAI workshops would help most:
   - "ai-for-business-leaders" — if they need strategic understanding
   - "hands-on-prompt-engineering" — if they need practical AI skills
   - "ai-powered-workflows" — if they need automation implementation
6. KEY RECOMMENDATIONS: 3-4 actionable next steps

Return as JSON: { summary: string, opportunities: string[], scores: { automationPotential: number, dataMaturity: number, processEfficiency: number, aiReadiness: number }, timeSavingsHoursPerWeek: number, recommendedWorkshops: string[], recommendations: string[] }`;

export const appRouter = router({
  system: systemRouter,
  auth: router({
    me: publicProcedure.query(opts => opts.ctx.user),
    logout: publicProcedure.mutation(({ ctx }) => {
      const cookieOptions = getSessionCookieOptions(ctx.req);
      ctx.res.clearCookie(COOKIE_NAME, { ...cookieOptions, maxAge: -1 });
      return { success: true } as const;
    }),
  }),

  // ─── Lead Capture ───
  leads: router({
    capture: publicProcedure
      .input(
        z.object({
          email: z.string().email(),
          name: z.string().min(1),
          company: z.string().min(1),
          toolUsed: z.string().min(1),
        })
      )
      .mutation(async ({ input }) => {
        await insertLead(input);
        // Notify owner of new lead
        await notifyOwner({
          title: `New AI Tool Lead: ${input.name}`,
          content: `${input.name} from ${input.company} (${input.email}) accessed the ${input.toolUsed} tool.`,
        }).catch(() => {}); // Don't fail if notification fails
        return { success: true };
      }),
  }),

  // ─── Prompt Playground (open access) ───
  playground: router({
    chat: publicProcedure
      .input(
        z.object({
          messages: z.array(
            z.object({
              role: z.enum(["system", "user", "assistant"]),
              content: z.string(),
            })
          ),
        })
      )
      .mutation(async ({ input }) => {
        const result = await invokeLLM({
          messages: input.messages,
        });
        const content = result.choices[0]?.message?.content;
        return {
          content: typeof content === "string" ? content : JSON.stringify(content),
          model: result.model,
        };
      }),

    scorePrompt: publicProcedure
      .input(z.object({ prompt: z.string().min(1) }))
      .mutation(async ({ input }) => {
        const result = await invokeLLM({
          messages: [
            { role: "system", content: PROMPT_SCORER_SYSTEM },
            { role: "user", content: input.prompt },
          ],
          response_format: {
            type: "json_schema",
            json_schema: {
              name: "prompt_score",
              strict: true,
              schema: {
                type: "object",
                properties: {
                  scores: {
                    type: "object",
                    properties: {
                      clarity: { type: "number" },
                      specificity: { type: "number" },
                      context: { type: "number" },
                      structure: { type: "number" },
                      effectiveness: { type: "number" },
                    },
                    required: ["clarity", "specificity", "context", "structure", "effectiveness"],
                    additionalProperties: false,
                  },
                  overall: { type: "number" },
                  suggestions: { type: "array", items: { type: "string" } },
                },
                required: ["scores", "overall", "suggestions"],
                additionalProperties: false,
              },
            },
          },
        });
        const content = result.choices[0]?.message?.content;
        const text = typeof content === "string" ? content : JSON.stringify(content);
        return JSON.parse(text);
      }),
  }),

  // ─── Voice Consultant (uses chat, gated on frontend) ───
  voiceConsultant: router({
    chat: publicProcedure
      .input(
        z.object({
          messages: z.array(
            z.object({
              role: z.enum(["system", "user", "assistant"]),
              content: z.string(),
            })
          ),
        })
      )
      .mutation(async ({ input }) => {
        // Prepend the consultant persona if not already there
        const messages = input.messages[0]?.role === "system"
          ? input.messages
          : [{ role: "system" as const, content: VOICE_CONSULTANT_SYSTEM }, ...input.messages];

        const result = await invokeLLM({ messages });
        const content = result.choices[0]?.message?.content;
        return {
          content: typeof content === "string" ? content : JSON.stringify(content),
        };
      }),
  }),

  // ─── Document Analyser (gated on frontend) ───
  documentAnalyser: router({
    analyse: publicProcedure
      .input(
        z.object({
          documentText: z.string().min(10),
          fileName: z.string().optional(),
        })
      )
      .mutation(async ({ input }) => {
        const result = await invokeLLM({
          messages: [
            { role: "system", content: DOC_ANALYSER_SYSTEM },
            {
              role: "user",
              content: `Analyse this business document (${input.fileName || "uploaded document"}):\n\n${input.documentText}`,
            },
          ],
          response_format: {
            type: "json_schema",
            json_schema: {
              name: "document_analysis",
              strict: true,
              schema: {
                type: "object",
                properties: {
                  summary: { type: "string" },
                  opportunities: { type: "array", items: { type: "string" } },
                  scores: {
                    type: "object",
                    properties: {
                      automationPotential: { type: "number" },
                      dataMaturity: { type: "number" },
                      processEfficiency: { type: "number" },
                      aiReadiness: { type: "number" },
                    },
                    required: ["automationPotential", "dataMaturity", "processEfficiency", "aiReadiness"],
                    additionalProperties: false,
                  },
                  timeSavingsHoursPerWeek: { type: "number" },
                  recommendedWorkshops: { type: "array", items: { type: "string" } },
                  recommendations: { type: "array", items: { type: "string" } },
                },
                required: ["summary", "opportunities", "scores", "timeSavingsHoursPerWeek", "recommendedWorkshops", "recommendations"],
                additionalProperties: false,
              },
            },
          },
        });
        const content = result.choices[0]?.message?.content;
        const text = typeof content === "string" ? content : JSON.stringify(content);
        return JSON.parse(text);
      }),
  }),
});

export type AppRouter = typeof appRouter;
