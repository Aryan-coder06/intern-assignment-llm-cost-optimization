from __future__ import annotations

import json
from dataclasses import dataclass

from shared.billing import CostSession
from shared.llm import ChatMessage, LlmClient
from shared.tools import format_thread, get_order, get_ticket


@dataclass
class TicketResolution:
    action: str
    kb_article: str
    customer_reply: str
    raw_completion: str


def parse_resolution(text: str) -> TicketResolution:
    decoder = json.JSONDecoder()
    data = None
    for index, char in enumerate(text):
        if char != "{":
            continue
        try:
            candidate, _ = decoder.raw_decode(text[index:])
        except json.JSONDecodeError:
            continue
        if isinstance(candidate, dict) and {"action", "kb_article"} <= candidate.keys():
            data = candidate
            break
    if data is None:
        raise ValueError(f"No resolution JSON in model output:\n{text[:400]}")
    return TicketResolution(
        action=str(data["action"]).upper(),
        kb_article=str(data["kb_article"]),
        customer_reply=str(data.get("customer_reply", "")),
        raw_completion=text,
    )


_POLICY = """Choose one action and its exact article id:
- subscription: age<=30 REFUND, otherwise SEND_ARTICLE; subscription-cooling-off
- revealed digital license: SEND_ARTICLE; digital-license-no-refund
- damaged+customized: ESCALATE_TIER2; custom-items-no-replace
- damaged+not customized+delivered<=7d: REPLACE; damage-replacement-7-days
- physical+unopened+delivered<=30d: REFUND; returns-within-30-days
- otherwise: ESCALATE_TIER2; returns-within-30-days
Return JSON only: action, kb_article, customer_reply. Keep the reply to one sentence."""


class SupportCopilot:
    """
    Cost-aware ShopAssist Tier-1 copilot.

    Given a support ticket + order snapshot, choose an action, cite the help-center
    article, and draft the customer reply.
    """

    def __init__(self, session: CostSession | None = None):
        self.session = session or CostSession()
        self.llm = LlmClient(self.session)

    def build_messages(self, ticket_id: str) -> list[ChatMessage]:
        ticket = get_ticket(ticket_id)
        order = get_order(ticket["order_id"])
        thread = format_thread(ticket)
        # Compact JSON preserves every order fact while avoiding whitespace tokens.
        snapshot = json.dumps(order, separators=(",", ":"))
        user = (
            f"TICKET {ticket_id}\n{thread}\n"
            f"ORDER_SNAPSHOT:{snapshot} END_SNAPSHOT"
        )
        return [ChatMessage("system", _POLICY), ChatMessage("user", user)]

    def handle_ticket(self, ticket_id: str) -> TicketResolution:
        messages = self.build_messages(ticket_id)
        completion = self.llm.chat("handle_ticket", messages)
        return parse_resolution(completion)
