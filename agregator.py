from telethon import TelegramClient, events, sync, functions, types, utils
from telethon.tl.custom import Button
import asyncio
import os
import logging
from TelegramCommand import *
from database import *
import importlib
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger("tggt")
logger.setLevel(logging.DEBUG)

fh = logging.FileHandler("app.log")
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)

api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")
master_account = os.getenv("MASTER_ACCOUNT")
bot_token = os.getenv("BOT_TOKEN")

client = TelegramClient('telegregator_session', api_id, api_hash)

bot = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

# client.start()
# https://github.com/LonamiWebs/Telethon/blob/master/readthedocs/extra/examples/telegram-client.rst#sending-messages

async def add_contact(contact_id):
    contact, created = Contact.get_or_create(contact_id=contact_id)
    # print("add contact get or create", contact, created)
    if created:
        logger.info("зарегали нового пользователя %d" % contact.contact_id)
    else:
        logger.info("написал существующий пользователь %d" % contact.contact_id)
    return contact

# async def log(message):
#     async client.send_message(, message)

async def call_command(**kwargs):
    # print(kwargs)
    logger.info("call_command {}".format(kwargs))
    try:
        module = importlib.import_module('commands.{}_command'.format(kwargs['module']))
    except Exception as e:
        logger.error(e)
    else:
        # print(args[1:])
        await module.main(client, logger, **kwargs)

async def send_read(chat, message):
    try:
        chat_read = await client.get_input_entity(chat)
        await client.send_read_acknowledge(chat_read, message)
    except Exception as e:
        logger.error(e)

async def is_our_channel(channel_id):
    destination = await client.get_entity(channel_id)
    # logger.info(destination.stringify())
    if destination.creator:
        return True
        # TODO разобраться, почему здесь не прерывается
    else:
        return False

async def handle_message(event):
    try:
        logger.info('ищем в БД поток, где channel_id = %s' % event.message.to_id.channel_id)
        forwards = Forward.select().where(Forward.channel_id == event.message.to_id.channel_id)
        # chat = await client.get_input_entity(event.message.to_id.channel_id)
        # await client.send_read_acknowledge(chat, event.message)
        # logger.info("%s" % forwards)
    except Forward.DoesNotExist:
        logger.info('Канала нет среди пересылаемых')
        forwards = None
        return
    if not len(forwards):
        logger.info('нет подписок на этот канал')
        return

    logger.info("Нашли следующие потоки, подписанные на канал channel_id %s" % event.message.to_id.channel_id)
    logger.info(forwards)

    chat = await client.get_input_entity(event.message.to_id)
    await client.send_read_acknowledge(chat, event.message)

    for forward in forwards:
        # определяем надо ли пересылать
        try:
            feed = Feed.get(Feed.feed_id == forward.feed_id)
        except Feed.DoesNotExist:
            logger.info('Поток не найден')
            feed = None
            return

        if not feed.is_enable:
            logger.info("Поток был отключен, не пересылаем")
            return
        # Определяем создателя потока, если сообщение пришло в поток
        # logger.info('Определяем создателя потока, куда должен транслироваться канал, откуда пришло сообщение')
        log_message = 'Сообщение пришло в канал {}'.format(event.message.to_id)
        if hasattr(event.message.to_id, 'channel_id'):
            feed_id = forward.feed_id
            try:
                owner = Contact.select().join(Feed, on=(Contact.contact_id == Feed.contact_id)).where(Feed.feed_id == feed_id).get()
            except Contact.DoesNotExist:
                log_message = log_message + ', владелец канала не определен'
                owner = None
            else:
                log_message = log_message + ', id владельца канала: {}'.format(owner.contact_id)
            logger.info(log_message)
        else:
            logger.error('нет параметра event.message.to_id.chat_id')

        log_message = 'пробуем фильтровать.'
        filterlist = []
        # print('contact.contact_id %s' % contact.contact_id)

        # TODO получать для конкретного юзера. нужно будет поменять логику и порядок, перенести на 438 строку
        try:
            filters = Filter.select().where(Filter.contact_id == owner.contact_id)
        except filterlist.DoesNotExist:
            log_message = log_message + ' нет фильтров'
            filters = []
        else:
            log_message = log_message + ' найдены фильтры для юзера'
            filterlist = [filter.word.lower() for filter in filters]
        # logger.info(filterlist)
        blacklistword = filterlist + ['запрещенный', 'выиграй', 'удалю', 'читать продолжение', 'joinchat', 'подписаться', 'подписывайся', 'подпишитесь', 'переходи', 'перейти в канал', 'подписываемся', 'дамы и господа', 'автор канала']
        # logger.info(blacklistword)
        message = event.message
        message_text = message.message
        # print(message.entities)
        if message.entities:
            # print(message.entities)
            for entity in message.entities:
                # print(entity.__class__.__name__)
                if entity.__class__.__name__ == 'MessageEntityTextUrl':
                    # print(entity.url)
                    message_text = message_text + entity.url
        if message.reply_markup:
            for row in message.reply_markup.rows:
                for button in row.buttons:
                    if hasattr(button, 'url'):
                        message_text = message_text + button.url
                    if hasattr(button, 'text'):
                        message_text = message_text + button.text
        # else:
        #     print('no buttons')

        if any([word in message_text.lower() for word in blacklistword]): # ищем стоп слова во всех текстах и ссылках
            log_message = log_message + "Найдены стоп-слова, не пересылаем"
            logger.info(log_message)
            return
        logger.info(log_message)
        logger.info("Фильтры прошли, пересылаем из канала %s в поток %s" % (forward.channel_id, forward.feed_id))
        await event.message.forward_to(forward.feed_id)
        # return




logger.info('\r\n\r\n\r\n------------start client------------------')

with client, bot:
    @client.on(events.ChatAction)
    async def my_event_handler(event):

        response_message = """**Добро пожаловать!**
Это Telegretator - агрегатор телеграм-каналов.
Он умеет подписываться на каналы и группы (даже закрытые), и объединять их в общую ленту. Мы называем это поток (feed).
Для того, чтобы Телегретатор начал формировать поток, перешлите сюда сообщение из любого канала, либо воспользуетесь командами ниже. Наберите /help для списка команд

Еще Телегрегатор умеет фильтровать сообщения из оригинальных каналов по стоп-словам: таким образом вы можете избавиться от надоедливой рекламы, просто выполнив команду: /filter стоп_слово."""

        async def add_group_as_feed(feed_id, contact_id):
            logger.info("Добавляем id " + str(feed_id) + " в новый поток, сохраняем в БД...")
            feed, created = Feed.get_or_create(feed_id=feed_id, contact_id = contact_id)
            if created:
                loginfo = "зарегали новый поток {}".format(feed.id)
            else:
                loginfo = "уже есть поток {}".format(feed.id)
            logger.info(loginfo)
            # logger.info('добавился')

            await client.send_message(event.action_message.to_id, response_message)

        # logger.info("Сработал event ChatAction %s" % event.stringify())

        # original_update это уникальный атрибут при добавлении в канал. в чате(группе) такого нет
        if event.original_update:
            logger.info("user_joined to channel_id %s" % event.original_update.channel_id)
            channel = await client.get_input_entity(event.original_update.channel_id)
            logger.info("channel joined %s" % channel)
            ## TODO здесь прерывается приглашение по инвайту
            
            # result = client(functions.channels.GetParticipantsRequest(
            #     channel=channel,
            #     filter=types.ChannelParticipantsRecent(),
            #     # offset=42,
            #     limit=100,
            #     hash=0
            # ))
            # logger.info("GetParticipantsRequest %s" % result.stringify())
            channel_admin = False
            async for user in client.iter_participants(channel, filter=types.ChannelParticipantsAdmins):
                logger.info("user %s" % user)
                if user.is_self:
                    channel_admin = True
                else:
                    owner = user
                    logger.info("owner is %s" % owner)

            logger.info("Is Telegregator admin? %s" % channel_admin)
            if(channel_admin):
                await client.send_message(channel, response_message)
            # добавляем владельца в контакты
            if owner:
                contact = await add_contact(owner.id)

            # tggt добавили в канал (публичный и приватный)
            if channel_admin:
                await add_group_as_feed(feed_id=event.original_update.channel_id, contact_id=contact.contact_id)
                
        # для группы это
        #     to_id=PeerChat(
        #     chat_id=476968657
        # ),
        # для канала это 
        #     to_id=PeerChannel(
        #     channel_id=1278799151
        # ),


        logger.info("action_message %s" % event.action_message)
        logger.info("action_message.from_id %s" % event.action_message.from_id)

        ## Определяем кто к нам постучался
        # для группы (чата)
        if event.action_message.from_id:
            contact = await add_contact(event.action_message.from_id)

        # tggt добавили в чат (группу)
        if event.action_message.action.__class__.__name__ in ['MessageActionChatAddUser', 'MessageActionChatCreate']:
            await add_group_as_feed(feed_id=event.action_message.to_id.chat_id, contact_id=contact.contact_id)
        
        # tggt удаляют из чата
        if(event.action_message.action.__class__.__name__ == 'MessageActionChatDeleteUser'):
            logger.info("Удалили из потока, обновляем в БД...")
            feed = Feed.delete().where(Feed.feed_id == event.action_message.to_id.chat_id).execute()
            logger.info(feed)

    @client.on(events.NewMessage)
    async def my_event_handler(event):
        # отладка
        logger.info("\r\n\r\n\r\n-------------Новое сообщение----------------")
        logger.info(event.message.stringify())
        # logger.info(event.message)

        ## Определяем кто к нам постучался
        if event.message.from_id:
            contact = await add_contact(event.message.from_id)

        # личка бота
        management = 0
        handled = 0

        if hasattr(event.message.to_id, 'channel_id'):
            handled = 1
            # logger.info('сообщение пришло в канал (тип channel_id), нужно обрабатывать для пересылки')

            try:
                chat = await client.get_input_entity(event.message.to_id)
            except Exception as e:
                logger.error(e)

        if hasattr(event.message.to_id, 'user_id'):
            if event.message.to_id.user_id == 887053090 or event.message.to_id.user_id == None:
                logger.info("сообщение в личку телегрегатора, обрабатывать как управляющую команду")
                management = 1
                try:
                    chat = await client.get_input_entity(event.message.from_id)
                    await client.send_read_acknowledge(chat, event.message)
                except Exception as e:
                    logger.error(e)
            else:
                try:
                    chat = await client.get_input_entity(event.message.to_id)
                except Exception as e:
                    logger.error(e)
        if hasattr(event.message.to_id, 'chat_id'):
            logger.info('сообщение в группу (chat_id) %s, нужно обрабатывать как команду' % event.message.to_id.chat_id)
            try:
                chat = await client.get_input_entity(event.message.to_id)
            except Exception as e:
                logger.error(e)

        if hasattr(event.message.to_id, 'channel_id'):
            logger.info('сообщение в канал (channel_id) %s, нужно обрабатывать как команду' % event.message.to_id.channel_id)

            try:
                chat = await client.get_input_entity(event.message.to_id)
            except Exception as e:
                logger.error(e)

            # для отладки, пересылаем сообщение админу (удалить таб, чтобы пересылать все. сейчас только команды в чат, см. проверку на строке 270)
            await event.message.forward_to(master_account)

        # mark message as read
        await client.send_read_acknowledge(chat, event.message)

        #Парсим команду
        command_handler = TelegramCommand()
        command, command_arg = command_handler.parseMessage(event.message.message)
        # если распознана команда
        if command:
            # прочитали
            await send_read(event.message.from_id, event.message)

            chat_command = command
            logger.info('Команда: {}, аргумент: {}'.format(chat_command, command_arg))
            # message = 'I see chat_command "{}" and channel name is "{}"'.format(chat_command, command_arg)
            # await client.send_message(chat, message)
            # на присоединение к каналу
            if chat_command == 'help':
                await call_command(module='helpmessage', answer_to=chat)
            if chat_command == 'new':
                await call_command(module='new', answer_to=chat, contact=contact, group_name = command_arg)
            if chat_command == 'test':
                await call_command(module='test')
            if chat_command in ['join', 'add']:
                channels_list = command_arg.split(' ')
                for channel in channels_list:
                    await call_command(module='join', answer_to=chat, channel_name=channel)
            # на описку от канала
            if chat_command in ['leave', 'remove', 'delete']:
                channels_list = command_arg.split(' ')
                for channel in channels_list:
                    await call_command(module='leave', answer_to=chat, channel_name=channel)
            # на список подписанных каналов
            if chat_command == 'list':
                await call_command(module='listchannels', answer_to=chat, feed_id=event.message.to_id.chat_id)
            ## Вкл/выкл поток
            if chat_command in ['stop', 'pause']:
                await call_command(module='stop', answer_to=chat)
            if chat_command in ['start', 'resume']:
                await call_command(module='start', answer_to=chat)
            if chat_command in ['deleteall', 'exit']:
                await call_command(module='deleteall', answer_to=chat)
            ## Фильтры и стоп слова
            if chat_command == 'filter':
                await call_command(module='filter', answer_to=chat, word = command_arg, contact_id = contact.contact_id)
            if chat_command == 'filterremove' or chat_command == 'removefilter' or chat_command == 'unfilter':
                await call_command(module='unfilter', answer_to=chat, word = command_arg, contact_id = contact.contact_id)
            if chat_command == 'filterlist':
                await call_command(module='filterlist', answer_to=chat, contact_id = contact.contact_id)
            if chat_command == 'filterclear' or chat_command == 'clearfilter':
                await call_command(module='filterclear', answer_to=chat, contact_id = contact.contact_id)
            if chat_command == 'filterstop' or chat_command == 'stopfilter':
                await call_command(module='filterstop', answer_to=chat)
            if chat_command == 'filterstart' or chat_command == 'sartfilter':
                await call_command(module='filterstart', answer_to=chat)
            if chat_command == 'message':
                await call_command(module='message', message=command_arg)


            # if chat_command == 'all':
            #     print('all')
            #     await client.send_message(chat, 'Подписаны на следующие каналы:\r\n{}'.format('\r\n'.join([str(dialog.name) for dialog in client.iter_dialogs()])))

        # если в сообщении нет команды
        if management:
            pass

        # если переслали сообщение
        # if event.message.fwd_from and event.message.fwd_from.channel_id and event.message.from_id == 388822642:
        if event.message.fwd_from and event.message.fwd_from.channel_id and event.message.to_id.__class__.__name__ == 'PeerChat':
            logger.info("Вижу репост канала в группу")
            try:
                channelInfo = await client.get_entity(event.message.fwd_from.channel_id)
            except Exception as e:
                logger.error(e)
                logger.error("не можем получить channelInfo для канала %s" % event.message.fwd_from.channel_id)
                channelInfo = None
                # logger.info("не можем получить channelInfo для канала %s" % channelEntity)
                await event.reply('не могу подписаться. Если канал закрытый, попробуйте по инвайту')
            else:

                # print(event.message.to_id.__class__.__name__)
                channelEntity = await client.get_input_entity(event.message.fwd_from.channel_id)
                logger.info('channelEntity {}'.format(channelEntity))
                logger.info("Репост канала {} (@{}), id {}".format(channelInfo.title, channelInfo.username, channelInfo.id))
                await call_command(module='join', answer_to=chat, channel_name=channelInfo.username)
        

        if event.message.fwd_from and event.message.fwd_from.channel_id and event.message.to_id.__class__.__name__ == 'PeerChannel':
            logger.info("Вижу репост канала в канал")
            try:
                channelInfo = await client.get_entity(event.message.fwd_from.channel_id)
            except Exception as e:
                logger.error(e)
                logger.error("не можем получить channelInfo для канала %s" % event.message.fwd_from.channel_id)
                channelInfo = None
                # logger.info("не можем получить channelInfo для канала %s" % channelEntity)
                await event.reply('не могу подписаться. Если канал закрытый, попробуйте по инвайту')
            else:

                # print(event.message.to_id.__class__.__name__)
                channelEntity = await client.get_input_entity(event.message.fwd_from.channel_id)
                logger.info('channelEntity {}'.format(channelEntity))
                logger.info("Репост канала {} (@{}), id {}".format(channelInfo.title, channelInfo.username, channelInfo.id))
                await call_command(module='join', answer_to=chat, channel_name=channelInfo.username)


        if handled:
            is_our = await is_our_channel(event.message.to_id)
            if not is_our:
                log_message = 'не мы'
                await handle_message(event)
            else:
                log_message = 'мы, сообщение нужно обрабатывать как команду'
                # TODO проверять написавшего админа, возможно это репост для добавления канала в поток
            
            logger.info("проверим кто создатель канала: " + log_message)


    client.start()
    # client.send_message(master_account, message='test', buttons=[['test']])
    client.send_message(master_account, 'Telegregator is online!')
    # https://telethon.readthedocs.io/en/latest/modules/client.html#telethon.client.buttons.ButtonMethods
    # https://github.com/LonamiWebs/Telethon/blob/e47f3ec1d6db80964054bfe438c473c42f75392c/telethon/tl/custom/button.py
    # markup = bot.build_reply_markup([
    # Button.switch_inline('/1', query='123', same_peer=True),
    # Button.switch_inline('/2', query='321', same_peer=True),
    # Button.switch_inline('/3', query='333', same_peer=True)
    # ])
    # bot.send_message(-319949754, 'select command', buttons=markup)
    client.run_until_disconnected()
