# chat-myself

chatglm ptuning-v2 for wechat data

## step1

按照链接教程导出微信聊天记录csv文件和通讯录csv文件，将其存放到项目目录的message_data目录下

[导出聊天记录](https://zhuanlan.zhihu.com/p/96648844)

*注意：修改教程里的IMEI为1234567890ABCDEF*

## step2
运行clean_message.py，自动清理输出聊天记录生成的多轮对话json文件

## step3
修改ptuning上的train_chat.sh脚本，运行ptuing-v2训练

