from queue import Queue
from threading import Thread


class A():

    def predict(self, documents):

        queue = Queue()
        array = []

        threads = [Thread(target=self.work, args=(queue, array)) for _ in range(min(len(documents), 4))]
        [t.start() for t in threads]

        [queue.put(doc) for doc in documents]

        queue.join()
        [queue.put(None) for _ in range(len(threads))]
        [t.join() for t in threads]
        print(array)


    def work(self, queue, array):

        while True:
            doc = queue.get()
            if doc is None:
                break
            print(doc)
            array.append(doc)
            queue.task_done()

a = A()
a.predict([1,2,3,4,5,6,6,7])
print("end")