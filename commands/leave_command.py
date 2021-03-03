from telethon import functions
from database import *

async def main(client, logger, **kwargs):

    # print(kwargs)
    command_arg = kwargs['channel_name']
    chat = kwargs['answer_to']

    try:
        channelEntity = await client.get_input_entity(command_arg)
    except Exception as e:
        logger.error('channelEntity ERROR: {}'.format(e))
    else:
        logger.info('Краткая сущность channelEntity {}'.format(channelEntity))

    # ищем канал, указанный в команде
    try:
        channel = Channel.get(channel_id=channelEntity.channel_id)
    except Channel.DoesNotExist:
        logger.error('Channel.DoesNotExist')
    else:
        logger.info('Channel.get {}'.format(channel))

    # определяем, в какой поток прислана команда
    try:
        feed_id = chat.chat_id
        forward = Forward.get(channel = channel.channel_id, feed = feed_id)
    except Forward.DoesNotExist:
        logger.error('Forward.DoesNotExist')
        forward = None
    else:
        logger.info('Forward.get {}'.format(forward))

    # logger.info("Отписались от канала %s, подписка была %s" % (channel, forward))

    # если поток был ранее добавлен
    if forward:
        logger.info('Удаляем подписку {}'.format(forward))
        # удаляем запись о необходимости пересылки сообщений из канала в поток
        forward.delete_instance()

        # отписываемся от канала. ВАЖНО!: сейчас не надо отписываться, т.к. другие могут быть подписаны, или подписаться в будущем. ну и для истории
        # try:
        #     await client(functions.channels.LeaveChannelRequest(channelEntity))
        # except Exception as e:
        #     print(e)
        # await event.reply('Отписались от канала')
        await client.send_message(chat, 'Удалили канал из этого потока')
        logger.info("отписался от канала {}".format(channelEntity.channel_id))
    else:
        try:
            await client.send_message(chat, 'Канал не добавлен в этот поток')
        except Exception as e:
            logger.error(e)

        logger.info("не подписан на канал {}".format(channelEntity.channel_id))
