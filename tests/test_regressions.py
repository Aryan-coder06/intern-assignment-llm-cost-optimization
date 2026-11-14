"""Behavioral regressions beyond the four public fixtures."""
import json

import pytest

from question1.agent import SupportCopilot, parse_resolution
from question2.agent import SupportPipeline
from shared.billing import CostSession


@pytest.mark.parametrize("age,action", [(29, "REFUND"), (30, "REFUND"), (31, "SEND_ARTICLE")])
def test_subscription_boundary(monkeypatch, age, action):
    order = {"product_type": "subscription", "subscription_age_days": age}
    for module, cls in (("question1.agent", SupportCopilot), ("question2.agent", SupportPipeline)):
        monkeypatch.setattr(module + ".get_ticket", lambda _: {
            "order_id": "new-order", "messages": [{"from": "customer", "text": "Cancel please"}]
        })
        monkeypatch.setattr(module + ".get_order", lambda _: order)
        got = cls().handle_ticket("unseen-ticket")
        assert (got.action, got.kb_article) == (action, "subscription-cooling-off")


@pytest.mark.parametrize("days,opened,damage,action,article", [
    (7, True, True, "REPLACE", "damage-replacement-7-days"),
    (8, True, True, "ESCALATE_TIER2", "returns-within-30-days"),
    (30, False, False, "REFUND", "returns-within-30-days"),
    (31, False, False, "ESCALATE_TIER2", "returns-within-30-days"),
])
def test_physical_boundaries(monkeypatch, days, opened, damage, action, article):
    order = dict(product_type="physical", delivered_days_ago=days,
                 opened=opened, damage_reported=damage, customized=False)
    monkeypatch.setattr("question2.agent.get_ticket", lambda _: {
        "order_id": "unseen", "messages": [{"from": "customer", "text": "Help"}]
    })
    monkeypatch.setattr("question2.agent.get_order", lambda _: order)
    got = SupportPipeline().handle_ticket("unseen")
    assert (got.action, got.kb_article) == (action, article)


def test_audit_rejects_wrong_action_even_with_retrieved_citation():
    pipe = SupportPipeline()
    draft = json.dumps({"action": "REFUND", "kb_article": "digital-license-no-refund"})
    with pytest.raises(ValueError, match="eligibility"):
        pipe._audit(draft, {"digital-license-no-refund": "policy"},
                    {"product_type": "digital", "license_revealed": True})


def test_audit_rejects_unretrieved_citation():
    with pytest.raises(ValueError, match="not retrieved"):
        SupportPipeline()._audit(
            '{"action":"REFUND","kb_article":"invented-policy"}', {}, {})


@pytest.mark.parametrize("text", [
    "no JSON", '{"action":null,"kb_article":"x"}',
    '{"action":"REFUND","kb_article":42}',
    '{"action":"REFUND","kb_article":"x","customer_reply":[]}',
])
def test_parser_rejects_invalid_schema(text):
    with pytest.raises(ValueError):
        parse_resolution(text)


def test_parser_handles_fences_and_unrelated_objects():
    got = parse_resolution('noise {"debug":1}\n```json\n'
                           '{"action":"refund","kb_article":"returns-within-30-days"}\n```')
    assert got.action == "REFUND"


@pytest.mark.parametrize("cls", [SupportCopilot, SupportPipeline])
def test_exactly_one_call_and_external_session(cls):
    session = CostSession()
    agent = cls(session)
    agent.handle_ticket("T-1001")
    agent.handle_ticket("T-1002")
    assert agent.session is session
    assert len(session.calls) == 2
