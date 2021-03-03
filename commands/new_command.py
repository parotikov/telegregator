from telethon import functions, types
from database import *

async def main(client, logger, **kwargs):

    contact = kwargs['contact'] 
    group_name = kwargs['group_name']

    if not group_name:
        group_name = 'TGFeed'

    try:
        result = await client(functions.channels.CreateChannelRequest(
            title=group_name,
            about='',
        ))
        #
        # код ниже не работает, выдает всегда ошибку Not enough users (to create a chat, for example) (caused by CreateChatRequest)
        # me = utils.get_input_peer(entity)
        # me = await client.get_input_entity('me')
        # guest = await client.get_input_entity(contact.contact_id)
        # print(me.stringify())
        # print(guest.stringify())
        # result = await client(functions.messages.CreateChatRequest(
        #     users=['me', 'parotikov', 'Telegregator'],
        #     title='Feed'
        # ))
    except Exception as e:
        logger.error(e)

    else:
        logger.info(result.stringify())
        new_chat = result.chats[0]

        logger.info("Добавили в новый поток, сохраняем в БД...")
        feed, created = Feed.get_or_create(feed_id=new_chat.id, contact_id = contact.contact_id, feed_title=new_chat.title)
        if created:
            loginfo = "зарегали новый поток {}".format(feed.id)
        else:
            loginfo = "уже есть поток {}".format(feed.id)
        logger.info(loginfo)

        response = """**Добро пожаловать!**
Это Telegretator - агрегатор телеграм-каналов.
Он умеет подписываться на каналы и группы (даже закрытые), и объединять их в общую ленту. Мы называем это поток (feed).
Для того, чтобы Телегретатор начал формировать поток, перешлите сюда сообщение из любого канала, либо воспользуетесь командами ниже.

Еще Телегрегатор умеет фильтровать сообщения по стоп-словам: таким образом вы можете избавиться от надоедливой рекламы, просто выполнив команду: /filter стоп_слово."""
        await client.send_message(new_chat, response)
        # await response_help(new_chat)

        # await client.send_message(chat, 'Создали новый канал')
        # # Добавляем юзера
        # только для чата, но создание чата не работает, см. выше ошибку Not enough users
        # result = await client(functions.messages.AddChatUserRequest(
        #     chat_id=new_chat.id,
        #     user_id=contact.contact_id,
        #     fwd_limit=10
        # ))

        logger.info('приглашаем юзера в канал')

        try:
            result = await client(functions.channels.InviteToChannelRequest(
                channel=new_chat.id,
                users=[contact.contact_id]
            ))
        except Exception as e:
            logger.error(e)
            response = str(e) + '\r\nОтключите в разделе "Конфиденциальность - Группы и каналы" запрет на приглашение Вас в группы и выполните команду new еще раз'
            await client.send_message(kwargs['answer_to'], response)
        else:
            logger.info(result.stringify())

        logger.info('даем права приглашенному юзеру')

        rights = types.ChatAdminRights(
            post_messages=True,
            add_admins=True,
            invite_users=True,
            change_info=True,
            ban_users=True,
            delete_messages=True,
            pin_messages=True,
        )

        user_peer = await client.get_input_entity(contact.contact_id)
        try:
            permission_result = await client(functions.channels.EditAdminRequest(new_chat, user_peer, rights))
        except Exception as e:
            logger.error(e)
        else:
            logger.info(permission_result.stringify())
