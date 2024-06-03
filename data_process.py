# 文件和数据操作功能实现
import os,json,database
async def save_group_members(members, group_title):
    # 获取当前脚本所在目录的路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 创建 /members 文件夹路径
    members_dir = os.path.join(current_dir, 'members')
    os.makedirs(members_dir, exist_ok=True)
    file_name = os.path.join(members_dir, f'{group_title}_members.json')

    with open(file_name, 'w', encoding='utf-8') as f:
        json.dump(members, f, ensure_ascii=False, indent=4)

    # 将文件信息存入数据库
    #database.dump_to_db(file_name)

    return file_name

def get_config(t):
    with open('config.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    if t == "client":
        client_config = data.get('client',{})
        api_id = client_config.get('api_id')
        api_hash = client_config.get('api_hash')
        return api_id,api_hash
    elif t == "database":
        db_config = data.get('database',{})
        db_host = db_config.get('host')
        db_user = db_config.get('user')
        db_password = db_config.get('password')
        db_database = db_config.get('database')
        db_charset = db_config.get('charset')
        return db_host,db_user,db_password,db_database,db_charset
    elif t == "bot":
        token = data.get('bot_token')
        return token

