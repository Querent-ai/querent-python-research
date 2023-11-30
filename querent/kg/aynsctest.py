import asyncio
import pynng
import random
import time
import collections

class Signal:
    def __init__(self, max_size=10):
        self.cache = collections.OrderedDict()
        self.max_size = max_size

    def send(self, command):
        if len(self.cache) >= self.max_size:
            self.cache.popitem(last=False)  # Remove the least recently used item
        self.cache[command] = None  # Store the command

    def receive(self):
        if self.cache:
            command, _ = self.cache.popitem(last=True)  # Get the most recent command
            return command
        return None
    
    def send_confirmation(self, command):
        confirmation_message = f"Processed command '{command}' at {time.ctime()}"
        if len(self.cache) >= self.max_size:
            self.cache.popitem(last=False)  # Remove the least recently used item
        self.cache[('confirmation', confirmation_message)] = None



done_counter = 0

async def worker(task_id, output_queue, signal):
    paused = False
    running = True

    try:
        while running:
            command = signal.receive()
            if command:
                # signal.send_confirmation(command)
                if command == "stop":
                    running = False
                    continue
                elif command == "pause":
                    print("pause implemented", task_id)
                    paused = True
                elif command == "resume":
                    paused = False

            if not paused:
                print(f"Worker {task_id} running - {time.ctime()}")
                # Simulate work
                await asyncio.sleep(random.uniform(0.1, 0.5))
                result = f'Task {task_id} completed at {time.ctime()}'
                output_queue.put_nowait(result)
            else:
                print(f"Worker {task_id} paused - {time.ctime()}")
                await asyncio.sleep(0.1)

    finally:
        output_queue.put_nowait(f'Worker {task_id} DONE')


async def output_consumer(consumer_id, output_queue, total_workers):
    global done_counter
    while True:
        try:
            if done_counter == total_workers:
                break
            await asyncio.sleep(2)
            message = output_queue.get_nowait()
            print(f"Consumer {consumer_id} processed: {message}")
            if "DONE" in message:
                done_counter += 1
                print(f"done counter: {done_counter}")  
        except asyncio.QueueEmpty:
            await asyncio.sleep(1)



async def main():
    worker_count = 5
    consumer_count = 3
    output_queue = asyncio.Queue()

    # Create a Signal instance for each worker
    signals = [Signal(max_size=10) for _ in range(worker_count)]

    # Create worker tasks
    workers = [asyncio.create_task(worker(i, output_queue, signals[i])) for i in range(worker_count)]
    consumers = [asyncio.create_task(output_consumer(i, output_queue, worker_count)) for i in range(consumer_count)]
    asyncio.gather(*workers)
    await asyncio.sleep(2)
    signals[1].send("stop")  # Stop worker 1 permanently
    await asyncio.sleep(2)
    signals[0].send("pause")  # Pause worker 0
    await asyncio.sleep(2)
    signals[0].send("resume")  # Resume worker 0
    await asyncio.sleep(2)
    for signal in signals:
        signal.send("stop")  # Stop all workers permanently
    # for i, signal in enumerate(signals):
    #     confirmation = signal.receive()
    #     if confirmation and confirmation[0] == 'confirmation':
    #         print(f"Worker {i} {confirmation[1]}")
   
    await asyncio.gather(*consumers)



if __name__ == "__main__":
    asyncio.run(main())
