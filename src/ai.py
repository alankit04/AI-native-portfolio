import os
from typing import List, Tuple


def naive_retrieve(chunks: List[str], query: str) -> List[str]:
    q = set(query.lower().split())
    scored: List[Tuple[int, str]] = []
    for c in chunks:
        score = len(q.intersection(set(c.lower().split())))
        scored.append((score, c))
    scored.sort(reverse=True, key=lambda x: x[0])
    return [c for _, c in scored[:3]]


def _llm_draft(patient_name: str, payer: str, evidence: List[str]) -> str | None:
    provider = os.getenv("LLM_PROVIDER", "none").lower()
    prompt = (
        "You are a clinical prior authorization assistant. "
        "Write a concise prior auth draft using only provided evidence.\n"
        f"Patient: {patient_name}\nPayer: {payer}\nEvidence:\n" + "\n".join(f"- {e}" for e in evidence)
    )

    if provider == "openai":
        try:
            from openai import OpenAI
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            res = client.responses.create(model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"), input=prompt)
            return res.output_text
        except Exception:
            return None

    if provider == "anthropic":
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
            msg = client.messages.create(
                model=os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-latest"),
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}],
            )
            return "".join([b.text for b in msg.content if hasattr(b, "text")])
        except Exception:
            return None

    return None


def generate_prior_auth_draft(patient_name: str, payer: str, chunks: List[str]) -> tuple[str, list[str]]:
    evidence = naive_retrieve(chunks, "medical necessity diagnosis treatment imaging prior failed")
    model_draft = _llm_draft(patient_name, payer, evidence)
    if model_draft:
        return model_draft.strip(), evidence

    bullets = "\n".join([f"- {e[:200]}" for e in evidence]) if evidence else "- No supporting notes provided"
    draft = (
        f"Prior Authorization Request for {patient_name}\n"
        f"Payer: {payer}\n\n"
        "Clinical Summary:\n"
        "The requested service is medically necessary based on documented symptoms, prior failed conservative treatment, and clinician assessment.\n\n"
        "Supporting Evidence:\n"
        f"{bullets}\n\n"
        "Request: expedited review and approval."
    )
    return draft, evidence
