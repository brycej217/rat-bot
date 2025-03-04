import os
from dotenv import load_dotenv
from discord import Intents, Client, Message
from responses import get_response

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
print(TOKEN)

intents = Intents.default()
intents.message_content = True
client = Client(intents=intents)

async def process_message(message, user_message) -> None:
    if not user_message:
        print('Intents error')
        return
    if is_private := user_message[0] == '?':
        user_message = user_message[1:]
    
    try:
        response = get_response(user_message)
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
    
main()