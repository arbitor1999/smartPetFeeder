import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import schedule

def job(name):
    print(name)
schedule.every().day.at("16:11:00").do(job, 'sss')


class MyHandler(FileSystemEventHandler):
    def on_modified(self, event):
        print('modify')
        f = open(event.src_path,'r')
        data = f.read()
        f.close()
        print(data)


path =  "./"
event_handler = MyHandler()
observer = Observer()
observer.schedule(event_handler, path, recursive=True)
observer.start()

try:
    while True:
        schedule.run_pending()
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()
observer.join()
