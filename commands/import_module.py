import importlib

async def call_command(**kwargs):
    print(kwargs)
    try:
        module = importlib.import_module('commands.{}_command'.format(kwargs['module']))
    except Exception as e:
        print(e)
    else:
        # print(args[1:])
        await module.main(client, logger, **kwargs)
