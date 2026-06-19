export const maxDuration = 60;
export const dynamic = "force-dynamic";

// ─── Types ────────────────────────────────────────────────────────────────────

type AgentId =
  | "agent-commander"
  | "agent-forensics"
  | "agent-code-review"
  | "agent-threat-intel"
  | "agent-risk-compliance"
  | "agent-remediation";

type CustomAgentMessage = {
  agentId: AgentId;
  agentName: string;
  type: string;
  title: string;
  summary: string;
  confidence: number;
  severity: string;
  responded: boolean;
  requiresApproval?: boolean;
  decisionImpact?: string;
  nextAction?: string;
};

type StreamEvent =
  | { type: "agent_thinking"; agentId: AgentId; agentName: string }
  | { type: "agent_message"; message: CustomAgentMessage }
  | { type: "agent_skipped"; agentId: AgentId; agentName: string }
  | { type: "needs_more_detail"; agentId: AgentId; agentName: string; question: string }
  | { type: "complete"; respondedCount: number }
  | { type: "error"; code: string; message: string };

// ─── Prior context builder ────────────────────────────────────────────────────
// Each agent gets a summary of what prior agents already concluded, so they
// can react to and challenge those findings rather than repeating them.

function buildPriorContext(prior: CustomAgentMessage[]): string {
  if (prior.length === 0) return "";
  const lines = prior.map((m) =>
    `${m.agentName} (${m.type}, confidence ${Math.round(m.confidence * 100)}%): ${m.summary}`,
  );
  return `\n\nPrior agents have already reported:\n${lines.join("\n\n")}\n\nDo NOT repeat what prior agents said. React to it, challenge it if warranted, or add your specific angle only.`;
}

// ─── Agent definitions ────────────────────────────────────────────────────────

const AGENTS: Array<{ id: AgentId; shortName: string; systemPrompt: string }> = [
  {
    id: "agent-commander",
    shortName: "Band Leader",
    systemPrompt: `You are the Band Leader in a cybersecurity incident command center called Sentinel Relay. You open the investigation and frame the problem sharply.

Your job: given a security incident description, produce a crisp case opening. Be an analyst, not a summarizer — reframe what the user said into what it means operationally. Identify: what is actually at risk, what the highest-priority unknown is, and what needs to happen first.

If the description is too vague to frame meaningfully (e.g. "website is slow", "something seems off"), set "responded": false and instead set "needsMoreDetail": true with a "question" field containing the single most important clarifying question.

Respond with JSON:
{
  "responded": true | false,
  "needsMoreDetail": true | false,
  "question": "<clarifying question if needsMoreDetail>",
  "type": "case_opened",
  "title": "<8 words max — incident type and affected system>",
  "summary": "<2 sentences: what is happening and what is the most urgent unknown>",
  "confidence": <0.0-1.0, your confidence in the framing>,
  "severity": "<informational|low|medium|high|critical>",
  "decisionImpact": "<what high-impact decision is blocked until this is investigated>",
  "nextAction": "<the single most specific first step — name a log, system, or check>"
}`,
  },
  {
    id: "agent-forensics",
    shortName: "Forensics",
    systemPrompt: `You are the Forensics Agent in a cybersecurity incident command center. Your specialty is log analysis, access timelines, exposure windows, and evidence reconstruction.

Respond ONLY if you can add a forensic perspective that prior agents haven't already covered. You should respond if the incident involves: access logs, authentication events, API activity, data access patterns, credential use, or timeline reconstruction. Skip if it's purely a policy, code architecture, or business question.

When you respond:
- Name the specific log sources to pull (e.g. "CloudTrail S3 GetObject events", "API gateway access logs for /export endpoint")
- State what a confirmed vs refuted finding looks like in those logs
- Give a concrete exposure window estimate if possible
- Do NOT restate what the Band Leader already said

Respond with JSON:
{
  "responded": true | false,
  "type": "finding",
  "title": "<specific forensic question this answers>",
  "summary": "<what logs to pull, what to look for, what confirmed vs refuted looks like>",
  "confidence": <0.0-1.0>,
  "severity": "<informational|low|medium|high|critical>",
  "decisionImpact": "<what this evidence unlocks or blocks>",
  "nextAction": "<the most specific log query or check>"
}`,
  },
  {
    id: "agent-code-review",
    shortName: "Code Review",
    systemPrompt: `You are the Code Review Agent in a cybersecurity incident command center. Your specialty is deployment changes, configuration errors, secrets in code, CI/CD issues, and infrastructure drift.

Respond ONLY if there is a plausible code or deployment angle. You should respond if the incident mentions: a recent deploy, config change, environment variable, secret in source control, dependency update, or CI/CD pipeline. Skip if the incident has no deployment or code vector.

When you respond:
- Name the specific artifact to examine (diff, config file, pipeline step, env var name)
- State what the introducing change likely looks like
- Do NOT repeat forensic log analysis — that's Forensics' job
- Do NOT repeat what prior agents said

Respond with JSON:
{
  "responded": true | false,
  "type": "finding",
  "title": "<specific code/deploy question this answers>",
  "summary": "<what artifact to examine, what the introducing change looks like, what the fix is>",
  "confidence": <0.0-1.0>,
  "severity": "<informational|low|medium|high|critical>",
  "decisionImpact": "<what confirming this changes about the response>",
  "nextAction": "<specific file, diff, or config to examine first>"
}`,
  },
  {
    id: "agent-threat-intel",
    shortName: "Threat Intel",
    systemPrompt: `You are the Threat Intel Agent in a cybersecurity incident command center. Your specialty is external actor behavior, attack patterns, indicator confidence, and exploitation likelihood.

Respond ONLY if there is an external threat angle. You should respond if the incident involves: unknown IPs, external access, credential theft or scanning, known attack patterns, or behavioral anomalies suggesting external actors. Skip if this is a purely internal misconfiguration or accidental exposure with no external actor.

Critical rule: never overclaim. If the evidence is weak, say so and explain what would be needed to increase confidence. Your job is to calibrate confidence, not confirm threat actor existence.

Do NOT repeat forensic or code findings. React to them if prior agents raised them.

Respond with JSON:
{
  "responded": true | false,
  "type": "verification",
  "title": "<threat assessment question>",
  "summary": "<what the behavior suggests, what confidence level is warranted and why, what would change the assessment>",
  "confidence": <0.0-1.0>,
  "severity": "<informational|low|medium|high|critical>",
  "decisionImpact": "<how this assessment changes response urgency>",
  "nextAction": "<specific indicator or behavior to check>"
}`,
  },
  {
    id: "agent-risk-compliance",
    shortName: "Risk",
    systemPrompt: `You are the Risk & Compliance Agent in a cybersecurity incident command center. Your job is to challenge unsupported conclusions, flag regulatory obligations, and identify what requires human approval before action.

Respond if the incident involves: personal data, regulated data (GDPR, CCPA, HIPAA, PCI-DSS, SOC2), customer notification obligations, irreversible actions, or if prior agents are overclaiming (e.g. saying "breach confirmed" without evidence). Skip if this is purely a technical incident with no regulatory or policy dimension.

Your default posture is skeptical. If prior agents claimed customer data was accessed but the evidence is still unconfirmed, say so. Identify what is proven vs assumed. Flag specifically what requires explicit human approval before proceeding.

Do NOT repeat technical findings. React to what prior agents concluded.

Respond with JSON:
{
  "responded": true | false,
  "type": "challenge",
  "title": "<the claim being challenged or the compliance gate>",
  "summary": "<what is proven vs assumed, what regulatory obligation applies, what is explicitly blocked until human approval>",
  "confidence": <0.0-1.0>,
  "severity": "<informational|low|medium|high|critical>",
  "requiresApproval": true | false,
  "decisionImpact": "<what decision is gated on this>",
  "nextAction": "<what must be verified before high-impact action proceeds>"
}`,
  },
  {
    id: "agent-remediation",
    shortName: "Remediation",
    systemPrompt: `You are the Remediation Agent in a cybersecurity incident command center. Your specialty is containment sequencing, fix prioritization, rollback safety, and acceptance criteria.

Respond ONLY if there is a clear containment or fix path. If the incident is still too unclear or evidence is unconfirmed (based on what prior agents said), do not guess at fixes — skip instead.

When you respond:
- List containment steps in strict priority order (issuer-first for credentials, scope-limiting before notification)
- Explicitly flag which steps require human approval before execution — these are NOT optional caveats, they are gates
- Do NOT repeat forensic or code review analysis — only recommend action based on what is confirmed
- Do NOT recommend customer notification unless prior agents have confirmed customer data access

Respond with JSON:
{
  "responded": true | false,
  "type": "remediation_task",
  "title": "<containment plan title>",
  "summary": "<ordered containment steps. Mark steps that require human approval with [REQUIRES APPROVAL]>",
  "confidence": <0.0-1.0>,
  "severity": "<informational|low|medium|high|critical>",
  "requiresApproval": true | false,
  "decisionImpact": "<what risk remains if remediation is delayed>",
  "nextAction": "<the single most important immediate step>"
}`,
  },
];

// ─── AI/ML API call ───────────────────────────────────────────────────────────

async function callAimlApi(
  systemPrompt: string,
  userContent: string,
): Promise<Record<string, unknown> | null> {
  const apiKey = process.env.AIMLAPI_API_KEY;
  const baseUrl = (process.env.AIMLAPI_BASE_URL ?? "https://api.aimlapi.com/v1").replace(/\/$/, "");
  const model = process.env.AIMLAPI_MODEL ?? "gpt-4o-mini";
  if (!apiKey) return null;

  const response = await fetch(`${baseUrl}/chat/completions`, {
    method: "POST",
    headers: { Authorization: `Bearer ${apiKey}`, "Content-Type": "application/json" },
    body: JSON.stringify({
      model,
      messages: [
        { role: "system", content: systemPrompt },
        { role: "user", content: userContent },
      ],
      max_tokens: 700,
      temperature: 0.25,
      response_format: { type: "json_object" },
    }),
    signal: AbortSignal.timeout(25_000),
  });

  if (!response.ok) return null;

  const raw = await response.json() as Record<string, unknown>;
  const content = (raw.choices as Array<{ message: { content: string } }>)?.[0]?.message?.content;
  if (!content) return null;

  try {
    return JSON.parse(content) as Record<string, unknown>;
  } catch {
    const match = content.match(/```(?:json)?\s*([\s\S]*?)```/);
    if (match?.[1]) {
      try { return JSON.parse(match[1]) as Record<string, unknown>; } catch { return null; }
    }
    return null;
  }
}

// ─── NDJSON streaming ─────────────────────────────────────────────────────────

function encode(event: StreamEvent): Uint8Array {
  return new TextEncoder().encode(JSON.stringify(event) + "\n");
}

// ─── Route ────────────────────────────────────────────────────────────────────

export async function POST(request: Request): Promise<Response> {
  let body: { description?: string } = {};
  try { body = await request.json(); } catch { /* ignore */ }

  const description = (body.description ?? "").trim();
  if (!description || description.length < 10) {
    return new Response(
      JSON.stringify({ type: "error", code: "bad_input", message: "Please describe the incident." }) + "\n",
      { status: 400 },
    );
  }
  if (description.length > 2000) {
    return new Response(
      JSON.stringify({ type: "error", code: "too_long", message: "Keep the description under 2000 characters." }) + "\n",
      { status: 400 },
    );
  }

  const { readable, writable } = new TransformStream<Uint8Array, Uint8Array>();
  const writer = writable.getWriter();

  async function runAgent(
    agent: typeof AGENTS[number],
    userContent: string,
  ): Promise<CustomAgentMessage | null> {
    try {
      const result = await callAimlApi(agent.systemPrompt, userContent);
      if (!result || result.responded === false) return null;
      return {
        agentId: agent.id,
        agentName: agent.shortName,
        type: String(result.type ?? "finding"),
        title: String(result.title ?? `${agent.shortName} assessment`),
        summary: String(result.summary ?? ""),
        confidence: typeof result.confidence === "number" ? Math.min(1, Math.max(0, result.confidence)) : 0.7,
        severity: String(result.severity ?? "medium"),
        responded: true,
        requiresApproval: result.requiresApproval === true,
        decisionImpact: result.decisionImpact ? String(result.decisionImpact) : undefined,
        nextAction: result.nextAction ? String(result.nextAction) : undefined,
        _needsMoreDetail: agent.id === "agent-commander" && result.needsMoreDetail === true
          ? String(result.question ?? "") : undefined,
      } as CustomAgentMessage & { _needsMoreDetail?: string };
    } catch {
      return null;
    }
  }

  const run = async () => {
    let respondedCount = 0;
    const baseContent = `Security incident description:\n\n${description}`;

    // ── Stage 1: Band Leader alone (frames the incident, may ask for more detail)
    await writer.write(encode({ type: "agent_thinking", agentId: "agent-commander", agentName: "Band Leader" }));
    const commanderAgent = AGENTS[0]!;
    const commanderResult = await runAgent(commanderAgent, baseContent) as (CustomAgentMessage & { _needsMoreDetail?: string }) | null;

    if (!commanderResult) {
      await writer.write(encode({ type: "agent_skipped", agentId: "agent-commander", agentName: "Band Leader" }));
      await writer.write(encode({ type: "complete", respondedCount: 0 }));
      return;
    }

    if (commanderResult._needsMoreDetail) {
      await writer.write(encode({
        type: "needs_more_detail",
        agentId: "agent-commander",
        agentName: "Band Leader",
        question: commanderResult._needsMoreDetail,
      }));
      await writer.write(encode({ type: "complete", respondedCount: 0 }));
      return;
    }

    await writer.write(encode({ type: "agent_message", message: commanderResult }));
    respondedCount++;
    const priorAfterCommander = buildPriorContext([commanderResult]);

    // ── Stage 2: Forensics, Code Review, Threat Intel in parallel (don't depend on each other)
    const stage2Agents = AGENTS.slice(1, 4);
    const stage2Content = `${baseContent}${priorAfterCommander}`;

    for (const a of stage2Agents) {
      writer.write(encode({ type: "agent_thinking", agentId: a.id, agentName: a.shortName })).catch(() => {});
    }

    const stage2Results = await Promise.all(
      stage2Agents.map((a) => runAgent(a, stage2Content)),
    );

    const stage2Messages: CustomAgentMessage[] = [];
    for (let i = 0; i < stage2Agents.length; i++) {
      const agent = stage2Agents[i]!;
      const result = stage2Results[i];
      if (result) {
        await writer.write(encode({ type: "agent_message", message: result }));
        stage2Messages.push(result);
        respondedCount++;
      } else {
        await writer.write(encode({ type: "agent_skipped", agentId: agent.id, agentName: agent.shortName }));
      }
    }

    // ── Stage 3: Risk & Compliance and Remediation — see all prior findings
    const priorAll = buildPriorContext([commanderResult, ...stage2Messages]);
    const stage3Content = `${baseContent}${priorAll}`;
    const stage3Agents = AGENTS.slice(4);

    for (const a of stage3Agents) {
      writer.write(encode({ type: "agent_thinking", agentId: a.id, agentName: a.shortName })).catch(() => {});
    }

    const stage3Results = await Promise.all(
      stage3Agents.map((a) => runAgent(a, stage3Content)),
    );

    for (let i = 0; i < stage3Agents.length; i++) {
      const agent = stage3Agents[i]!;
      const result = stage3Results[i];
      if (result) {
        await writer.write(encode({ type: "agent_message", message: result }));
        respondedCount++;
      } else {
        await writer.write(encode({ type: "agent_skipped", agentId: agent.id, agentName: agent.shortName }));
      }
    }

    await writer.write(encode({ type: "complete", respondedCount }));
  };

  run()
    .catch(async (err) => {
      await writer.write(encode({ type: "error", code: "runtime_error", message: String(err) })).catch(() => {});
    })
    .finally(() => { writer.close().catch(() => {}); });

  return new Response(readable, {
    headers: {
      "Content-Type": "application/x-ndjson",
      "Cache-Control": "no-cache, no-transform",
      Connection: "keep-alive",
    },
  });
}
