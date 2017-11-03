
from multiprocessing.pool import ThreadPool
from multiprocessing import Process
from multiprocessing import Array
import multiprocessing
from observer import Observer
from subject import Subject
import ctypes


class Sentinel(Observer):

    def update(*args, **kwargs):
        print "Running processing on "


class DataController(Subject):

    def __init__(self):
        self.observers = []
        self.Shared_Data_Array = Array(ctypes.c_wchar_p, [' '] * N)

    def set_state(self, s):
        self.Shared_Data_Array[0]

    def subject_state(self):
        return self.Shared_Data_Array


def send_data(subject, s):
    subject.set_state(str(s))
    print subject.subject_state()[:]


if __name__ == '__main__':
    N = 10
    subject = DataController()
    sentinel_observer = Sentinel()

    subject.register(sentinel_observer)

    pool = ThreadPool(processes=3)
    p = pool.map(lambda x: send_data(subject, x), range(3))

    subject.update_observers()
