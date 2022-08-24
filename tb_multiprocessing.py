# https://medium.com/analytics-vidhya/python-tips-multithreading-vs-multiprocessing-data-sharing-tutorial-52743ed48825
import multiprocessing
import time

def run(array):
    array[0] += 1
    array[1] += 1
    print(f"ID inside thread:{id(array)}")

if __name__ == "__main__":
    # The first attribute is the datatype in the list.
    var = multiprocessing.Array("i", [0, 1])
    print(f"ID outside thread:{id(var)}")

    process1 = multiprocessing.Process(target=run, args=[var])
    process1.start()
    time.sleep(1)

    print("the original var is [0, 1]")
    print(f"the updated var is {list(var)}")
    process1.join()