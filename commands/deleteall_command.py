from telethon import functions
from database import *

async def main(client, logger, **kwargs):

    # print(kwargs)
    chat = kwargs['answer_to']

    # определяем, в какой поток прислана команда
    try:
        feed_id = chat.chat_id
        feed = Feed.get(Feed.feed_id == feed_id)
    except Feed.DoesNotExist:
        logger.error('Feed.DoesNotExist')
        await client.send_message(chat, 'Feed.DoesNotExist')
        feed = None
    else:
        logger.info('feed.get {}'.format(feed))

    # если поток существует
    if feed:
        logger.info('Удаляем все связанные подписки')
        try:
            forwards = Forward.delete().where(Forward.feed_id == feed_id).execute()
        except Forward.DoesNotExist:
            logger.info('ошибка удаления подписок {}'.format(feed))

        #нельзя удалять, т.к. потом хз как добавить заново
        # logger.info('Затем удаляем сам поток {}'.format(feed))
        # feed.delete_instance()
        
        response = 'Удалили все подписки'
        await client.send_message(chat, response)
        logger.info(response)


        try:
            channelEntity = await client.get_input_entity(feed_id)
        except Exception as e:
            logger.error('channelEntity ERROR: {}'.format(e))
        else:
            logger.info('Краткая сущность channelEntity {}'.format(channelEntity))

        # TODO выкинуть юзера из канала и самому удалиться
        try:
            result = await client(functions.channels.DeleteChannelRequest(
                channel=feed_id,
            ))
        except Exception as e:
            logger.error(e)

    else:
        try:
            await client.send_message(chat, 'Ошибка, обратитесь к администратору')
        except Exception as e:
            logger.error(e)

        logger.info("ошибка удаления потока")
