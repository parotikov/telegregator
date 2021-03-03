from database import *

async def main(client, logger, **kwargs):

    # print(kwargs)
    message = kwargs['message']

    notification_text = '**Сообщение от админа:**\r\n' + message
    feeds = Feed.select()
    print(', '.join([str(feed.feed_id) + ' ' + str(feed.contact_id) for feed in feeds]))
    for feed in feeds:
        if feed.contact_id == 388822642:
            await client.send_message(feed.feed_id, notification_text)
