import random
import numpy as np


class Predict(object):

    def predicts(self):
        x = random.randint(1,14)

        lt = []
        for i in range(15):
            lt.append(0)
            if i == x:
                lt.append(1)
        t = np.array([lt])
        return t