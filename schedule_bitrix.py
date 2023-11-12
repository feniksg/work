import schedule, time, threading
from bitrix_updater import scan

def bitrix_up(time_seconds):
    schedule.every(time_seconds).seconds.do(scan)

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    bitrix = threading.Thread(target=bitrix_up, args=(300,))
    bitrix.start()