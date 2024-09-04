from asyncio import tasks
from asyncore import loop
import os
import asyncio
from openai import AsyncOpenAI
import sys
from pathlib import Path

# Add the parent directory to sys.path
parent_dir = str(Path(__file__).resolve().parent.parent)
sys.path.append(parent_dir)
import functions_constants as con

#config = con.MODEL_CONFIGS["LOCAL_MISTRAL7B_GRAMMAR_CORRECT"]
config = con.MODEL_CONFIGS["GPT3.5_TURBO_GENERAL"]

client = AsyncOpenAI(base_url=config['base_url'])


async def main(i) -> None:
    chat_completion = await client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"Say this is test {i}",
            }
        ],
        temperature=config["temperature"],
        model=config["model"],
    )
    resp = chat_completion.choices[0].message.content
    print(resp)
    return resp

async def run():
    tasks = []
    loop = asyncio.get_running_loop()
    for i in range(10): {
        tasks.append(asyncio.create_task(main(i)))
    }

    all = await asyncio.gather(*tasks)
    print(all)

asyncio.run(run())