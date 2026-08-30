# ControlPlane.ai — Business Proposal
### Accenture Innovation Challenge 2026 · Round 2 · Team TrendMaker

---

## 1. Problem framing

Enterprises now run generative AI across many use cases at once — customer-facing chatbots, internal copilots, decision-support tools in regulated workflows — and each carries a different risk signature depending on the model, the data it draws on, and how its output gets used downstream.

Today's oversight response to this is almost always the same: sort traffic into a small number of hand-drawn buckets (customer-facing / internal / regulated, or similar) and apply one level of checking per bucket. This fails in a specific, measurable way: **a ₹42,00,000 fire-damage claim and a ₹4,000 windscreen claim, if they land in the same bucket, get the same checks, the same cost, the same speed.** Gartner's own 2026 position states this plainly: *"applying uniform governance across AI agents will lead to enterprise AI agent failure."*

The deeper problem is not that mistakes happen — it's that **almost no organization has actually measured what an AI mistake costs, or what a wrongly-blocked legitimate request costs.** The checking level in most deployments is a guess that became a habit, not a deliberate, defensible tradeoff.

A second, easy-to-miss failure mode matters just as much: **rupee amount is not the same thing as stakes.** A ₹5 medicine recommendation with a fatal drug interaction and a ₹50,00,000 medicine approval both carry the same irreducible ceiling — someone can be seriously harmed. A pricing model that uses amount as its only proxy for risk will silently underweight the ₹5 case. Any credible solution has to treat financial exposure and harm potential as separate, independently-weighted inputs — not conflate them.

## 2. Solution design

**ControlPlane.ai is a Consequence Layer**: a policy-and-verification layer that sits at the input/output boundary of any AI system — never inside the model, never requiring access to model internals, since enterprises overwhelmingly consume foundation models via API rather than owning them outright.

It prices every request from signals the business already owns before spending any compute checking it:

- **Reversibility** — reversible / hard-to-reverse / irreversible
- **Amount-to-authority ratio** — how much of the approving party's own sign-off limit this decision consumes
- **Consequence Class** — Financial-only / Safety-critical / Legal-Regulatory / Reputational / Informational, set independently of amount, so a low-rupee safety-critical item is never underweighted by a purely financial pricing model

That price routes the request to one of three checking tiers (Light / Standard / Heavy), each running a different combination of detectors — PII/entity detection, groundedness verification against a supplied source (with an explicit signal, `NO_GROUND_TRUTH_AVAILABLE`, when no source exists, rather than faking verification), a bias/loaded-language check, a statistical outlier check against a rolling baseline, and — only at Heavy tier, where the cost is justified — a secondary AI-as-judge opinion.

Two hard floors prevent the pricing formula from being gamed or from silently under-checking real risk: **Safety-critical and Legal-Regulatory items always route to Heavy tier**, regardless of price, and always **bypass Governance Budget throttling** — the system cannot be made to skip a safety check simply because it's under load. **Adaptive Risk Memory** accumulates risk against the *entity* a request touches (a claim ID, an account, a vendor), not just the requester, closing the obvious evasion of splitting one large irreversible action into several small ones. **Living Policy Genome** represents regulatory requirements as modular, versioned rules that workflows inherit — so a single regulatory update propagates to every dependent workflow instead of requiring dozens of manual edits, and every audit-log entry records exactly which rule version governed that decision.

Every decision, check, price, and outcome is written to an **Outcome Ledger**, and human overrides feed a **feedback loop** that adjusts detector confidence over time — with the override itself required to state *why* (not actually risky, vs. right issue wrong remedy), so the feedback loop can't be gamed into silently disabling a detector that was actually right.

## 3. Target users

- **Risk/compliance and AI governance teams** at enterprises running multiple concurrent AI use cases — the direct configurers of thresholds, Consequence Classes, and Policy Genes.
- **Frontline reviewers** (claims adjusters, support leads, clinical reviewers) who receive escalated items with a clear, structured reason rather than an opaque flag.
- **Engineering/platform teams** integrating the layer at the API boundary of existing AI deployments, who benefit from a model-agnostic design that doesn't require touching the underlying model.
- **Department heads** who own a Governance Budget and need oversight spend to behave like a manageable resource, not an unpredictable stream of alerts.

## 4. Business case and impact

The status quo cost is dual-sided: **over-checking** wastes compute and latency on low-stakes traffic and creates alert fatigue that trains staff to ignore warnings; **under-checking** exposes the organization to the exact liability the Round 1 brief opened with — a confidently wrong, quietly expensive, or subtly biased response discovered only after a user has already acted on it.

ControlPlane.ai's value case is that **checking cost should track consequence, not category** — so the same total oversight budget can be redirected from routine ₹4,000 windscreen claims (fast, cheap, correctly low-friction) toward the ₹42,00,000 fire claims and safety-critical items that actually warrant it, without adding net latency or net spend to the system as a whole. The Governance Budget mechanism makes this an explicit, auditable resource-allocation decision rather than an implicit one, giving compliance teams a lever they can actually report on to leadership.

## 5. Phased roadmap

**Phase 1 (this prototype):** core pricing/tiering/verification pipeline, Adaptive Risk Memory, Governance Budget, Living Policy Genome, Decision Sandbox dry-run checks, feedback loop — demonstrated model-agnostically, standalone, no external dependencies.

**Phase 2:** replace the deterministic AI-judge stand-in with a real secondary-LLM call via a backend proxy (holding API credentials server-side, never client-side); add an authenticated identity layer so Adaptive Risk Memory reflects real user/session identity rather than self-reported IDs; move the Outcome Ledger to an append-only or hash-chained store for tamper-evident audit integrity.

**Phase 3:** multi-model consensus scoring for genuinely no-ground-truth cases (e.g., strategic or legal judgment calls) — explicitly designed around correlated-error mitigation, since independent models can still share the same training-data blind spots and agree confidently on the same wrong answer; this is why it's scoped to Phase 3 rather than claimed as solved today.

**Phase 4:** backpressure handling for Heavy-tier demand surges — near-duplicate request caching/batching, with genuine surge routed into a managed human queue rather than silently degrading check depth.

## 6. Key risks and mitigations

| Risk | Mitigation |
|---|---|
| Pricing formula gamed by structuring one large action as several small ones | Adaptive Risk Memory accumulates against the referenced entity, not just the requester, across a rolling window |
| Governance Budget exhaustion silently degrades checking during a genuine incident | Safety-critical/Legal class, a tripped circuit breaker, and amounts exceeding 3× approver authority always bypass budget throttling |
| AI-as-judge stage becomes a prompt-injection bypass (response text instructing the judge to clear itself) | Response content is only ever read as delimited data, never as instructions; judge scoring is monotonic — it can add risk signal, never cancel a flag another detector already raised |
| Regulatory rules go stale as law changes | Living Policy Genome — a single gene update propagates to every workflow that inherits it, versioned per decision for audit purposes |
| Feedback loop gamed by mass override to quietly disable a detector | Override requires a stated reason; only "not actually risky" decays detector confidence; override concentration per reviewer is tracked as its own metric |
| False-negative rate silently misrepresented | Not reported at all in the metrics panel — stated explicitly as unmeasurable without a labeled evaluation set, rather than estimated |
| Source documents used for groundedness checks may themselves be unreliable (well-governed vs. loosely-governed data sources) | Source Trust Tier caps groundedness confidence on unverified sources for safety/legal items — does not itself solve source-quality verification, named as a Phase 2+ item |
| Detector techniques (regex PII, lexical-overlap groundedness, keyword bias lexicon) are individually simple and not state-of-the-art | Deliberate choice for a dependency-free, standalone prototype — each is designed to be swappable; the claimed innovation is the pricing/routing logic that decides how much checking to buy, not the detectors themselves |
