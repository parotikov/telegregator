from database import *

async def main(client, logger, **kwargs):

    # print(kwargs)
    chat = kwargs['answer_to']

    feed_id = chat.chat_id
    feedupdate = Feed.update({Feed.is_enable: 1}).where(Feed.feed_id == feed_id).execute()
    await client.send_message(chat, 'Включили поток')
