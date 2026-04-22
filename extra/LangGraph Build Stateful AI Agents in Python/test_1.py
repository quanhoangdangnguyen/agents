from chains.escalation_check import ESCALATION_CHECK_CHAIN

escalation_criteria = """There is currently water damage
or potential water damage reported"""

message = """Several cracks in the foundation have
been identified along with water leaks"""

respone=ESCALATION_CHECK_CHAIN.invoke(
    {"message": message, "escalation_criteria": escalation_criteria}
)
print(respone)

message = "The wheel chair ramps are too steep"

respone=ESCALATION_CHECK_CHAIN.invoke(
    {"message": message, "escalation_criteria": escalation_criteria}
)
print(respone)
