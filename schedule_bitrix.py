import schedule, time, threading
from testbt import BtUpdater, Product

def bitrix_up(time_seconds):
    updater = BtUpdater()
    schedule.every(time_seconds).seconds.do(updater.mainloop)

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    bitrix = threading.Thread(target=bitrix_up, args=(900,))
    bitrix.start()