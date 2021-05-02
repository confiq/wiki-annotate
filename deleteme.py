import signal
import time
import asyncio, random
# import uvloop
# asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

async def consumer(queue):
    while True:
        revision = await queue.get()
        if revision is False:
            return
        await asyncio.sleep(revision/10 * random.random() * 2)
        queue.task_done()
        print(f'done working on {revision}')


def main():
    loop = asyncio.get_event_loop()
    queue = asyncio.Queue()
    task = loop.create_task(consumer(queue))
    for run in range(1, 5):
        print(f'produced {run}')
        loop.run_until_complete(queue.put(run))
        # asyncio.run(queue.put(run))
        # queue.put(run)
        # queue.put_nowait(run) # actually does not wait, the point is that I want to put in queue without waiting for it
        time.sleep(.1)
    print('---- done producing')
    loop.run_until_complete(queue.put(False))
    # loop.run_until_complete(task)  # runs forever
    # loop.run_until_complete(asyncio.gather(task))  # runs forever
    # loop.run_until_complete(queue.join())  # gives: Task was destroyed but it is pending!
    loop.run_until_complete(task)

main()
