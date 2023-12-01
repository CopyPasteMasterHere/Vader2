import datetime
import time
import schedule

# Set the time for the function to run
run_time = datetime.time(hour=17, minute=7, second=15)



def my_function():
    print("Hello, World!")


def schedule_job():
    run_time = datetime.time(hour=17, minute=7, second=15)
    print(str(run_time))
    schedule.every().day.at(str(run_time)).do(my_function)
    
schedule_job()

from threading import Thread, Event

class MyThread(Thread):
    def __init__(self, event):
        Thread.__init__(self)
        self.stopped = event

    def run(self):
        while not self.stopped.wait(1):
            schedule.run_pending()
            print("hello")
            
my_event = Event()
thread = MyThread(my_event)
thread.start()