from telethon import functions
from database import *
import re

async def main(client, logger, **kwargs):

    # print(kwargs)
    command_arg = kwargs['channel_name']
    chat = kwargs['answer_to']

    # определяем по имени канала его краткую сущность
    try:
        channelEntity = await client.get_input_entity(command_arg)
    except Exception as e:
        logger.error('channelEntity ERROR: {}'.format(e))
        channelEntity = None
    else:
        logger.info('Краткая сущность channelEntity {}'.format(channelEntity))

    # https://t.me/joinchat/AAAAAFJZZ_f91J_H7ht4GQ
    # TODO добавить обработку инвайтов: https://telethon.readthedocs.io/en/latest/examples/chats-and-channels.html
    # если вместо названия передали инвайт ссылку
    if 'joinchat' in command_arg:
        logger.info('прислали инвайт-ссылку {}'.format(command_arg))
        invite = re.search('([^\/]+)\/?$', command_arg)
        # invite = command_arg.split("/")[-1]

        logger.info('инвайт - %s' % invite[0])
        try:
            logger.info('пробуем подписаться на закрытый канал по инвайту {}'.format(invite[0]))
            updates = await client(functions.messages.ImportChatInviteRequest(invite[0]))
            # TODO остановился на этом
            # https://docs.telethon.dev/en/latest/examples/chats-and-channels.html?highlight=private#joining-a-private-chat-or-channel
            # await asyncio.sleep(1)
        except Exception as e:
            logger.error('ImportChatInviteRequest: {}'.format(e))
            updates = None
        else:
            logger.info('подписались, updated {}'.format(updated))

    # определяем по имени канала его полную сущность. Для закрытых не сработает, там надо сначала подписаться
    try:
        channelFullEntity = await client.get_entity(command_arg)
    except Exception as e:
        logger.error('channelFullEntity ERROR: {}'.format(e))
        channelFullEntity = None
    else:
        logger.info('Полная сущность channelFullEntity {} {}'.format(channelFullEntity.title, channelFullEntity.username))



    # Добавляем в аккаунт
    # добавляем канал в систему (InputPeerChat,InputPeerChannel, 'string'
    try:
        await client(functions.channels.JoinChannelRequest(channelEntity))
    except Exception as e:
        logger.error(e)
    else:
        logger.info("Отправили запрос JoinChannelRequest {}".format(channelEntity.channel_id))

        # в случае успешного добавления канала в аккаунт, сохраняем его в бд с полученным названием
        try:
            channel, is_channel_joined = Channel.get_or_create(channel_id=channelEntity.channel_id, channel_name=channelFullEntity.username or command_arg, channel_title=channelFullEntity.title)
            if is_channel_joined:
                loginfo = "Сохранили канал {} {} {} в БД".format(channel.channel_title, channel.channel_name, channel.channel_id)
            else:
                loginfo = "Канал {} {} {} уже добавлен в БД".format(channel.channel_title, channel.channel_name, channel.channel_id)
                logger.info(loginfo)
        except Exception as e:
            logger.error(e)


    # теперь добавляем канал в поток, где была выполнена команда join

    logger.info("chat {}".format(chat.stringify()))

    # для группы (чата)
    if hasattr(chat, 'chat_id'):
        feed_id = chat.chat_id
        logger.info("Теперь сохраним chat_id как feed_id %s в БД Forward" % feed_id)


    #для канала
    if hasattr(chat, 'channel_id'):
        feed_id = chat.channel_id
        logger.info("Теперь сохраним channel_id как feed_id %s в БД Forward" % feed_id)

    # print(chat.stringify())

    try:
        forward, forward_created = Forward.get_or_create(channel_id=channel.channel_id, feed_id=feed_id)
        if forward_created:
            response = 'Добавили канал {} ({}) в этот поток'.format(channel.channel_title, channel.channel_name)
        else:
            response = 'Канал {} ({}) уже добавлен в этот поток'.format(channel.channel_title, channel.channel_name)

        logger.info(response)

        await client.send_message(chat, response)

    except Exception as e:
        logger.error(e)
    else:
        logger.info("не получилось обработать {}".format(channel.channel_id))


    

    
