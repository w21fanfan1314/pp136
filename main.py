from app import run
from time import sleep
import threading


run_list = []
def get_pp136():
    from pp136 import home_page
    from pp136 import page
    from pp136 import page_detail

    pp136_run = run(home_page, page, page_detail)
    pp136_run.get_all_res()
    run_list.append(True)


def get_ss25():
    from ss25 import home_page
    from ss25 import page
    from ss25 import page_detail

    ss25 = run(home_page, page, page_detail)
    ss25.get_all_res()
    run_list.append(True)

if __name__ == '__main__':
    tasks = []
    tasks.append(threading.Thread(target=get_pp136))
    tasks.append(threading.Thread(target=get_ss25))

    for task in tasks:
        # task.setDaemon(True)
        task.start()

    while run_list.__len__() == tasks.__len__():
        sleep(30)