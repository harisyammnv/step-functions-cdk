import numpy as np
from time import sleep

def square_array(inp: list) -> list:
    return np.square(np.array(inp))

if __name__ == "__main__":
    print(square_array(inp=[3, 4, 5]))
    sleep(10)
    print(square_array(inp=[6, 7, 8]))