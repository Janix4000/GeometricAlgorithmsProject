from Triangulation import Triangulation, Visualiser, FakeVisualiser
from generators import gen_a as generate_random_points
import time


if __name__ == '__main__':
    ps = generate_random_points(100, -1000, 1000)
    # Visualiser(), dla tworzenia animacji
    triangulation = Triangulation(ps, FakeVisualiser())

    start = time.time()
    triangulation.triangulate()
    end = time.time()

    print(end - start)
