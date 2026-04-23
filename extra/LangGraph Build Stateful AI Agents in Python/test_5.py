from graphs.notice_extraction import NOTICE_EXTRACTION_GRAPH
from example_emails import EMAILS

initial_state_escalation = {
      "notice_message": EMAILS[0],
      "notice_email_extract": None,
      "escalation_text_criteria": """Workers explicitly violating safety
                                  protocols""",
      "escalation_dollar_criteria": 100_000,
      "requires_escalation": False,
      "escalation_emails": ["brog@abc.com", "bigceo@company.com"],
 }

results = NOTICE_EXTRACTION_GRAPH.invoke(initial_state_escalation)

print(results["follow_ups"])