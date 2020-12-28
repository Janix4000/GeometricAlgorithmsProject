from TriangleSet import TriangleSet
from tools import own_det_3 as det
from generators import gen_a as generate_random_points
from typing import List, Tuple
from functools import reduce
import numpy as np
from plots import Plot, Scene, LinesCollection as LC


class Triangulation:
    def __init__(self, points: List[Tuple[float, float]]):
        self.points: List[Tuple[float, float]] = list(points)
        self.triangle_set = TriangleSet()
        self.idx = 0

    def triangulate(self):
        points = self.points
        n = len(points)
        if n < 3:
            return None
        if n == 3:
            return [(0, 1, 2)]

        p0, p1, p2 = self.make_starting_points()
        points.extend([p0, p1, p2])
        self.triangle_set.add_triangle(n, n + 1, n + 2)

        for point in points:
            if self.idx == n:
                break
            self.add_point_to_triangulation(point)
        return self.get_result_triangulation()

    def triangulate_test(self):
        points = self.points
        n = len(points)
        if n < 3:
            return None
        if n == 3:
            return [(0, 1, 2)]

        p0, p1, p2 = self.make_starting_points()
        points.extend([p0, p1, p2])
        self.triangle_set.add_triangle(n, n + 1, n + 2)

        for point in points:
            if self.idx == n:
                break
            self.add_point_to_triangulation(point)
            # if not self.is_proper():
            #     print("There's a bug...")
            yield self.get_test_lines()
        for _ in range(3):
            points.pop()

    def make_starting_points(self):
        ps = self.points
        left = reduce(lambda a, b: a if a[0] < b[0] else b, ps)[0]
        right = reduce(lambda a, b: a if a[0] > b[0] else b, ps)[0]
        bot = reduce(lambda a, b: a if a[1] < b[1] else b, ps)[1]
        top = reduce(lambda a, b: a if a[1] > b[1] else b, ps)[1]
        width = right - left
        height = top - bot
        p0 = (left + width / 2, top + width / 2)
        p1 = (right + 2 * height, bot - height * 0.5)
        p2 = (left - 2 * height, bot - height * 0.5)

        return p0, p1, p2

    def find_in_triangle(self, point):
        i0, i1, i2 = self.triangle_set.get_first()
        while not self.is_point_in_triangle(point, i0, i1, i2):
            i0, i1, i2 = self.find_next_in_triangle(point, i0, i1, i2)
        return i0, i1, i2

    def is_point_in_triangle(self, point, i0, i1, i2):
        p0 = self.points[i0]
        p1 = self.points[i1]
        p2 = self.points[i2]
        return Triangulation.in_triangle(point, p0, p1, p2)

    @staticmethod
    def in_triangle(point, p0, p1, p2):
        d0 = det(p0, p1, point)
        d1 = det(p1, p2, point)
        d2 = det(p2, p0, point)
        return d0 <= 0 and d1 <= 0 and d2 <= 0

    def find_next_in_triangle(self, point, i0, i1, i2):
        if self.can_be_next_triangle(i1, i0, point):
            return i1, i0, self.triangle_set[(i1, i0)]
        if self.can_be_next_triangle(i2, i1, point):
            return i2, i1, self.triangle_set[(i2, i1)]
        if self.can_be_next_triangle(i0, i2, point):
            return i0, i2, self.triangle_set[(i0, i2)]
        return -1, -1, -1

    def can_be_next_triangle(self, i0, i1, point):
        p0 = self.points[i0]
        p1 = self.points[i1]
        d = det(p0, p1, point)
        return d < 0 and (i0, i1) in self.triangle_set

    def add_point_to_triangulation(self, point):
        i0, i1, i2 = self.find_in_triangle(point)
        self.apply_point_in_triangle(point, (i0, i1, i2))
        self.idx += 1

    def apply_point_in_triangle(self, point, triangle):
        t = triangle
        self.triangle_set.remove_triangle(*t)
        for i in range(3):
            self.triangle_set.add_triangle(t[i], t[(i + 1) % 3], self.idx)
        self.swap_bad_neighbours(t)

    def swap_bad_neighbours(self, first_triangle):
        t = first_triangle
        stack = [(t[i], t[(i + 1) % 3]) for i in range(3)]
        while stack:
            diagonal = stack.pop()
            new_diagonals = self.swap_diagonal_if_necessary(diagonal)
            stack.extend(new_diagonals)

    def swap_diagonal_if_necessary(self, diagonal):
        d = diagonal
        dr = (d[1], d[0])
        if d in self.triangle_set and dr in self.triangle_set:
            tr0 = (d[0], d[1], self.triangle_set[d])
            tr1 = (dr[0], dr[1], self.triangle_set[dr])
            if self.should_be_swapped(tr0, tr1):
                self.swap_diagonals_in_triangles(tr0, tr1)
                return [(tr1[1], tr1[2]), (tr1[2], tr1[0])]
        return []

    def should_be_swapped(self, tr0, tr1):
        if self.is_convex(tr0, tr1):
            point = self.points[tr1[2]]
            triangle = tr0
            return self.is_point_in_circumscribed_circle_of_triangle(point, triangle)
        return False

    def is_point_in_circumscribed_circle_of_triangle(self, point, triangle):
        tr = [self.points[triangle[i]] for i in range(3)]
        center, r_sq = self.circumscribed_circle_of_triangle(tr)
        return (point[0] - center[0]) ** 2 + (point[1] - center[1]) ** 2 < r_sq

    @staticmethod
    def circumscribed_circle_of_triangle(triangle):
        p0 = triangle[0]
        p1 = triangle[1]
        p2 = triangle[2]
        a = np.array([[p2[0] - p0[0], p2[1] - p0[1]],
                      [p2[0] - p1[0], p2[1] - p1[1]]])
        y = np.array([(p2[0] ** 2 + p2[1] ** 2 - p0[0] ** 2 - p0[1] ** 2),
                      (p2[0] ** 2 + p2[1] ** 2 - p1[0] ** 2 - p1[1] ** 2)])
        if np.linalg.det(a) == 0:
            return False
        a_inv = np.linalg.inv(a)
        x = 0.5 * np.dot(a_inv, y)
        x, y = x[0], x[1]
        r_sq = (x - p0[0]) ** 2 + (y - p0[1]) ** 2
        return (x, y), r_sq

    def swap_diagonals_in_triangles(self, tr0, tr1):
        self.triangle_set.remove_triangle(*tr0)
        self.triangle_set.remove_triangle(*tr1)
        self.triangle_set.add_triangle(tr0[2], tr0[0], tr1[2])
        self.triangle_set.add_triangle(tr1[2], tr1[0], tr0[2])

    def get_result_triangulation(self):
        result = self.triangle_set.get_triangles()
        n = self.idx + 1
        return list(filter(lambda p: p[2] < n, result))

    def get_test_lines(self):
        ps = self.points
        triangles = [[[ps[t[0]], ps[t[1]]], [ps[t[1]], ps[t[2]]], [
            ps[t[2]], ps[t[0]]]] for t in self.triangle_set.get_triangles()]
        ls = [item for sublist in triangles for item in sublist]
        return ls

    def is_convex(self, tr0, tr1):
        p0 = self.points[tr0[0]]
        p1 = self.points[tr0[1]]
        p2 = self.points[tr0[2]]
        p3 = self.points[tr1[2]]
        d0 = det(p2, p1, p3)
        d1 = det(p3, p0, p2)
        return d0 > 0 and d1 > 0

    def is_proper(self):
        triangles = self.get_result_triangulation()
        for i0, i1, i2 in triangles:
            triangle = (i0, i1, i2)
            for i in range(self.idx):
                if i in [i0, i1, i2]:
                    continue
                point = self.points[i]
                if self.is_point_in_circumscribed_circle_of_triangle(point, triangle):
                    return False
        return True


if __name__ == '__main__':
    # ps = [
    #     (0, 0), (1, 1), (2, 0), (4, 2),
    #     (2, 4), (0, 4), (1.5, 6)
    # ]
    ps = generate_random_points(30, -1000, 1000)
    tr = Triangulation(ps)
    scenes = []
    for i, lines in enumerate(tr.triangulate_test()):
        print("Made triangulation for {} step".format(i))
        scenes.append(Scene(
            lines=[LC(
                lines=lines
            )]
        ))
    # tr.triangulate()
    # triangles = tr.get_result_triangulation()

    plot = Plot(scenes=scenes)
    plot.draw()
