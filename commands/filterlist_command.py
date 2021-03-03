from database import *

async def main(client, logger, **kwargs):
    # print(kwargs)
    chat = kwargs['answer_to']
    contact_id = kwargs['contact_id']

    filters = Filter.select().where(Filter.contact_id == contact_id)
    filterlist = [filter.word.lower() for filter in filters]
    response = '**Добавленные фильтры**:\r\n' + '\r\n'.join(filterlist)

    await client.send_message(chat, response)
    logger.info(response)
