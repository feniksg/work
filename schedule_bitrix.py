import schedule, time, threading, sys, traceback
from testbt import BtUpdater, Product
from tgbot import send_alert_message

def bitrix_up(time_seconds):
    try:
        updater = BtUpdater()
        schedule.every(time_seconds).seconds.do(updater.mainloop)

        while True:
            schedule.run_pending()
            time.sleep(1)
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback_str = ''.join(traceback.format_tb(exc_traceback))
        error_info = f"Exception Type: {exc_type.__name__}\nException Value: {exc_value}\nModule: {sys.argv[0]}\nTraceback: {traceback_str}"
        send_alert_message(error_info)



if __name__ == '__main__':
    bitrix = threading.Thread(target=bitrix_up, args=(900,))
    bitrix.start()