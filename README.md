# ControlPlane.ai — Consequence Layer

**Accenture Innovation Challenge 2026 — Round 2 Prototype**
**Team TrendMaker** — Rushikesh Gundewar, Aaditya Dabhade, Nazmi Syed (Geophysics, IIT Kharagpur)
**Track:** ControlPlane.ai
---

## 1. What this is

Most AI governance layers sort traffic into a small number of hand-drawn categories (customer-facing / internal / regulated) and give every request in a category identical checking. That means a ₹42,00,000 fire claim and a ₹4,000 windscreen claim can receive the same scrutiny, the same cost, the same speed — while a genuinely dangerous request that happens to carry no rupee value at all (a wrong drug-interaction answer, say) can slip through underweighted.

**ControlPlane.ai is a Consequence Layer**: it prices every AI request from signals the business already owns — reversibility, amount, who has authority over it, and what kind of harm is possible — *before* spending any compute checking it. The price decides how much checking the request gets, not a fixed category.

It sits at the **input/output boundary only**. It never needs access to model internals, works with any foundation model consumed via API, and the prototype demonstrates this directly: label the "source model" field anything you like and the price, tier, and decision are unaffected.

## 2. Solution architecture

```
Any model (GPT / Claude / Gemini / Llama / your fine-tune)
        │  (prompt + response text only — no internals)
        ▼
┌───────────────────────────────────────────────────────────┐
│  1. Consequence Engine                                     │
│     prices the request from reversibility, amount/approval  │
│     ratio, and Consequence Class (financial / safety /      │
│     legal / reputational / informational)                   │
├───────────────────────────────────────────────────────────┤
│  2. Assurance Router                                        │
│     price → tier (Light / Standard / Heavy), gated by a      │
│     department Governance Budget — except three              │
│     non-negotiable triggers that always bypass budget:        │
│     Safety-critical/Legal class, a tripped circuit breaker,   │
│     or an amount exceeding 3× the approver's own authority    │
├───────────────────────────────────────────────────────────┤
│  3. Verification Layer  (checks run per tier)                │
│     • PII / entity detector (regex)                          │
│     • Groundedness check vs. supplied source, incl. a         │
│       negation-asymmetry check ("not approved" vs "approved")  │
│       — explicitly flags NO_GROUND_TRUTH_AVAILABLE when no     │
│       source exists, rather than faking verification           │
│     • Bias / loaded-language lexicon                          │
│     • Statistical outlier check — response shape vs. a         │
│       rolling per-(use case, consequence class) baseline;       │
│       abstains under 5 samples rather than guessing             │
│     • AI-as-judge second opinion (Heavy tier only) —            │
│       a deterministic stand-in for a real secondary-LLM call     │
│       in this prototype (see §5); monotonic — can only add       │
│       risk signal, never cancel a flag another detector raised   │
├───────────────────────────────────────────────────────────┤
│  4a. Decision Sandbox  (Safety/Legal class, or Heavy+          │
│      irreversible only) — pre-execution dry-run: duplicate      │
│      check, budget-cap check, approval-chain check              │
├───────────────────────────────────────────────────────────┤
│  4b. Action Engine — Allow / Redo / Mask / Escalate / Block,    │
│      tunable Allow/Escalate thresholds                          │
├───────────────────────────────────────────────────────────┤
│  5. Outcome Ledger — every price, tier, check, decision,        │
│     latency, and the active Policy Gene version logged           │
└───────────────────────────────────────────────────────────┘
        │
        ▼
End user / downstream system / agent action
```

**Supporting mechanisms, running alongside the pipeline:**

- **Adaptive Risk Memory** — risk accumulates against the *entity* referenced (claim ID, account ID, vendor ID) in a rolling window, not just the requester — so splitting one large action into several small ones against the same entity, even across sessions, still trips the circuit breaker.
- **Governance Budget** — denominated in check-cost points per department, not raw alert count, so it can't be exhausted by trivia right before a real event — and the three non-negotiable triggers above always bypass it.
- **Living Policy Genome** — regulations are modular "genes" (e.g. G1 PII masking, G2 health-data consent, G3 lending disclosure); a workflow inherits only the genes it needs, conflicts resolve strictest-wins, and every ledger row stamps the gene *version* active at decision time for audit integrity.
- **Feedback loop** — a human override requires a reason (*not actually risky* vs. *right issue, wrong remedy*); only the former decays the triggering detector's confidence weight, so the loop can't be gamed into silently disabling a detector that was actually correct.

## 3. Why the pricing logic is the innovation (not the detectors)

The detectors themselves — regex PII matching, lexical-overlap groundedness, a bias keyword lexicon — are intentionally simple, off-the-shelf techniques. That is a deliberate choice, not a limitation we're hiding: they run with zero external dependencies, so the prototype works offline, in any browser, with nothing to install.

The actual novel claim is in the **routing logic**: pricing a request from organizational signals (reversibility, authority, consequence class) is free and instant — no model call required — so the system decides *how much to spend checking* before it spends anything. That ordering is what makes the approach efficient, and it borrows deliberately from patterns that already exist elsewhere:

| Mechanism here | Borrowed pattern |
|---|---|
| Price-before-check tiering | Adaptive/early-exit computation in ML systems — spend compute proportional to difficulty, decided up front |
| Monotonic AI-judge scoring | Integrity-lattice models (Biba) — once risk is asserted, nothing downstream can silently cancel it |
| Entity-linked risk accumulation | AML transaction-structuring detection — splitting one large action into many small ones under different identities is a known evasion pattern |
| Non-negotiable safety tier | Non-maskable interrupts in real-time systems — a priority that can't be starved out under load |
| Policy Genome conflict resolution | Deny-overrides policy combination (XACML/ABAC) |

## 4. Honest limitations (stated deliberately, not overlooked)

- **False-negative rate is not reported.** It requires a labeled evaluation set this prototype doesn't have; reporting a number would be fabricated, so the metrics panel says so explicitly instead.
- **The AI-as-judge stage is simulated.** See §5 for why, and what a production version needs.
- **PII regex and the bias lexicon have real recall/precision limits** — they're a coarse first pass, not a complete detector, and are explicitly swappable.
- **Groundedness checking trusts the supplied source document's own reliability** — it does not itself verify whether the source is accurate, only whether the response is consistent with it. Source Trust Tier (Verified / Unverified / None) partially addresses this by capping confidence on unverified sources for safety/legal items, but doesn't solve source-quality verification itself.
- **Session/entity identity is self-reported** in this prototype (no auth layer) — production requires an authenticated identity system for Adaptive Risk Memory to be trustworthy.
- **The ledger is a plain in-memory array**, not tamper-evident — production needs an append-only or hash-chained audit log.

## 5. Dependencies

**None.** `index.html` is a single self-contained file — HTML, CSS, and vanilla JavaScript, no build step, no package manager, no server.

The only external network calls are two Google Fonts `<link>` tags (Space Grotesk, Inter, JetBrains Mono) — the page still functions correctly without them (falls back to system fonts), so it works fully offline.

**On the AI-as-judge stage specifically:** a real secondary-LLM call would require an API key. Calling a model API directly from client-side JavaScript in a static file would expose that key to anyone who views the page source — a real credential leak, not a shortcut worth taking for a demo. The correct production design is a backend proxy that holds the key server-side and forwards judged requests; that's a genuine build (auth, hosting, rate-limiting) outside this prototype's scope. The judge stage here is therefore a clearly-labeled deterministic stand-in, with the exact function (`judgeCheck` in `index.html`) commented to show where the real call plugs in. This is stated openly in the demo narration rather than presented as a live integration.

## 6. Execution instructions

**To run locally:** download `index.html` and open it in any modern browser (Chrome, Edge, Firefox, Safari) — double-click it, no installation needed.

**To use the demo:**
1. Two pre-loaded examples are available via the buttons under the request form ("load routine example," "load ₹5 medicine example") — these demonstrate the low-stakes fast path and the low-amount-but-safety-critical case respectively.
2. Click **"Run through Consequence Layer"** to watch the five-stage pipeline execute live, with real computed values at each stage.
3. Try changing the **Consequence Class** to "Safety-critical" on a low-amount request to see the non-negotiable floor override the price-based tier.
4. Toggle a gene off in **Living Policy Genome** and re-run a request to see the gene-version stamp change on the new ledger row.
5. Run several requests with the same **Entity ID** to watch **Adaptive Risk Memory** accumulate and eventually trip the circuit breaker.
6. Use the **"not risky" / "wrong remedy"** buttons on any ledger row to see the **Feedback Loop** detector-confidence weights shift.

**To deploy publicly (GitHub Pages):** in the repository settings, under Pages, set source to "Deploy from branch," branch `main`, folder `/root`. GitHub will publish `index.html` at a public URL within about a minute — no build step required.

## 7. Repository contents

```
index.html    — the working prototype (this is the entire application)
Streamlit_link - https://trendmakers.streamlit.app/
README.md     — this file
PROPOSAL.md   — business proposal: problem framing, solution design, target
                users, business case, phased roadmap, risks & mitigations
```
