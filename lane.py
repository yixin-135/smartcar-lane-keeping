import os
from multiprocessing import Process, Queue
from src.scenes import LF_threshold
from src.utils import getkey, log, CameraBroadcaster, CAMERA_INFO, Controller
from src.actions import Stop

if __name__ == '__main__':
    log.info('start')
    ctrl = Controller()
    msg_queue = Queue(maxsize=1)
    camera = CameraBroadcaster(CAMERA_INFO)
    shared_memory_name = camera.memory_name
    camera_process = Process(target=camera.run)
    camera_process.start()
    task = LF_threshold(shared_memory_name, CAMERA_INFO, msg_queue)
    process = Process(target=task.loop)
    process.start()
    try:
        while True:
            key = getkey()
            if key == 'esc':
                process.kill()
                ctrl.execute(Stop())
                camera.stop_sign.value = True
                camera_process.join()
                break
            else:
                msg_queue.put(key)
    except (KeyboardInterrupt, SystemExit):
        camera.stop_sign.value = True
        camera_process.join()
        os.system('stty sane')
        log.info('stopping.')