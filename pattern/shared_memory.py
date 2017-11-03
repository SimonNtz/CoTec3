from multiprocessing import Process, Lock
from multiprocessing.sharedctypes import Value, Array
from ctypes import Structure, c_double


class BandController(object):
    list = []


def modify(v, n, A):
    A[0] = n
    v += 1


if __name__ == '__main__':
    lock = Lock()

    v = Value('i', 0)
    s = Array('c', 'hello world', lock=lock)
    A = Array('i', [9, 9, 9], lock=lock)

    p = Process(target=modify, args=(v, 5, A))
    p.start()
    p.join()

    print v.value
    print [a for a in A]
