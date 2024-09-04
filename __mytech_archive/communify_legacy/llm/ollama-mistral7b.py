

from langchain_community.llms import Ollama
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from langchain.schema.runnable import Runnable
from langchain.schema.runnable.config import RunnableConfig

import chainlit as cl

Model_Name = "Mistral 7B"
Model_Key = "mistral"
AI_Name = "Community (Mistral7B)"
Avatar_Path="communify.png"
system_prompt =  """You are incredibly knowledgeable of wealth managementfinancial services, investment management, and the stock market. 
                You are extremely helpful, and share accurate and eloquent answers to questions about these topics.
                You also always try to provide the most accurate and helpful information to the best of your ability.
                And also provide relevant and insightful information about topics related to questions you receive."""

@cl.on_chat_start
async def on_chat_start():
    
    await cl.Avatar(
        name=AI_Name,
        path=Avatar_Path,
    ).send()
    
    await cl.Message(content= f"Hello there, I am {AI_Name} and am powered by {Model_Name}. How can I help you ?").send()
    
    # Below is how the AI sends an image
    #await cl.Message(content= f"Hello there, I am {AI_Name} and am powered by {Model_Name}. How can I help you ?", elements=elements).send()

    
    # await cl.Message(content="Hello there, I am Gemma. How can I help you ?", elements=elements).send()
    model = Ollama(model="Model_Key")
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                system_prompt,
            ),
            ("human", "{question}"),
        ]
    )
    runnable = prompt | model | StrOutputParser()
    cl.user_session.set("runnable", runnable)


@cl.on_message
async def on_message(message: cl.Message):
    runnable = cl.user_session.get("runnable")  # type: Runnable

    msg = cl.Message(content="")

    async for chunk in runnable.astream(
        {"question": message.content},
        config=RunnableConfig(callbacks=[cl.LangchainCallbackHandler()]),
    ):
        await msg.stream_token(chunk)

    await msg.send()



