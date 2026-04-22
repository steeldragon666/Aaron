/**
 * AIReadinessQuiz.tsx — v2 AI Readiness quiz wizard (/ai-readiness-quiz).
 *
 * Multi-step wizard ported from legacy client/src/pages/AIReadinessQuiz.tsx.
 * Same question set and scoring math, rebuilt with v2 primitives (RadioCard,
 * Card, Button-styled anchors) and semantic tone accents.
 *
 *   Layout → (step 'intro')     → HeroCentric + Start CTA
 *          → (step 'questions') → Progress bar + MonoBadge + H2 question +
 *                                 RadioCard stack + Back / Next nav
 *          → (step 'result')    → HeroCentric with score + interpretation +
 *                                 StatsRow category breakdown + recommendations
 *                                 + CTAStrip → /book
 *
 * Scoring: each of the 10 questions exposes four options worth 1-4 points
 * (from QUIZ_QUESTIONS in lib/data.ts). We compute total / 40 as a 0-100
 * score and bucket into three tiers: 0-40 "Just starting", 41-70 "Solid
 * foundation", 71-100 "AI-ready". Category breakdown mirrors the legacy
 * radar chart — percent-of-max per category.
 *
 * Product UI, not marketing — semantic accents (--success on AI-ready tier)
 * and dot-grid backgrounds are allowed.
 *
 * TODO: copy drafted 2026-04-22 — founder to validate tier descriptions and
 * recommendation bullets.
 */

import { useState, useMemo, type ReactNode } from 'react';
import SEO from '@/components/SEO';
import { Layout } from '@/components-v2/layout';
import { HeroCentric, StatsRow, CTAStrip } from '@/components-v2/sections';
import {
  Card,
  Display,
  Eyebrow,
  Lede,
  MonoBadge,
  RadioCard,
} from '@/components-v2/ui';
import { cn } from '@/lib/utils';
import { QUIZ_QUESTIONS } from '@/lib/data';

type Step = 'intro' | 'questions' | 'result';

// Shared button style — matches Button primary+lg used elsewhere.
const buttonBase =
  'inline-flex items-center gap-2 font-semibold rounded-md ' +
  'px-[22px] py-[14px] text-[15px] ' +
  'transition-[transform,background-color,filter] duration-[180ms] ' +
  'ease-[cubic-bezier(0.2,0.9,0.2,1)] ' +
  'hover:-translate-y-px active:translate-y-0 active:brightness-[.96] ' +
  'disabled:opacity-40 disabled:cursor-not-allowed disabled:hover:translate-y-0 ' +
  'focus-visible:outline-2 focus-visible:outline-blue-glow focus-visible:outline-offset-2 ' +
  'cursor-pointer';
const primaryBtn = cn(buttonBase, 'bg-blue text-paper border-0 hover:bg-blue-deep');
const secondaryBtn = cn(
  buttonBase,
  'bg-paper text-ink border-[1.5px] border-ink hover:bg-paper-2',
);

// Max possible score: 10 questions × 4 points = 40. Normalised to /100 for
// the three-tier interpretation.
const MAX_POINTS = QUIZ_QUESTIONS.length * 4;

interface Tier {
  label: string;
  description: string;
  // CSS variable name for the semantic accent. --warn / --blue / --success
  // are all valid tokens inside the .v2 scope.
  colorVar: string;
}

// TODO: founder to validate tier copy — drafted 2026-04-22.
function getTier(score100: number): Tier {
  if (score100 <= 40) {
    return {
      label: 'Just starting',
      description:
        "Your organisation is at the start of its AI journey. Build data foundations and team awareness before investing in tools. The good news: the biggest wins often come from the first 20% of the work.",
      colorVar: 'var(--warn)',
    };
  }
  if (score100 <= 70) {
    return {
      label: 'Solid foundation',
      description:
        "Your organisation has solid foundations for AI adoption. Focus on identifying two or three high-impact use cases and building internal capability around them — don't spread thin.",
      colorVar: 'var(--blue)',
    };
  }
  return {
    label: 'AI-ready',
    description:
      'Your organisation is well-positioned for advanced AI initiatives. Focus on scaling successful pilots, building governance frameworks, and developing internal champions.',
    colorVar: 'var(--success)',
  };
}

// TODO: founder to validate — drafted 2026-04-22.
function getRecommendations(score100: number): string[] {
  if (score100 <= 40) {
    return [
      'Audit your data — where it lives, who owns it, what shape it\'s in. You can\'t automate what you can\'t see.',
      'Run a 90-minute "AI for Business Leaders" workshop with your exec team to establish a shared vocabulary.',
      'Pick one department, one process, one pilot. Keep scope tight and ship something measurable in a quarter.',
      'Establish baseline privacy and data-handling policies — generic ones are fine to start, refine later.',
    ];
  }
  if (score100 <= 70) {
    return [
      'Build a prioritised backlog of AI opportunities with rough business cases — not all ideas are equal.',
      'Upskill two or three internal champions who can own the work after consultants leave.',
      'Run a Microsoft Copilot Masterclass or equivalent to convert curiosity into practical daily use.',
      'Formalise an AI governance framework — proportionate to your scale, not enterprise-grade by default.',
      'Measure everything from day one. Shipping is easy; knowing what worked is the hard part.',
    ];
  }
  return [
    'Scale your successful pilots — identify what patterns transferred and productionise the supporting infrastructure.',
    'Run an AI Governance Essentials workshop to lock down policies before they become audit findings.',
    'Invest in eval harnesses and monitoring — production AI is an operations problem, not a modelling one.',
    'Consider custom agents or retrieval-augmented systems for domain-specific workflows your team has earned the right to build.',
  ];
}

// Category breakdown — percent-of-max per category. Used in the StatsRow
// on the result screen so the user sees where their strengths vs gaps are.
interface CategoryScore {
  category: string;
  score: number; // 0-100
}

function computeCategoryScores(
  answers: Record<number, number>,
): CategoryScore[] {
  const cats: Record<string, { total: number; count: number }> = {};
  QUIZ_QUESTIONS.forEach((q) => {
    if (!cats[q.category]) cats[q.category] = { total: 0, count: 0 };
    cats[q.category].count += 1;
    if (answers[q.id] !== undefined) {
      cats[q.category].total += answers[q.id];
    }
  });
  return Object.entries(cats).map(([category, { total, count }]) => ({
    category,
    score: Math.round((total / (count * 4)) * 100),
  }));
}

export default function AIReadinessQuiz() {
  const [step, setStep] = useState<Step>('intro');
  const [currentQ, setCurrentQ] = useState(0);
  // answers keyed by question id (not index) — matches legacy shape.
  // Value is the selected option's score (1-4).
  const [answers, setAnswers] = useState<Record<number, number>>({});

  const totalQuestions = QUIZ_QUESTIONS.length;
  const question = QUIZ_QUESTIONS[currentQ];
  const currentAnswer = answers[question?.id];
  const hasSelection = currentAnswer !== undefined;
  const isLastQuestion = currentQ === totalQuestions - 1;
  const progressPercent = ((currentQ + 1) / totalQuestions) * 100;

  // Total score out of 40, normalised to a 0-100 display score.
  const totalPoints = useMemo(
    () => Object.values(answers).reduce((a, b) => a + b, 0),
    [answers],
  );
  const score100 = Math.round((totalPoints / MAX_POINTS) * 100);
  const tier = getTier(score100);
  const recommendations = getRecommendations(score100);
  const categoryScores = useMemo(() => computeCategoryScores(answers), [answers]);

  const handleStart = () => {
    setStep('questions');
    setCurrentQ(0);
  };

  const handleSelect = (value: string) => {
    const scoreValue = Number(value);
    setAnswers((prev) => ({ ...prev, [question.id]: scoreValue }));
  };

  const handleNext = () => {
    if (!hasSelection) return;
    if (isLastQuestion) {
      setStep('result');
      return;
    }
    setCurrentQ((q) => q + 1);
  };

  const handleBack = () => {
    if (currentQ === 0) return;
    setCurrentQ((q) => q - 1);
  };

  let body: ReactNode;

  if (step === 'intro') {
    body = (
      <>
        <HeroCentric
          eyebrow="Assessment"
          title="AI Readiness Quiz"
          lede="Ten questions, five minutes. A quick diagnostic of where your organisation sits on the AI adoption curve — data, team, process, strategy, infrastructure."
        />
        <section className="pb-16 lg:pb-24">
          <div className="max-w-[1200px] mx-auto px-6 lg:px-8">
            <div className="flex justify-center">
              <button
                type="button"
                onClick={handleStart}
                className={primaryBtn}
                data-testid="start-quiz"
              >
                Start assessment <span aria-hidden>→</span>
              </button>
            </div>
          </div>
        </section>
      </>
    );
  } else if (step === 'questions') {
    body = (
      <section className="py-16 lg:py-24">
        <div className="max-w-[1200px] mx-auto px-6 lg:px-8">
          <div className="mx-auto max-w-2xl">
            {/* Progress bar — thin, --blue fill on --line track. */}
            <div
              className="mb-8 h-1 w-full rounded-full bg-line overflow-hidden"
              role="progressbar"
              aria-valuenow={currentQ + 1}
              aria-valuemin={1}
              aria-valuemax={totalQuestions}
              aria-label="Quiz progress"
            >
              <div
                className="h-full bg-blue transition-all duration-[300ms] ease-[cubic-bezier(0.2,0.9,0.2,1)]"
                style={{ width: `${progressPercent}%` }}
              />
            </div>

            <div className="mb-5 flex items-center gap-3 flex-wrap">
              <MonoBadge>
                Question {currentQ + 1} of {totalQuestions}
              </MonoBadge>
              <MonoBadge>{question.category}</MonoBadge>
            </div>

            <h2 className="font-semibold text-[26px] leading-tight text-ink mb-6">
              {question.question}
            </h2>

            {/* RadioCard options — vertical stack with 12px gap. */}
            <div className="flex flex-col gap-3">
              {question.options.map((opt) => {
                const value = String(opt.score);
                return (
                  <RadioCard
                    key={`${question.id}-${opt.score}-${opt.label}`}
                    name={`question-${question.id}`}
                    value={value}
                    label={opt.label}
                    checked={currentAnswer === opt.score}
                    onChange={handleSelect}
                  />
                );
              })}
            </div>

            {/* Navigation — Back (disabled on Q1) / Next (disabled until
                a selection is made). */}
            <div className="mt-8 flex items-center justify-between gap-4">
              <button
                type="button"
                onClick={handleBack}
                disabled={currentQ === 0}
                className={secondaryBtn}
                data-testid="back-button"
              >
                <span aria-hidden>←</span> Back
              </button>
              <button
                type="button"
                onClick={handleNext}
                disabled={!hasSelection}
                className={primaryBtn}
                data-testid="next-button"
              >
                {isLastQuestion ? 'See results' : 'Next'} <span aria-hidden>→</span>
              </button>
            </div>
          </div>
        </div>
      </section>
    );
  } else {
    // step === 'result'
    body = (
      <>
        <section className="py-16 lg:py-24 text-center">
          <div className="max-w-[1200px] mx-auto px-6 lg:px-8">
            <Eyebrow className="mb-5 block">Result</Eyebrow>
            <div
              className="font-mono font-bold text-[80px] lg:text-[120px] leading-none tracking-[-0.02em]"
              style={{ color: tier.colorVar, fontFamily: 'var(--font-mono)' }}
              data-testid="result-score"
            >
              {score100}
              <span className="text-ink-3 text-[48px] lg:text-[72px]">/100</span>
            </div>
            <Display as="h1" className="mt-6 max-w-3xl mx-auto">
              {tier.label}
            </Display>
            <Lede className="mt-6 max-w-2xl mx-auto">{tier.description}</Lede>
          </div>
        </section>

        <StatsRow
          eyebrow="Where you sit"
          sectionTitle="Category breakdown"
          tone="paper-2"
          stats={categoryScores.map((c) => ({
            value: `${c.score}%`,
            label: c.category,
          }))}
        />

        <section className="py-16 lg:py-24">
          <div className="max-w-[1200px] mx-auto px-6 lg:px-8">
            <div className="mx-auto max-w-2xl">
              <Eyebrow className="mb-3 block">Recommended next steps</Eyebrow>
              <h2 className="font-semibold text-[28px] leading-tight text-ink mb-6">
                What to do with this score.
              </h2>
              <Card tone="paper-2">
                <ul className="flex flex-col gap-4">
                  {recommendations.map((rec) => (
                    <li
                      key={rec}
                      className="flex gap-3 text-ink-2 leading-relaxed"
                    >
                      <span aria-hidden className="text-blue font-bold mt-0.5">
                        →
                      </span>
                      <span>{rec}</span>
                    </li>
                  ))}
                </ul>
              </Card>
            </div>
          </div>
        </section>

        <CTAStrip
          tone="ink"
          title="Want a real assessment?"
          lede="A 5-minute quiz is a starting point. A diagnostic call is 20 minutes with a practitioner who can interpret your answers against real engagements we've run."
          primaryCta={{ label: 'Book a diagnostic call', href: '/book' }}
        />
      </>
    );
  }

  return (
    <Layout>
      <SEO
        title="AI Readiness Quiz"
        description="Ten questions, five minutes. A quick diagnostic of where your organisation sits on the AI adoption curve."
      />
      {body}
    </Layout>
  );
}
