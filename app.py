from flask import Flask, request, jsonify
import asyncio
import sys
import json
from telethon.sync import TelegramClient
from telethon.tl.types import ChannelParticipantsAdmins, ChannelParticipantCreator
from telethon.errors import ChannelInvalidError

app = Flask(__name__)

async def scrape_admins(channel_usernames):
    result = ""
    
    api_id = '16746680'
    api_hash = 'd038e172eb99839b69c39c3c25cd98cf'
    phone_number = '84569898598'
    
    # Connect to Telegram client
    client = TelegramClient('session', api_id, api_hash)
    await client.connect()
    await client.start(phone_number)

    for channel_username in channel_usernames:
        try:
            channel = await client.get_entity(channel_username)
            admins = await client.get_participants(channel, filter=ChannelParticipantsAdmins)

            admin_usernames = []
            for admin in admins:
                if admin.username:
                    username = admin.username
                    status = "Admin"
                    if isinstance(admin.participant, ChannelParticipantCreator):
                        status = "Creator"
                    group_link = f"https://t.me/{channel_username}"
                    admin_usernames.append(f"{username},{status},{group_link}")

            if admin_usernames:
                result += "\n".join(admin_usernames)
            else:
                result += f"No admin usernames found for {channel_username}"
        except ChannelInvalidError:
            result += f"Cannot fetch members for {channel_username}. Invalid channel username."
        except Exception as e:
            result += f"Error occurred while fetching members for {channel_username}: {str(e)}"

        result += "\n"

    await client.disconnect()
    return result.strip()

@app.route('/scrape_admins', methods=['POST'])
def handle_scrape_admins():
    data = request.get_json()
    if 'channel_usernames' not in data:
        return jsonify({'error': 'Invalid input'}), 400

    channel_usernames = data['channel_usernames']

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    admins = loop.run_until_complete(scrape_admins(channel_usernames))
    loop.close()

    return jsonify({'result': admins})


