from openai import OpenAI
import os
open_ai_api=os.environ.get("OPENAI_API_KEY")
open_ai_url=os.environ.get("OPENAI_API_BASE_URL")
client=OpenAI(api_key=open_ai_api,base_url=open_ai_url)
conversation_history=[]
def generate_text(prompt):#简单的模型历史对话
    conversation_history.append({"role":"user","content":prompt})
    response=client.chat.completions.create(model="gpt-4",
                                            messages=conversation_history,
                                            temperature=0.5,
                                            max_tokens=500)
    
    return response.choices[0].message.content
