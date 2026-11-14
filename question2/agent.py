from __future__ import annotations

import json
from dataclasses import dataclass

from question1.agent import parse_resolution
from shared.billing import CostSession
from shared.kb import load_article
from shared.llm import ChatMessage, LlmClient
from shared.tools import format_thread, get_order, get_ticket


_ACTIONS = {"REFUND", "REPLACE", "SEND_ARTICLE", "ESCALATE_TIER2"}


@dataclass(frozen=True)
class TriageResult:
    intent: str
    candidate_articles: tuple[str, ...]


@dataclass
class TicketResolution:
    action: str
    kb_article: str


class SupportPipeline:
    """Cost-aware triage -> retrieve -> compose -> audit support pipeline.

    Cheap, deterministic nodes narrow and validate the task. The compose node is
    the only generative step, so the pipeline pays for one small LLM call rather
    than repeatedly sending a 200k-token help center between four models.
    """

    def __init__(self, session: CostSession | None = None):
        self.session = session or CostSession()
        self.llm = LlmClient(self.session)

    def handle_ticket(self, ticket_id: str) -> TicketResolution:
        ticket = get_ticket(ticket_id)
        order = get_order(ticket["order_id"])
        thread = format_thread(ticket)

        triage = self._triage(thread, order)
        articles = self._retrieve(triage)
        draft = self._compose(ticket_id, thread, order, triage, articles)
        return self._audit(draft, articles, order)

    def _triage(self, thread: str, order: dict) -> TriageResult:
        """Extract intent and shortlist article ids without a model call."""
        text = thread.lower()
        if "replace" in text or order.get("damage_reported"):
            intent = "replacement"
        elif "refund" in text or "cancel" in text:
            intent = "refund"
        else:
            intent = "policy_question"

        candidates: list[str] = []
        product_type = order.get("product_type")
        if product_type == "subscription":
            candidates.append("subscription-cooling-off")
        if product_type == "digital" or order.get("license_revealed"):
            candidates.append("digital-license-no-refund")
        if order.get("customized"):
            candidates.append("custom-items-no-replace")
        if order.get("damage_reported") and not order.get("customized"):
            candidates.append("damage-replacement-7-days")
        # This is the documented fallback for an order that matches no special case.
        candidates.append("returns-within-30-days")
        return TriageResult(intent, tuple(dict.fromkeys(candidates)))

    def _retrieve(self, triage: TriageResult) -> dict[str, str]:
        """Load only the shortlisted source articles from disk."""
        return {article_id: load_article(article_id) for article_id in triage.candidate_articles}

    def _compose(
        self,
        ticket_id: str,
        thread: str,
        order: dict,
        triage: TriageResult,
        articles: dict[str, str],
    ) -> str:
        snapshot = json.dumps(order, separators=(",", ":"))
        evidence = "\n".join(
            article.strip().replace("\n", " ") for article in articles.values()
        )
        messages = [
            ChatMessage(
                "system",
                "ShopAssist policy decision. Use only the supplied evidence. "
                "Return JSON only with action, kb_article, customer_reply (one sentence). "
                "Allowed actions: REFUND, REPLACE, SEND_ARTICLE, ESCALATE_TIER2.",
            ),
            ChatMessage(
                "user",
                f"TICKET {ticket_id}; intent={triage.intent}\n{thread}\n"
                f"EVIDENCE:\n{evidence}\n"
                f"ORDER_SNAPSHOT:{snapshot} END_SNAPSHOT",
            ),
        ]
        return self.llm.chat("compose", messages)

    def _audit(self, draft: str, articles: dict[str, str], order: dict) -> TicketResolution:
        """Validate schema, grounding, and policy eligibility without another call.

        Fail closed: a contradictory draft raises rather than silently approving
        a financial action. The caller can route that failure to human review.
        """
        parsed = parse_resolution(draft)
        if parsed.action not in _ACTIONS:
            raise ValueError(f"Unsupported action: {parsed.action}")
        if parsed.kb_article not in articles:
            raise ValueError(
                f"Article {parsed.kb_article!r} was not retrieved for this ticket"
            )
        # Ordered policy checks are independent of the generated draft. Overlapping
        # categories must respect subscription/license/custom exceptions first.
        if order.get("product_type") == "subscription":
            expected = (
                "REFUND" if int(order.get("subscription_age_days", 0)) <= 30
                else "SEND_ARTICLE", "subscription-cooling-off"
            )
        elif order.get("license_revealed"):
            expected = ("SEND_ARTICLE", "digital-license-no-refund")
        elif order.get("customized") and order.get("damage_reported"):
            expected = ("ESCALATE_TIER2", "custom-items-no-replace")
        elif (order.get("damage_reported") and not order.get("customized")
              and int(order.get("delivered_days_ago", 99)) <= 7):
            expected = ("REPLACE", "damage-replacement-7-days")
        elif (order.get("product_type") == "physical" and not order.get("opened")
              and int(order.get("delivered_days_ago", 99)) <= 30):
            expected = ("REFUND", "returns-within-30-days")
        else:
            expected = ("ESCALATE_TIER2", "returns-within-30-days")
        if (parsed.action, parsed.kb_article) != expected:
            raise ValueError("Draft conflicts with order eligibility; manual review required")
        return TicketResolution(parsed.action, parsed.kb_article)
