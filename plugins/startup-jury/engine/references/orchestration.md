# 7. Normalized startup packet and frozen Stage 1 input

Before launching Stage 1, create a neutral normalized STARTUP PACKET containing:

- `PROPOSED PRODUCT / SERVICE`;
- `PRIMARY USER`;
- `ECONOMIC BUYER / PAYER`, if different;
- `CORE JOB / USE CASE`;
- `CURRENT ALTERNATIVE / STATUS QUO`;
- `STARTUP STAGE`;
- `STARTUP ARCHETYPE(S)`;
- `TARGET GEOGRAPHY / REGULATORY CONTEXT`, if material;
- `INTENDED BUSINESS AMBITION`, if known: venture-scale / bootstrapped / small profitable business / unknown;
- `KNOWN TEAM / CAPITAL / DISTRIBUTION / DOMAIN ACCESS`, if supplied;
- `USER-SUPPLIED EVIDENCE`;
- `EXPLICIT ASSUMPTIONS`;
- `IMPORTANT UNKNOWNS`.

Do not improve the pitch while normalizing it.

Do not silently substitute a stronger adjacent ICP, buyer, product scope, monetization model, or distribution strategy.

If the user's business ambition is unknown, do not assume venture scale. Evaluate basic business viability and classify plausible outcome separately later.

Freeze this packet before Stage 1.

Every first-stage agent must receive the SAME frozen STARTUP PACKET plus the same user-provided source materials legitimately available to all roles.

Do NOT include:

- coordinator opinions;
- summaries of another first-stage agent;
- partial conclusions from earlier first-stage runs;
- post-hoc advocate/skeptic framing.

If Stage 1 must run in multiple batches because of concurrency limits, later batches still receive only the frozen packet and permitted common sources, never previous Stage 1 reports.

---

# 8. First-stage architecture

Run EIGHT independent specialist agents concurrently.

They must all receive:

- the same frozen STARTUP PACKET;
- the same permitted common user-supplied source materials.

Their initial reports must be independent.

They MUST NOT see each other's reports before submitting.

Use these agents:

1. `startup_customer_demand`
2. `startup_market_timing`
3. `startup_landscape`
4. `startup_distribution`
5. `startup_economics`
6. `startup_product_execution`
7. `startup_advocate`
8. `startup_skeptic`

Wait for all eight to finish, or exhaust the defined retry/failure procedure and explicitly record any missing role before Stage 2.

These agents must not spawn additional subagents.

---

# 34. Independence and failure handling

The first eight agents must remain independent.

Do NOT:

1. run the Skeptic;
2. show its report to other first-stage agents;
3. ask them to respond.

All first-stage agents analyze the same frozen STARTUP PACKET independently.

Only:

- Verifier;
- Cross-Examiner;
- Judge

see the combined reports.

Each Stage 1 invocation must receive the frozen STARTUP PACKET directly, not a coordinator-generated paraphrase produced after other agents have run.

If concurrency is lower than eight, use independent batches. Later batches must not receive earlier Stage 1 outputs.

If a first-stage agent errors, times out, or returns an invalid/incomplete schema:

1. record the failure;
2. retry that role once with the same frozen packet if the current Codex environment supports a safe retry;
3. do not substitute another role's report;
4. do not simulate multiple agents inside one assistant response while claiming independence;
5. propagate unresolved missing-role limitations to Verifier, Cross-Examiner, and Judge and use `LIMITED` or `BLOCKED` appropriately.

After a batch's reports are captured by the coordinator, close/release child-agent sessions when the current Codex runtime requires this to free concurrency slots before later stages. Do not discard the captured reports.

---

# 35. Custom agent differentiation

Ensure agents do not collapse into generic startup reviewers.

`startup_customer_demand`
= Does anybody meaningfully want this?

`startup_market_timing`
= Is there enough opportunity and is now a plausible time?

`startup_landscape`
= What does the customer already have and why could this win?

`startup_distribution`
= How does this reach customers?

`startup_economics`
= Can value capture plausibly produce sustainable economics?

`startup_product_execution`
= Can the commercially required product actually be delivered?

`startup_advocate`
= Strongest rigorous case FOR.

`startup_skeptic`
= Strongest rigorous case AGAINST.

`startup_verifier`
= Which factual claims are actually supported?

`startup_cross_examiner`
= Do all parts of the business model work simultaneously?

`startup_judge`
= Should the startup be pursued?

---
