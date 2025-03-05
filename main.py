import os
from dotenv import load_dotenv
from collections import deque
from discord import Intents, Client, Message
from openai import OpenAI

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
KEY = os.getenv('GPT_KEY')

intents = Intents.default()
intents.message_content = True
intents.members = True
client = Client(intents=intents)
gpt_client = OpenAI(api_key=KEY)
with open("prompt.txt", "r", encoding="utf-8") as f:
    PROMPT = f.read()


async def process_message(message, user_message) -> None:
    if not user_message:
        print('Intents error')
        return
    if is_private := user_message[0] == '?':
        user_message = user_message[1:]

    # extract roles
    user_roles = [role.name for role in message.author.roles if role.name not in [
        "@everyone", "Rivals"]]
    roles_string = ", ".join(user_roles) if user_roles else "Unassigned"

    try:
        response = await get_response(
            message.channel, user_message, roles_string, message.author.display_name)
        if is_private:
            await message.author.send(response)
        else:
            await message.channel.send(response)
    except Exception as e:
        print(e)


@client.event
async def on_ready() -> None:
    print(f'{client.user} is now running')


@client.event
async def on_message(message) -> None:
    if message.author == client.user:
        return

    username = str(message.author)
    user_message = message.content
    channel = str(message.channel)

    print(f'[{channel}] {username}: "{user_message}"')
    await process_message(message, user_message)


def main() -> None:
    client.run(token=TOKEN)


async def get_response(channel, user_input, roles, username) -> str:
    if not "rat bot" in user_input.lower():
        return
    else:
        message = user_input.lower()

    messages = [
        {"role": "system", "content": f"{PROMPT}\nUsername: {username}\nUser Role: {roles}"}]

    async for msg in channel.history(limit=5):
        if msg.author.bot:
            continue
        messages.append(
            {"role": "assistant", "content": msg.content})

    messages.append({"role": "user", "content": message})

    completion = gpt_client.chat.completions.create(
        model="gpt-4o-mini",
        store=True,
        messages=messages
    )
    return completion.choices[0].message.content


main()