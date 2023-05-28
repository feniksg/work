from produman import check_payments
import threading, time, schedule



def check_check_payments(time_secunds):
    schedule.every(time_secunds).seconds.do(check_payments)

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    check_payments_thread = threading.Thread(target=check_check_payments, args=(20,))
    check_payments_thread.start()
 