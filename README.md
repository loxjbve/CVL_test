bot.py:实现bot功能,bot暂作为client服务临时前端
tg.py:实现client功能
data_process.py:实现数据处理
database.py:实现数据库功能
main.py:未完成，仅作为bot启动器
cpt.py:实现crypto market功能
config.json:全局配置
keyword.json:关键词配置
/group_msg:保存聊天记录
/members:保存群组成员列表

todolist:
+bot群管功能
+实现LLM接入,搭配langchain培养炒作语料
+实现更多crypto market功能
+将tg.py的功能api化以便后续开发
+使用者鉴权
+用户群组关系分析
+标记高价值用户
+用db保存msg，避免json文件读取的性能问题
