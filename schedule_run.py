from handler import get_all_rents, check_timeout, activ_rents
from produman import check_payments
import threading, time, schedule, sys, traceback
from tgbot import send_alert_message

def get_all_rents_schedule(time_secunds):
    schedule.every(time_secunds).seconds.do(get_all_rents)

    while True:
        schedule.run_pending()
        time.sleep(1)


def activ_rents_schedule(time_secunds):
    try:
        schedule.every(time_secunds).seconds.do(activ_rents)

        while True:
            schedule.run_pending()
            time.sleep(1)
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback_str = ''.join(traceback.format_tb(exc_traceback))
        error_info = f"Exception Type: {exc_type.__name__}\nException Value: {exc_value}\nModule: {sys.argv[0]}\nTraceback: {traceback_str}"
        send_alert_message(error_info)


def check_timeout_schedule(time_secunds):
    try:
        schedule.every(time_secunds).seconds.do(check_timeout)

        while True:
            schedule.run_pending()
            time.sleep(1)
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback_str = ''.join(traceback.format_tb(exc_traceback))
        error_info = f"Exception Type: {exc_type.__name__}\nException Value: {exc_value}\nModule: {sys.argv[0]}\nTraceback: {traceback_str}"
        send_alert_message(error_info)

    
def check_check_payments(time_secunds):
    schedule.every(time_secunds).seconds.do(check_payments)

    while True:
        schedule.run_pending()
        time.sleep(1)



if __name__ == "__main__":
    # get_all_rents_thread = threading.Thread(target=get_all_rents_schedule, args=(300,))
    # get_all_rents_thread.start()

    activ_rents_thread = threading.Thread(target=activ_rents_schedule, args=(1000,))
    activ_rents_thread.start()
 
    check_timeout_thread = threading.Thread(target=check_timeout_schedule, args=(500,))
    check_timeout_thread.start()

    # check_payments_thread = threading.Thread(target=check_check_payments, args=(20,))
    # check_payments_thread.start()
 