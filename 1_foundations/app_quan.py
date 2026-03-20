#!/usr/bin/env python
# coding: utf-8

import requests
from dotenv import load_dotenv
import os
import json
from PyPDF2 import PdfReader
from openai import OpenAI
import gradio as gr


load_dotenv(override=True)

pushover_user=os.getenv('PUSHOVER_USER')
pushover_token=os.getenv('PUSHOVER_TOKEN')

def push(message):
    data_sending={'token':pushover_token,'user':pushover_user,'message':message}
    requests.post(url='https://api.pushover.net/1/messages.json',data=data_sending)

def record_user_info(email,name="Not provided",phone_number="Not provided"):
    push(f"Record user info of {name} with email: {email} and phone number: {phone_number}")
    return {"recorded":"sucessfully"}

def record_unanswered_question(question):
    push(f"This question was not answered :{question}")
    return {"recorded":"sucessfully"}

record_user_info_json={
        "name":"record_user_info",
        "description":"Record user info like name, email, phone number. Use this function if user want to keep in touch",
        "parameters":{
            "type":"object",
            "properties":{
                "email":{
                    "type":"string",
                    "description":"The email address of user"
                },
                "name":{
                    "type":"string",
                    "description":"Name of user"
                },
                "phone_number":{
                    "type":"string",
                    "description":"Phone number of user"
                }
            },
            "required":[
                "email"
            ],
            "additionalProperties":False
        }
    }

record_unanswered_question_json={
    "name":"record_unanswered_question",
    "description":"Record the question that cannot be anwser. Use this function when cannot answer or you do not know the answer from user",
    "parameters":{
        "type":"object",
        "properties":{
            "question":{
                "type":"string",
                "description":"The question that couldn't be answered"
            },
        },
        "required":[
            "question"
        ],
        "additionalProperties":False
    }
}


tool=[
    {"type":"function","function":record_user_info_json},
    {"type":"function","function":record_unanswered_question_json}
]

class AI_chatbot():
    def __init__(self) -> None:
        self.openai=OpenAI()

        file=PdfReader('./quan/Quan Nguyen.pdf')
        self.linkedin=''
        for page in file.pages:
            text=page.extract_text()
            if text:
                self.linkedin+=text

        with open('./quan/Summary.txt') as file:
            self.summary=file.read()

        self.name="Quan Nguyen"

    def handle_tool_calls(self,tool_calls):
        results=[]
        for tool in tool_calls:
            tool_id=tool.id
            tool_name=tool.function.name
            tool_arguments=json.loads(tool.function.arguments)
            function=globals().get(tool_name)
            result=function(**tool_arguments)
            results.append({"role":"tool",
                    "content":json.dumps(result),
                    "tool_call_id":tool_id})
        return results

    def system_prompt(self):
        return f"""You are acting as {self.name} to answer question about him in most professional way
                You will be provided CV and summary to answer to the users' question, please be faithful as possible. If you dont know the answer, just say you dont know
                Here is the CV: {self.linkedin}
                Here is the summary: {self.summary}
                With this context please chat with user, always stay in {self.name} character 
                If you don't know the answer to any question, use your record_unanswered_question tool to record the question that you couldn't answer or you do not have information, even if it's about something trivial or unrelated to career.
                If the user is engaging in discussion, try to steer them towards getting in touch via email; ask for their email and record it using your record_user_info tool
                """

    def chat(self,message,history):
        messages=[{"role":"system","content":self.system_prompt()}]+history+[{"role":"user","content":message}]
        done=False
        while not done:
            response=self.openai.chat.completions.create(model="gpt-4o-mini",messages=messages,tools=tool)
            finish_reason=response.choices[0].finish_reason
            if finish_reason=="tool_calls":
                message_=response.choices[0].message
                tool_calls=message_.tool_calls
                result=self.handle_tool_calls(tool_calls)
                messages.append(message_)
                messages.extend(result)
            else:
                done=True
        return response.choices[0].message.content


if __name__=="__main__":
    chat_bot=AI_chatbot()
    gr.ChatInterface(chat_bot.chat,type="messages").launch()




