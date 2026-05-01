# AI-Native Portfolio Project Briefs (Recruiter + ATS Optimized)

Assumed profile for this build: **AI SWE / Backend / Full-Stack / AI Solutions Engineer**, **TypeScript + Python**, **US remote / Bay Area**, domains: **HealthTech, FinTech, Logistics**, constraints: **weekend MVP + 2-week V1**.

---

## Project 1 — Clinical Prior Authorization Copilot (HealthTech)

### one-line pitch
An AI-assisted prior-authorization platform that cuts payer submission time from hours to minutes while preserving auditability and HIPAA-conscious controls.

### why it matters
Prior auth teams (provider-side revenue cycle staff) lose time stitching chart notes, diagnosis codes, and payer forms; denials and slow approvals delay care and cash flow. This project targets operations leads and specialists, aiming to reduce average submission prep time by **60%+** and first-pass denial rate by **15%** with explainable evidence linking.

### differentiators vs “todo app”
- Handles unreliable payer APIs with retries, idempotency keys, and dead-letter queues.
- Enforces deterministic “human-in-the-loop” checkpoints for safety-critical outputs.
- Includes PII redaction and structured audit logs for compliance review.
- Uses eval gates (citation correctness + hallucination checks) before enabling auto-draft mode.
- Adds token and latency budgets to keep per-case AI cost predictable.

### architecture overview
```text
[Next.js UI + Auth.js]
   |  REST/GraphQL + JWT/OAuth2
   v
[API Gateway/BFF (Fastify/Nest)] -----> [Redis: cache + rate limit]
   |            |                         
   |            +---- OpenAPI docs -------
   |
   +--> [Postgres/Supabase] <----> [pgvector (RAG)]
   |          |                          ^
   |          +--> [S3: document store]  |
   |
   +--> [Queue (SQS/RabbitMQ)] --> [Worker svc (Python)] --> [OpenAI/Anthropic]
                  |                        |     (agent loop: retrieve->draft->verify)
                  |                        v
                  +--> [DLQ]         [Eval runner + policy checks]

[Observability: OpenTelemetry -> Prometheus/Grafana]
[CI/CD: GitHub Actions] [Dockerized services] [Optional K8s]
```
Security: zod/pydantic validation, per-tenant RBAC, JWT expiry/rotation, secret manager, PHI tagging, encrypted S3 buckets, signed URLs.
Cost controls: prompt caching, retrieval chunk caps, model routing (small model default, large model escalation), monthly budget alerts.

### scoped feature set
**Weekend MVP**
- OAuth login, org/user roles.
- Upload patient packet (PDF), OCR + chunking to S3/pgvector.
- Generate prior-auth draft with source citations.
- Submission queue + background status polling.
- Basic dashboard: turnaround time, denials, AI cost per case.

**Week-2 V1**
- Payer-specific form templates + field-level confidence scores.
- Human approval workflow with diff view.
- Redaction pipeline and immutable audit timeline.
- Auto-retry with DLQ replay UI.
- Canary model switch via feature flags.

### acceptance criteria and demo script
**Acceptance criteria**
- 95% of seeded cases generate draft in <45s.
- Every generated rationale includes >=1 supporting citation.
- Retry path processes transient failure within 2 attempts.
- Audit log records actor, timestamp, decision.

**3-minute deterministic demo**
1. Login as `ops-manager@demohealth.io`.
2. Load seed case `CASE-PA-0007`.
3. Click “Generate Draft”; show evidence panel with citations.
4. Force simulated payer API timeout; show queued retry + eventual success.
5. Approve and submit; open audit timeline and KPI widget.

Seed data: 20 synthetic patient packets, 3 payer rule profiles, 50 historical outcomes.

### test plan
- **Unit**: parser, validator, auth middleware, prompt-builder (Jest + Pytest).
- **Integration**: API ↔ queue ↔ worker ↔ DB with test containers.
- **Load**: k6 scenario at 50 VUs for submission endpoint.

Target metrics:
- p95 `/cases/:id/generate` < 2.5s API ack (async job accepted).
- p95 end-to-end draft completion < 45s.
- Throughput: 300 cases/hour sustained in worker tier.
- Error budget: <1% failed jobs excluding injected faults.

Minimal k6:
```js
import http from 'k6/http';
import { check, sleep } from 'k6';
export let options = { vus: 50, duration: '2m' };
export default function () {
  const res = http.post(`${__ENV.API_URL}/v1/cases/CASE-PA-0007/generate`, {}, { headers: { Authorization: `Bearer ${__ENV.TOKEN}` } });
  check(res, { 'accepted': (r) => r.status === 202 });
  sleep(1);
}
```

### evals for ai behavior (if applicable)
Offline eval set: 200 de-identified historical cases with known payer outcomes.
- Citation faithfulness >= 0.90.
- Required-code extraction F1 >= 0.88.
- Hallucination rate <= 3% on adjudicated sample.
Run locally in CI: `pytest evals/ --maxfail=1` with fixed model snapshot + deterministic seed; block merge if thresholds fail.

### resume bullets (3)
- Built a HIPAA-conscious AI prior-authorization platform processing **300+ cases/hour**, reducing draft preparation time by **62%** through RAG + async worker orchestration.
- Implemented queue-driven reliability (retry, DLQ replay, idempotency), cutting transient-failure drop-offs from **8.4% to 0.9%**.
- Added offline AI eval gating and observability (OTel traces + SLO dashboards), improving citation faithfulness to **91%** and keeping AI cost under **$0.42/case**.

ATS keyword line: REST, GraphQL, distributed systems, message queues, Postgres, S3, Redis, Docker, CI/CD, GitHub Actions, OAuth2, JWT, OpenTelemetry, RAG, vector DB, embeddings, evaluations, agents, caching.

### ats keyword coverage
- [x] rest
- [x] graphql
- [ ] websockets
- [x] microservices
- [x] distributed systems
- [x] message queues
- [x] postgres
- [ ] dynamodb
- [x] s3
- [x] redis
- [x] docker
- [ ] kubernetes
- [x] ci/cd
- [x] github actions
- [x] testing (jest/pytest)
- [x] openapi
- [x] oauth2
- [x] jwt
- [x] rate limiting
- [x] observability
- [x] opentelemetry
- [x] tracing
- [x] rag
- [x] vector db
- [x] embeddings
- [x] prompt engineering
- [x] evaluations
- [x] agents
- [x] caching
- [x] feature flags
- [ ] infra as code (terraform optional)
- [x] aws (lambda, ec2)
- [ ] gcp/azure acceptable alternatives

### repo blueprint
```text
clinical-auth-copilot/
  apps/web/                     # Next.js UI
  services/api/                 # REST + GraphQL BFF
  services/worker/              # Python async jobs
  packages/shared/              # types/schemas/sdk
  infra/docker/                 # compose + dockerfiles
  infra/terraform/              # optional IaC
  evals/
  tests/{unit,integration,load}
  scripts/{seed.ts,backfill.py}
  .github/workflows/{ci.yml,cd.yml}
  Makefile
```
Sample env vars:
- `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`
- `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`
- `DATABASE_URL`, `REDIS_URL`, `S3_BUCKET`
- `JWT_SECRET`, `OAUTH_CLIENT_ID`, `OAUTH_CLIENT_SECRET`
- `OTEL_EXPORTER_OTLP_ENDPOINT`, `MONTHLY_AI_BUDGET_USD`

Make targets: `make dev`, `make seed`, `make test`, `make load`, `make eval`, `make lint`, `make ci`.

### interview talking points
1. Why async acceptance + later completion was chosen over synchronous generation.
2. Tradeoff between strict templates vs model flexibility in medical narrative extraction.
3. How eval thresholds were tuned to minimize false confidence.
4. Cost/performance strategy via model routing and cache-hit optimization.
5. Compliance boundary: what the system automates vs what remains human decision.

### risks and mitigations
- **Risk 1:** Synthetic data overstates production quality. **Mitigation:** include adversarial cases and clinician review panel in week 2.
- **Risk 2:** Payer endpoint variability breaks integrations. **Mitigation:** abstraction adapters + contract tests + fallback manual export.

---

## Project 2 — Real-Time Merchant Risk Triage Engine (FinTech)

### one-line pitch
A streaming fraud-triage service that scores suspicious transactions in real time and routes high-risk events for AI-assisted analyst review.

### why it matters
Fraud ops teams face alert fatigue and delayed response, causing chargeback losses and customer friction. Target users are risk analysts and fraud leads; outcome is reducing false positives by **25%** while keeping decision latency under **250ms p95** for live scoring.

### differentiators vs “todo app”
- Combines low-latency rules engine with AI explanation layer instead of model-only decisions.
- Uses event-driven microservices and backpressure-aware queues.
- Includes deterministic replay for incident debugging.
- Enforces strict PII minimization and tokenized identities.
- Demonstrates cost-aware architecture by splitting real-time path from batch enrichment.

### architecture overview
```text
[Merchant Dashboard (Next.js)]
   | REST/GraphQL + JWT
   v
[Risk API (Go)] <--> [Redis feature cache]
   | \
   |  \--> [WebSocket stream for analyst console]
   |
   +--> [DynamoDB txn profile store]  +--> [S3 raw event lake]
   |
   +--> [Queue/Kafka topic] --> [Python worker: enrichment + AI rationale]
                             |--> [OpenAI/Anthropic]
                             |--> [Pinecone/Supabase vector store]

[OTel tracing + Prometheus/Grafana]
[GitHub Actions CI/CD] [Docker; optional K8s]
```
Security: schema validation, HMAC request signing, OAuth2 service-to-service tokens, rate limiting by merchant, secrets via AWS/GCP secret manager.
Cost controls: real-time path uses rules + small embedding model; expensive explanation generation only for flagged top 5% events.

### scoped feature set
**Weekend MVP**
- Ingest transaction events via REST.
- Rule-based risk scoring + thresholds.
- Queue flagged events for async enrichment.
- Analyst UI list with decision states.
- Basic WebSocket live alert feed.

**Week-2 V1**
- AI-generated rationale with retrieval from known fraud patterns.
- Replay mode for incident windows.
- Feature flags for threshold experiments.
- Merchant-level tuning + SLA dashboards.
- Chargeback outcome feedback loop for calibration.

### acceptance criteria and demo script
**Acceptance criteria**
- p95 scoring latency <250ms for 200 RPS synthetic traffic.
- Queue lag stays <30s at 1,000 events/minute.
- Analyst can approve/reject with full trace ID linkage.
- Replay reproduces score within ±1 point.

**3-minute deterministic demo**
1. Seed merchant `M-114`, load 10k historical events.
2. Start event simulator at 200 RPS.
3. Show live risk feed; trigger known attack pattern burst.
4. Open one flagged event, inspect AI rationale + similar cases.
5. Resolve event and show trace from ingest to decision.

### test plan
- Unit: scoring funcs, auth, schema checks.
- Integration: event ingestion -> queue -> worker -> persistence.
- Load: k6 at 200 RPS + burst 500 RPS for 30s.

Targets:
- p95 ingest API <120ms.
- p95 end-to-end flagged-event enrichment <8s.
- Throughput 1,000 events/min sustained.

### evals for ai behavior (if applicable)
Eval set: 5,000 labeled historical fraud events.
- Explanation factuality >= 0.92 (against feature snapshot).
- Recommended action agreement with senior analysts >= 0.80.
- No prohibited fields leakage (PII policy) = 100% pass.
CI job: `python -m evals.run --dataset data/eval.json --seed 42` and fail on threshold regressions.

### resume bullets (3)
- Delivered a real-time fraud triage platform handling **1,000 events/min** with **<250ms p95** scoring latency using Go microservices and Redis caching.
- Reduced false-positive analyst alerts by **27%** through hybrid rules + AI rationale workflow and feedback-based threshold tuning.
- Built deterministic replay and distributed tracing, cutting incident RCA time from **hours to <20 minutes**.

ATS keyword line: REST, GraphQL, WebSockets, microservices, distributed systems, message queues, DynamoDB, S3, Redis, Docker, Kubernetes, CI/CD, GitHub Actions, OAuth2, JWT, rate limiting, observability, tracing, RAG, vector DB, evaluations, caching.

### ats keyword coverage
- [x] rest
- [x] graphql
- [x] websockets
- [x] microservices
- [x] distributed systems
- [x] message queues
- [ ] postgres
- [x] dynamodb
- [x] s3
- [x] redis
- [x] docker
- [x] kubernetes
- [x] ci/cd
- [x] github actions
- [x] testing (jest/pytest)
- [x] openapi
- [x] oauth2
- [x] jwt
- [x] rate limiting
- [x] observability
- [x] opentelemetry
- [x] tracing
- [x] rag
- [x] vector db
- [x] embeddings
- [x] prompt engineering
- [x] evaluations
- [ ] agents
- [x] caching
- [x] feature flags
- [ ] infra as code (terraform optional)
- [x] aws (lambda, ec2)
- [x] gcp/azure acceptable alternatives

### repo blueprint
```text
merchant-risk-engine/
  apps/dashboard/
  services/risk-api-go/
  services/enrichment-worker-py/
  services/replay/
  packages/contracts/
  infra/docker/
  infra/k8s/
  tests/{unit,integration,load}
  evals/
  scripts/{seed_events.py,simulate.ts}
  .github/workflows/
  Makefile
```
Sample env vars:
- `DYNAMODB_TABLE_TXN`, `S3_EVENTS_BUCKET`, `REDIS_URL`
- `OPENAI_API_KEY`, `PINECONE_API_KEY`
- `JWT_SECRET`, `OAUTH_ISSUER`
- `KAFKA_BROKERS` or `SQS_QUEUE_URL`

Make targets: `make up`, `make seed`, `make simulate`, `make test`, `make load`, `make eval`.

### interview talking points
1. Real-time vs async split and why it preserves UX + cost.
2. Rules-first architecture to satisfy regulated explainability.
3. Handling hot partitions and queue backpressure.
4. How replay mode enables fast incident forensics.
5. KPI framing: fraud capture, false positives, analyst throughput.

### risks and mitigations
- **Risk 1:** Biased historical labels degrade model usefulness. **Mitigation:** calibration set + periodic human audit.
- **Risk 2:** Burst traffic overwhelms queue. **Mitigation:** autoscaling workers + circuit breaker + graceful degradation.

---

## Project 3 — Dispatch Exception Copilot (Logistics)

### one-line pitch
A logistics control-tower app that predicts shipment exceptions and auto-generates operator actions to recover SLA before customer impact.

### why it matters
Dispatch teams react late to delays, leading to missed SLAs and support volume spikes. Target users are dispatch managers and customer ops; measurable outcome is improving on-time delivery by **8–12%** and reducing manual triage time by **40%**.

### differentiators vs “todo app”
- Multi-source ingestion (telemetry, scans, weather, notes) with eventual consistency.
- Background planners prioritize actions under capacity constraints.
- AI assistant constrained by policy rules and deterministic action templates.
- Observability-first design with per-route SLOs and alerting.
- Explicit cost/latency budgets for high-volume event streams.

### architecture overview
```text
[Ops UI (Next.js + Auth.js)]
   | REST + GraphQL
   v
[Control API (TypeScript)] ---> [Postgres/Supabase]
   |        |                    [S3: scan artifacts]
   |        +--> [Redis cache]
   |
   +--> [Queue (SQS)] --> [Planner Worker (Python)] --> [OpenAI/Anthropic]
   |                        |        (light agent: detect->propose->score)
   |                        +--> [pgvector/Pinecone for route playbooks]
   |
   +--> [Webhook ingest service] <--- carriers/telematics/weather

[OpenTelemetry + Prometheus/Grafana + alert rules]
[GitHub Actions CI/CD] [Docker; optional K8s]
```
Security: signed webhooks, strict input validation, tenant isolation, secrets vault, redact driver/customer PII in prompts.
Cost controls: debounce event bursts, cache route embeddings, batch low-priority enrichments.

### scoped feature set
**Weekend MVP**
- Ingest shipment events + webhook signatures.
- Exception detection rules (delay, reroute, failed handoff).
- Queue-based action suggestion generation.
- Dispatch board with status and recommended actions.
- Basic SLA metrics panel.

**Week-2 V1**
- Playbook retrieval via vector search.
- One-click action execution (notify carrier/customer).
- Route-level forecast and confidence bands.
- Pager-style alerting + escalation policies.
- Cost dashboard (tokens per shipment, infra/day).

### acceptance criteria and demo script
**Acceptance criteria**
- Detect seeded exceptions with recall >= 0.9.
- p95 API latency <300ms under 100 concurrent users.
- Suggested actions generated within 20s for priority exceptions.
- SLA dashboard updates within 60s of event ingest.

**3-minute deterministic demo**
1. Login to tenant `west-region-demo`.
2. Run `seed:scenario storm-delay` to inject deterministic event stream.
3. Show newly flagged exceptions and ranked action suggestions.
4. Execute “rebook linehaul” suggestion and observe SLA recovery projection.
5. Open trace view for one shipment from webhook to action outcome.

### test plan
- Unit: rule engine, webhook verifier, scoring logic.
- Integration: ingest -> queue -> planner -> DB/UI.
- Load: locust scenario with 1,000 events/min + 100 operators.

Targets:
- p95 ingest API <150ms.
- p95 action suggestion completion <20s.
- 99.5% event durability (at-least-once with dedupe key).

Minimal locust:
```py
from locust import HttpUser, task, between
class OpsUser(HttpUser):
    wait_time = between(0.5, 1.5)
    @task
    def get_board(self):
        self.client.get('/v1/exceptions?tenant=west-region-demo')
```

### evals for ai behavior (if applicable)
Eval set: 300 historical disruption scenarios with expert-approved interventions.
- Action correctness >= 0.85.
- Policy compliance >= 0.98.
- “No-action-needed” precision >= 0.80 to avoid alert fatigue.
CI: `pytest evals/test_actions.py -q` using frozen snapshots + golden outputs.

### resume bullets (3)
- Architected a dispatch exception copilot across **50k+ daily shipment events**, improving projected on-time delivery by **10%** in simulation.
- Built distributed worker orchestration with dedupe keys and replay support, achieving **99.5% event durability** and stable SLA dashboards.
- Introduced policy-constrained AI action generation and eval gates, raising operator trust and reducing manual triage effort by **41%**.

ATS keyword line: REST, GraphQL, distributed systems, message queues, Postgres, S3, Redis, Docker, Kubernetes, CI/CD, GitHub Actions, OpenAPI, OAuth2, JWT, rate limiting, observability, OpenTelemetry, RAG, vector DB, prompt engineering, evaluations, agents, caching, feature flags.

### ats keyword coverage
- [x] rest
- [x] graphql
- [ ] websockets
- [x] microservices
- [x] distributed systems
- [x] message queues
- [x] postgres
- [ ] dynamodb
- [x] s3
- [x] redis
- [x] docker
- [x] kubernetes
- [x] ci/cd
- [x] github actions
- [x] testing (jest/pytest)
- [x] openapi
- [x] oauth2
- [x] jwt
- [x] rate limiting
- [x] observability
- [x] opentelemetry
- [x] tracing
- [x] rag
- [x] vector db
- [x] embeddings
- [x] prompt engineering
- [x] evaluations
- [x] agents
- [x] caching
- [x] feature flags
- [ ] infra as code (terraform optional)
- [x] aws (lambda, ec2)
- [x] gcp/azure acceptable alternatives

### repo blueprint
```text
dispatch-exception-copilot/
  apps/ops-web/
  services/control-api/
  services/planner-worker/
  services/ingest-webhooks/
  packages/{types,client,telemetry}
  tests/{unit,integration,load}
  evals/
  scripts/{seed_scenarios.ts,replay.py}
  infra/{docker,k8s,terraform-optional}
  .github/workflows/
  Makefile
```
Sample env vars:
- `DATABASE_URL`, `SUPABASE_URL`, `SUPABASE_ANON_KEY`
- `S3_BUCKET`, `REDIS_URL`, `SQS_URL`
- `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`
- `AUTH_SECRET`, `OAUTH_CLIENT_ID`, `OAUTH_CLIENT_SECRET`
- `OTEL_EXPORTER_OTLP_ENDPOINT`, `FEATURE_FLAG_PROVIDER`

Make targets: `make dev`, `make seed`, `make replay`, `make test`, `make locust`, `make eval`, `make ci`.

### interview talking points
1. Event-driven design under eventual consistency and idempotency constraints.
2. Why operator action suggestions need policy constraints, not open-ended chat.
3. SLA as a product metric tied to technical SLOs.
4. Capacity-aware planning and graceful degradation during spikes.
5. Cost governance at scale for AI in operations workflows.

### risks and mitigations
- **Risk 1:** External data quality is noisy/incomplete. **Mitigation:** confidence scoring + fallback manual override.
- **Risk 2:** Operator distrust of AI suggestions. **Mitigation:** transparent rationale, traceability, and incremental rollout.
