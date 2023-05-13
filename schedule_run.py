from handler import get_all_rents, check_timeout, activ_rents
import threading, time, schedule


def get_all_rents_schedule(time_secunds):
    schedule.every(time_secunds).seconds.do(get_all_rents)

    while True:
        schedule.run_pending()
        time.sleep(1)


def activ_rents_schedule(time_secunds):
    schedule.every(time_secunds).seconds.do(activ_rents)

    while True:
        schedule.run_pending()
        time.sleep(1)


def check_timeout_schedule(time_secunds):
    schedule.every(time_secunds).seconds.do(check_timeout)

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    # get_all_rents_thread = threading.Thread(target=get_all_rents_schedule, args=(300,))
    # get_all_rents_thread.start()

    activ_rents_thread = threading.Thread(target=activ_rents_schedule, args=(500,))
    activ_rents_thread.start()
 
    check_timeout_thread = threading.Thread(target=check_timeout_schedule, args=(60,))
    check_timeout_thread.start()
 