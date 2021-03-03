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
        filter, created = Filter.get_or_create(word=word, contact_id = contact_id)
        if created:
            response = 'Добавили в фильтры слово {}'.format(word)
        else:
            response = 'Уже есть слово {}'.format(word)

    await client.send_message(chat, response)
    logger.info(response)
