from database import *

async def main(client, logger, **kwargs):
    # print(kwargs)
    chat = kwargs['answer_to']
    contact_id = kwargs['contact_id']

    filters = Filter.delete().where(Filter.contact_id == contact_id)
    deleted = filters.execute()
    response = '**Удалено фильтров**:\r\n' + str(deleted)

    await client.send_message(chat, response)
    logger.info(response)
