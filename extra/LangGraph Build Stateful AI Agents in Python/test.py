from chains.notice_extraction import NOTICE_PARSER_CHAIN
from example_emails import EMAILS

response=NOTICE_PARSER_CHAIN.invoke({"message": EMAILS[0]})
print(response)
