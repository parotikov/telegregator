from database import *

async def main(client, logger, **kwargs):
    # print(kwargs)
    chat = kwargs['answer_to']
    contact_id = kwargs['contact_id']

    if not kwargs['word']:
        response = 'Не указано слово'
    else:
        word = kwargs['word'].lower()
        logger.info('прислали слово {}'.format(word))
        filters = Filter.delete().where((Filter.contact_id == contact_id) and (Filter.word == word))
        deleted = filters.execute()
        if deleted:
            response = '**Удален фильтр**:\r\n' + word
        else:
            response = 'Нет такого фильтра'

    await client.send_message(chat, response)
    logger.info(response)
