import numpy as np
from random import randint
from math import sqrt


def gen_a(n=100, l=-100, r=100):
    a = np.random.uniform(l, r, 2 * n)
    a.shape = (-1, 2)
    return a


def gen_b(n=100, p=np.array([0, 0]), r=10):
    angles = np.random.uniform(0, 2 * np.pi, n)
    x = np.cos(angles) * r + p[0]
    y = np.sin(angles) * r + p[1]
    return np.vstack((x, y)).T


def gen_c(n=100, lr=np.array([-10, 10]), tb=np.array([-10, 10])):
    x = np.random.uniform(lr[0], lr[1], n)
    y = np.random.uniform(tb[0], tb[1], n)
    ps = np.array(
        [
            [x[i], tb[randint(0, 1)]] if randint(0, 1) == 0
            else [lr[randint(0, 1)], y[i]]
            for i in range(n)
        ]
    )
    return ps


def gen_d(n_axes=25, n_diag=20, a=10):
    x1 = np.random.uniform(0, a, max(0, n_axes - 2))
    x1 = np.append(x1, [0, a])
    y1 = np.zeros(max(n_axes, 2))

    x2 = np.zeros(max(n_axes, 1))
    y2 = np.random.uniform(0, a, max(0, n_axes - 1))
    y2 = np.append(y2, [a])

    x3 = np.random.uniform(0, a, max(n_diag - 1, 0))
    x3 = np.append(x3, [a])
    y3 = np.copy(x3)

    x4 = np.random.uniform(0, a, n_diag)
    y4 = np.copy(x4) * (-1) + a
    x = np.concatenate((x1, x2, x3, x4), axis=None)
    y = np.concatenate((y1, y2, y3, y4), axis=None)
    res = np.vstack((x, y)).T
    np.random.shuffle(res)
    return res
