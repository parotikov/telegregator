from telethon import functions
from database import *

async def main(client, logger, **kwargs):
    try:
        # TODO оптимизировать в один запрос через join
        forwards = Forward.select(Forward.channel_id).where(Forward.feed_id == kwargs['feed_id'])
    except Forward.DoesNotExist:
        logger.info('Sender is not in forwarded channels')
        forwards = None
    else:
        logger.info("forwarding...")

        feed_channels = Channel.select().where(Channel.channel_id << forwards)
        feed_list = 'Подписаны на следcующие каналы:\r\n{}'.format('\r\n'.join([channel.channel_title + ' @' + channel.channel_name for channel in feed_channels]))
        logger.info('отправляем юзеру список его подписок')
        logger.info(feed_list)
        await client.send_message(kwargs['answer_to'], feed_list)
        # https://lonamiwebs.github.io/Telethon/methods/messages/forward_messages.html
        # https://telethon.readthedocs.io/en/latest/extra/examples/telegram-client.html?highlight=forward#forwarding-messages
        # https://prosto-tak.ru/adminer/?sqlite=&username=&db=%2Fvar%2Fdb%2Fcontacts.db&select=favorite
