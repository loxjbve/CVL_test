# Telegram 第三方客户端功能实现
import asyncio
import datetime
import json

from telethon import TelegramClient, functions, types
from telethon.tl.functions.channels import JoinChannelRequest, InviteToChannelRequest, \
    GetParticipantsRequest
from telethon.tl.functions.messages import ImportChatInviteRequest
from telethon.tl.types import ChannelParticipantsSearch

import data_process as dp



# 创建会话
async def create_session(session_name, api_id, api_hash, phone_number):
    global client
    client = TelegramClient(session_name, api_id, api_hash)
    await client.connect()
    if not await client.is_user_authorized():
        sent = await client.send_code_request(phone_number)
        return sent
    else:
        return "Success"


# 登录会话
async def login(phone_number, code):
    await client.connect()
    if not await client.is_user_authorized():
        success = await client.sign_in(phone_number, code)
        client.start()
        if success:
            return success
        else:
            return "failed"
    else:
        return "failed"


# 获取群组成员
async def get_group_members(entity):
    print(f'group: {entity.title} (ID: {entity.id})')
    all_members = []
    offset = 0
    limit = 100  # 每次请求100个，tg限制
    while True:
        await asyncio.sleep(0.2)  # 增加延迟以防止请求过快
        print(f'Retrieving members, offset: {offset},ts:{datetime.datetime.now()}')
        try:
            participants = await client(GetParticipantsRequest(
                channel=entity,
                filter=ChannelParticipantsSearch(''),
                offset=offset,
                limit=limit,
                hash=0
            ))
        except Exception as e:
            print(f"Failed to retrieve members: {e}")
            break

        if not participants.users:
            print("No more users to retrieve.")
            break

        for user in participants.users:
            all_members.append({
                'id': user.id,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'phone': user.phone,
                'status': str(user.status) if user.status else None
            })

        offset += len(participants.users)

    return all_members


async def get_entity(inf):
    async with client:
        try:
            # 如果是群组链接，则先加入群组再获取entity
            if "http" in inf:
                try:
                    print("Parsing link.")
                    if "+" in inf:
                        invite_code = inf.split('+', 1)[1]
                        print(f"Invite code: {invite_code}")
                        await client(ImportChatInviteRequest(hash=invite_code))
                    else:
                        await client(JoinChannelRequest(inf))
                        print("Joined the group successfully")
                except Exception as e:
                    print(f"Failed to join the group: {e}")
                    return None
        except Exception as e:
            print(f"Failed to get entity: {e}")
            return None
        entity = await client.get_entity(inf)
        return entity


async def dump_members(group_link):
    async with client:
        try:
            # 获取entity
            entity = await get_entity(group_link)
            if entity:
                group_members = await get_group_members(entity)
                json_file = await dp.save_group_members(group_members, entity.title)
                return json_file

            print(f"joined group: {entity.title} (ID: {entity.id})")
            group_members = await get_group_members(entity)
            # 写入json
            json_file = await dp.save_group_members(group_members, entity.title)
            if json_file:
                print(f"Members data saved to {json_file}")
                return json_file
            else:
                print("Failed to retrieve members data.")
                return None
        except Exception as e:
            return "Failed to get entity: " + str(e)


async def send_msg(inf, text):
    async with client:
        try:
            entity = await client.get_entity(inf)
            await client.send_message(entity, text)
            return f"Message sent to {inf} successfully!"
        except Exception as e:
            return f"Failed to send message to {inf}: {e}"


async def reaction(usr_inf, reaction):
    async with client:
        try:
            entity = await client.get_input_entity(usr_inf)
            messages = await client.get_messages(entity, limit=1)
            last_message_id = messages[0].id
            result = await client(functions.messages.SendReactionRequest(
                peer=entity,
                msg_id=last_message_id,
                reaction=[types.ReactionEmoji(emoticon=reaction)],
                add_to_recent=True
            ))
            print(f"Reaction '{reaction}' added to the last message of {usr_inf} successfully!{result}")
        except Exception as e:
            print(f"Failed to add reaction to the last message of {usr_inf}: {e}")


async def reply_keywords(usr_inf):
    #未实现
    #+使用消息处理器实时获取实体消息
    #+提取新消息关键字并回复
    async with client:
        try:
            # 获取用户实体
            entity = await client.get_entity(usr_inf)
            # 加载关键字和回复的 JSON 文件
            with open('keyword.json', 'r', encoding='utf-8') as file:
                keyword_dict = json.load(file)
                print(keyword_dict)
            # 持续监听用户的消息
            async for message in client.iter_messages(entity):
                # 检查消息中是否包含关键字
                for keyword, reply_text in keyword_dict.items():
                    if keyword in message.text:
                        # 发送回复消息
                        await client.send_message(entity, reply_text, reply_to=message.id)
                        print(f"Replied to message from {usr_inf} with keyword '{keyword}'")
        except Exception as e:
            print(f"Failed to reply to messages from {usr_inf}: {e}")


async def invite_users(json_file, group_link):
    async with client:
        try:
            entity = await get_entity(group_link)
            with open(json_file, 'r', encoding='utf-8') as file:
                users_data = json.load(file)

            for user_data in users_data:
                user_id = user_data.get('id')
                try:
                    await client(InviteToChannelRequest(channel=entity.id, users=[user_id]))
                    print(f"Invited user {user_id} to group {entity.title}")
                except Exception as e:
                    print(f"Failed to invite user {user_id} to group {entity.title}: {e}")
        except Exception as e:
            print(f"Failed to load users data from {json_file}: {e}")
