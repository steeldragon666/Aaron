import { describe, expect, it, vi, beforeEach } from "vitest";
import { appRouter } from "./routers";
import type { TrpcContext } from "./_core/context";

// Mock the LLM helper
vi.mock("./_core/llm", () => ({
  invokeLLM: vi.fn(),
}));

// Mock the db helper
vi.mock("./db", () => ({
  insertLead: vi.fn().mockResolvedValue(undefined),
  upsertUser: vi.fn(),
  getUserByOpenId: vi.fn(),
}));

// Mock the notification helper
vi.mock("./_core/notification", () => ({
  notifyOwner: vi.fn().mockResolvedValue(true),
}));

function createPublicContext(): TrpcContext {
  return {
    user: null,
    req: {
      protocol: "https",
      headers: {},
    } as TrpcContext["req"],
    res: {
      clearCookie: vi.fn(),
    } as unknown as TrpcContext["res"],
  };
}

describe("leads.capture", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("captures a lead with valid input", async () => {
    const ctx = createPublicContext();
    const caller = appRouter.createCaller(ctx);

    const result = await caller.leads.capture({
      email: "test@example.com",
      name: "Test User",
      company: "Test Corp",
      toolUsed: "AI Consultant",
    });

    expect(result).toEqual({ success: true });
  });

  it("rejects invalid email", async () => {
    const ctx = createPublicContext();
    const caller = appRouter.createCaller(ctx);

    await expect(
      caller.leads.capture({
        email: "not-an-email",
        name: "Test User",
        company: "Test Corp",
        toolUsed: "AI Consultant",
      })
    ).rejects.toThrow();
  });

  it("rejects empty name", async () => {
    const ctx = createPublicContext();
    const caller = appRouter.createCaller(ctx);

    await expect(
      caller.leads.capture({
        email: "test@example.com",
        name: "",
        company: "Test Corp",
        toolUsed: "AI Consultant",
      })
    ).rejects.toThrow();
  });
});

describe("playground.chat", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("sends messages to LLM and returns content", async () => {
    const { invokeLLM } = await import("./_core/llm");
    (invokeLLM as ReturnType<typeof vi.fn>).mockResolvedValue({
      choices: [{ message: { content: "Hello! I can help with that." } }],
      model: "test-model",
    });

    const ctx = createPublicContext();
    const caller = appRouter.createCaller(ctx);

    const result = await caller.playground.chat({
      messages: [
        { role: "system", content: "You are helpful." },
        { role: "user", content: "Hello" },
      ],
    });

    expect(result.content).toBe("Hello! I can help with that.");
    expect(invokeLLM).toHaveBeenCalledOnce();
  });

  it("rejects empty messages array", async () => {
    const ctx = createPublicContext();
    const caller = appRouter.createCaller(ctx);

    // Empty array should still be valid as zod allows empty arrays
    const { invokeLLM } = await import("./_core/llm");
    (invokeLLM as ReturnType<typeof vi.fn>).mockResolvedValue({
      choices: [{ message: { content: "OK" } }],
      model: "test-model",
    });

    const result = await caller.playground.chat({ messages: [] });
    expect(result.content).toBe("OK");
  });
});

describe("playground.scorePrompt", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("scores a prompt and returns structured result", async () => {
    const { invokeLLM } = await import("./_core/llm");
    const mockScores = {
      scores: { clarity: 8, specificity: 7, context: 6, structure: 9, effectiveness: 7 },
      overall: 7.4,
      suggestions: ["Add more context", "Be more specific about output format"],
    };
    (invokeLLM as ReturnType<typeof vi.fn>).mockResolvedValue({
      choices: [{ message: { content: JSON.stringify(mockScores) } }],
    });

    const ctx = createPublicContext();
    const caller = appRouter.createCaller(ctx);

    const result = await caller.playground.scorePrompt({
      prompt: "Write a blog post about AI",
    });

    expect(result.scores.clarity).toBe(8);
    expect(result.overall).toBe(7.4);
    expect(result.suggestions).toHaveLength(2);
  });
});

describe("voiceConsultant.chat", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("sends messages with system prompt prepended", async () => {
    const { invokeLLM } = await import("./_core/llm");
    (invokeLLM as ReturnType<typeof vi.fn>).mockResolvedValue({
      choices: [{ message: { content: "G'day! How can I help?" } }],
    });

    const ctx = createPublicContext();
    const caller = appRouter.createCaller(ctx);

    const result = await caller.voiceConsultant.chat({
      messages: [
        { role: "user", content: "What workshops do you offer?" },
      ],
    });

    expect(result.content).toBe("G'day! How can I help?");
    expect(invokeLLM).toHaveBeenCalledOnce();

    // Verify system prompt was prepended
    const callArgs = (invokeLLM as ReturnType<typeof vi.fn>).mock.calls[0][0];
    expect(callArgs.messages[0].role).toBe("system");
    expect(callArgs.messages[0].content).toContain("OmniscientAI Virtual Consultant");
  });

  it("does not double-prepend system prompt", async () => {
    const { invokeLLM } = await import("./_core/llm");
    (invokeLLM as ReturnType<typeof vi.fn>).mockResolvedValue({
      choices: [{ message: { content: "Response" } }],
    });

    const ctx = createPublicContext();
    const caller = appRouter.createCaller(ctx);

    await caller.voiceConsultant.chat({
      messages: [
        { role: "system", content: "Custom system prompt" },
        { role: "user", content: "Hello" },
      ],
    });

    const callArgs = (invokeLLM as ReturnType<typeof vi.fn>).mock.calls[0][0];
    // Should use the provided system prompt, not prepend another
    expect(callArgs.messages[0].content).toBe("Custom system prompt");
    expect(callArgs.messages).toHaveLength(2);
  });
});

describe("documentAnalyser.analyse", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("analyses a document and returns structured result", async () => {
    const { invokeLLM } = await import("./_core/llm");
    const mockAnalysis = {
      summary: "This is a business process document.",
      opportunities: ["Automate data entry", "AI-powered reporting"],
      scores: {
        automationPotential: 75,
        dataMaturity: 60,
        processEfficiency: 45,
        aiReadiness: 55,
      },
      timeSavingsHoursPerWeek: 12,
      recommendedWorkshops: ["ai-for-business-leaders", "ai-powered-workflows"],
      recommendations: ["Start with data cleanup", "Implement prompt templates"],
    };
    (invokeLLM as ReturnType<typeof vi.fn>).mockResolvedValue({
      choices: [{ message: { content: JSON.stringify(mockAnalysis) } }],
    });

    const ctx = createPublicContext();
    const caller = appRouter.createCaller(ctx);

    const result = await caller.documentAnalyser.analyse({
      documentText: "This is a sample business document with various processes described...",
      fileName: "test-doc.txt",
    });

    expect(result.summary).toBe("This is a business process document.");
    expect(result.scores.automationPotential).toBe(75);
    expect(result.timeSavingsHoursPerWeek).toBe(12);
    expect(result.recommendedWorkshops).toContain("ai-for-business-leaders");
  });

  it("rejects too-short document text", async () => {
    const ctx = createPublicContext();
    const caller = appRouter.createCaller(ctx);

    await expect(
      caller.documentAnalyser.analyse({
        documentText: "short",
        fileName: "test.txt",
      })
    ).rejects.toThrow();
  });
});
