import random
import logging.config 
import asyncio
import sys
import warnings
 
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(filename)s:%(lineno)d %(message)s',
    stream=sys.stderr,
)
LOG = logging.getLogger()
 
def stop_operation(future):
    LOG.info(future.result())

async def operation(loop):
    queue = asyncio.Queue()
    LOG.info('start main operation')
    task = asyncio.ensure_future(operationsub(queue))

    count = 1

    while True:
        if not queue.empty():
            queuedata = await queue.get()
            LOG.info('queuedata:{}'.format(queuedata))
            if queuedata[0]=="stop":
                break
        LOG.info('waiting sub operation... ' + str(count))
        await asyncio.sleep(1)
        count += 1

    LOG.info('main operation 1')
    await asyncio.sleep(3)

    LOG.info('main operation is done')
    loop.stop()

async def operationsub(queue):
    LOG.info('start sub operation')

    LOG.info('sub operation process 1')
    await asyncio.sleep(3)
    queue.put_nowait(["start", 1,2,3])
    LOG.info('sub operation process 2')
    await asyncio.sleep(1)
    queue.put_nowait(["next", 4,5,6])
    LOG.info('sub operation process 3')
    await asyncio.sleep(12)
    queue.put_nowait(["stop", 7,8,9])

    LOG.info('sub operation is done')

async def check_label():
    asyncio.sleep(2)
    return random.randint(0, 1)

LOG.info('start')
loop = asyncio.get_event_loop()
loop.slow_callback_duration = 0.001
asyncio.ensure_future(operation(loop))
loop.run_forever()
loop.close()
exit()