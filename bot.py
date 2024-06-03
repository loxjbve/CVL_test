from telegram import Update,ChatMember
from telegram.ext import CommandHandler, CallbackContext, ApplicationBuilder,MessageHandler,filters

# 引入 tg.py 中的函数
import json
import os
import tg
import data_process as dp

KEYWORD_FILE = 'keyword.json'
client_status = 0
GROUP_MSG_FOLDER = "group_msg/"
CHAT_MSG_FORMAT = "{}.json"

# 通过bot登录真人账号
async def create_session_handler(update: Update, context: CallbackContext):
    global client_status  # Declare client_status as global

    args = context.args
    # 检查参数长度是否符合要求
    if len(args) != 4:
        await update.message.reply_text("Usage: /create_session <session_name> <api_id> <api_hash> <phone_number>")
        return

    session_name, api_id, api_hash, phone_number = args
    print(phone_number)

    # 调用 tg.create_session 函数创建会话
    session_created = await tg.create_session(session_name, api_id, api_hash, phone_number)

    # 返回结果给用户
    if session_created:
        if session_created == "Success":
            await update.message.reply_text(f"已使用存在的会话 {session_name}")
            client_status = 1
        else:
            await update.message.reply_text(f"成功创建会话 {session_name},{session_created}")
    else:
        await update.message.reply_text("创建会话失败")


async def login_session_handler(update: Update, context: CallbackContext):
    global client_status  # Declare client_status as global
    # 解析命令参数
    args = context.args
    if len(args) != 2:
        await update.message.reply_text("Usage: /login <phone_number> <code>")
        return

    phone_number, code = args

    # 调用 create_session 函数创建会话
    login_success = await tg.login(phone_number, code)

    # 返回结果给用户
    if login_success:
        await update.message.reply_text(f"成功登录 {phone_number},{login_success}")
        client_status = 1
    else:
        await update.message.reply_text("登录失败")


async def send_msg(update: Update, context: CallbackContext):
    global client_status  # Declare client_status as global
    if client_status != 1:
        await update.message.reply_text("请先登录")
        return
    else:
        args = context.args
        if len(args) != 2:
            await update.message.reply_text("Usage: /send <usrname> <text>")
            return
        usrname, text = args
        # print(usrname,text)
        reply = await tg.send_msg(usrname, text)
        # print(reply)
        if reply:
            await update.message.reply_text(reply)
        else:
            await update.message.reply_text("发送失败")

async def peep(update: Update, context: CallbackContext):
    #未完成
    await update.message.reply_text("持续视奸消息中👁")

async def dump(update: Update, context: CallbackContext):
    #未完成
    await update.message.reply_text("数据库已同步聊天记录缓存")


async def set_keyword_reply(update: Update, context: CallbackContext):
    # 通过bot对话设置关键词
    # 获取命令参数
    args = context.args
    if len(args) != 2:
        await update.message.reply_text('Usage: /set_keyword_reply <keyword> <reply>')
        return
    keyword, reply = args
    if os.path.exists('keyword.json') and os.stat('keyword.json').st_size != 0:
        with open('keyword.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
    else:
        data = {}

    data[keyword] = reply

    with open('keyword.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

    await update.message.reply_text(f'Keyword "{keyword}" set with reply "{reply}"')



async def list_keyword_reply(update: Update, context: CallbackContext):
    # 通过机器人查看关键词-回复
    with open(KEYWORD_FILE, 'r', encoding='utf-8') as f:
        keywords = json.load(f)
    reply_message = '\n'.join([f'{keyword}: {reply}' for keyword, reply in keywords.items()])

    await update.message.reply_text(reply_message)


async def set_reply_handler(update: Update, context: CallbackContext):
    # 通过机器人设置指定的回复对象
    args = context.args
    if len(args) != 1:
        await update.message.reply_text("Usage: /set_reply <usrname>")
        return
    else:
        await tg.reply_keywords(args[0])
        await update.message.reply_text("成功！")

async def save_message(update: Update, context: CallbackContext):
    # 视奸消息
    message = update.message
    chat_id = message.chat.id
    chat_title = message.chat.title
    message_id = message.message_id
    sender = message.from_user
    sender_id = sender.id
    sender_firstname = sender.first_name
    sender_lastname = sender.last_name
    sender_name = sender.username if sender.username else sender_firstname

    # 如果对话标题为 None，则使用发送者的姓名命名文件
    if chat_title is None:
        chat_title = f"{sender_firstname}_{sender_lastname}"

    msg_data = {
        "message_id": message_id,
        "sender_id": sender_id,
        "sender_firstname": sender_firstname,
        "sender_lastname": sender_lastname,
        "sender_name": sender_name,
        "timestamp": message.date.timestamp(),
        "text": message.text
    }
    file_path = GROUP_MSG_FOLDER + CHAT_MSG_FORMAT.format(chat_title)

    # 读取已有的对话记录
    try:
        with open(file_path, "r",encoding="utf-8") as file:
            chat_data = json.load(file)
    except FileNotFoundError:
        chat_data = []

    # 将新消息添加到对话记录中
    chat_data.append(msg_data)

    # 将更新后的对话记录写入文件
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(chat_data, file, indent=4,ensure_ascii=False)



async def run():
    # 初始化 Bot
    token = dp.get_config("bot")
    app = ApplicationBuilder().token(token).build()

    # 添加命令处理器


    #app.add_handler(CommandHandler("create_session", create_session_handler))
    #app.add_handler(CommandHandler("login", login_session_handler))
    #app.add_handler(CommandHandler("send", send_msg))
    #app.add_handler(CommandHandler("set_keyword", set_keyword_reply))
    #app.add_handler(CommandHandler("list_keyword", list_keyword_reply))
    #app.add_handler(CommandHandler("set_reply_handler", set_reply_handler))

    app.add_handler(CommandHandler("peeping", peep))
    app.add_handler(CommandHandler("dump_to_db", dump))
    app.add_handler(MessageHandler(filters.ALL, save_message))
    # 启动 Bot
    app.run_polling()


run()
