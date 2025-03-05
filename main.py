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

    role = extract_role(message.author)

    try:
        response = await get_response(
            message.channel, user_message, role, message.author.display_name)
        if response and response.strip():
            if is_private:
                await message.author.send(response)
            else:
                await message.channel.send(response)
    except Exception as e:
        print(e)


@client.event
async def on_ready() -> None:
    client.members_dict = {}

    for guild in client.guilds:
        print(f"Connected to {guild.name}")
        client.members_dict[guild.id] = {}

        members = guild.members

        for member in members:
            role = extract_role(member)
            if role not in client.members_dict[guild.id]:
                client.members_dict[guild.id][role] = []

            client.members_dict[guild.id][role].append(member.display_name)


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
    member_info = "\n".join(
        [f"{role}: {', '.join(members)}" for role, members in client.members_dict[channel.guild.id].items()])

    if not "rat bot" in user_input.lower():
        return
    else:
        message = user_input.lower()
    
    messages = [
        {"role": "system", "content": f"{PROMPT}\nUsername: {username}\nUser Role: {roles}\nCurrent Members and Their Roles:\n{member_info}"}
    ]

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


def extract_role(user):
    role_priority = ["CEO", "Executives",
                     "Shareholders", "Interns", "Employees"]

    valid_roles = [role.name for role in user.roles if role.name not in [
        "@everyone", "Rivals", "Rat Bot"]]
    assigned_role = "Unassigned"
    for role in role_priority:
        if role in valid_roles:
            assigned_role = role
            return assigned_role


main()
