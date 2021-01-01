from random import shuffle
from TriangleSet import TriangleSet
from tools import own_det_3 as det
from generators import gen_a as generate_random_points
from visualiser import Visualiser, FakeVisualiser
from typing import List, Tuple
from functools import reduce
from math import sqrt
import numpy as np
from plots import Plot, Scene, LinesCollection as LC

OVERLAPING_METHOD = 1
SWAPING_METHOD = 2
delta = 1e-5


class Triangulation:
    def __init__(self, points: List[Tuple[float, float]], method=SWAPING_METHOD, visualiser=FakeVisualiser()):
        self.points: List[Tuple[float, float]] = list(points)
        self.triangle_set = TriangleSet()
        self.idx = 0
        self.visualiser = visualiser
        self.visualiser.set_triangulator(self)
        self.method = method

    def triangulate(self):
        points = self.points
        n = len(points)
        if n < 3:
            return None
        if n == 3:
            return [(0, 1, 2)]

        p0, p1, p2 = self.make_starting_points()
        points.extend([p0, p1, p2])
        self.add_triangle(n, n + 1, n + 2)

        self.visualiser.draw_clear_triangulation()

        for point in points:
            if self.idx == n:
                break
            self.add_point_to_triangulation(point)
            self.visualiser.draw_clear_triangulation()
        self.visualiser.draw_result_triangulation()
        return self.get_result_triangulation()

    def make_starting_points(self):
        ps = self.points
        left = reduce(lambda a, b: a if a[0] < b[0] else b, ps)[0]
        right = reduce(lambda a, b: a if a[0] > b[0] else b, ps)[0]
        bot = reduce(lambda a, b: a if a[1] < b[1] else b, ps)[1]
        top = reduce(lambda a, b: a if a[1] > b[1] else b, ps)[1]
        width = right - left
        height = top - bot
        self.visualiser.set_boundaries(
            left - 0.25 * width, right + 0.25 * width, bot - 0.25 * height, top + 0.25 * height)
        p0 = (left + width / 2, top + 10 * width)
        p1 = (right + 20 * height, bot - height * 5)
        p2 = (left - 20 * height, bot - height * 5)

        return p0, p1, p2

    def find_in_triangle(self, point):
        self.visualiser.reset_path()
        i0, i1, i2 = self.triangle_set.get_first()
        self.visualiser.add_to_path((i0, i1, i2))
        self.visualiser.draw_with_path()
        while not self.is_point_in_triangle(point, i0, i1, i2):
            i0, i1, i2 = self.find_next_in_triangle(point, i0, i1, i2)
            self.visualiser.add_to_path((i0, i1, i2))
            self.visualiser.draw_with_path()
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
        tr = (i0, i1, i2)
        for i in range(3):
            i0, i1 = tr[i], tr[(i+1) % 3]
            if self.can_be_next_triangle(i0, i1, point):
                rev = (i1, i0)
                return (*rev, self.triangle_set[rev])
        return -1, -1, -1

    def can_be_next_triangle(self, i0, i1, point):
        if not (i1, i0) in self.triangle_set:
            return False
        i2 = self.triangle_set[(i0, i1)]
        p0 = self.points[i0]
        p1 = self.points[i1]
        p2 = self.points[i2]
        n01 = self.get_norm_line(p0, p1)
        n12 = self.get_norm_line(p1, p2)
        n20 = self.get_norm_line(p2, p0)
        n201 = (n20[0] - n01[0], n20[1] - n01[1])
        n012 = (n01[0] - n12[0], n01[1] - n12[1])
        d201 = det(p0, (p0[0] + n201[0], p0[1] + n201[1]), point)
        d012 = det(p1, (p1[0] + n012[0], p1[1] + n012[1]), point)
        return d201 < delta and d012 > -delta

    def get_norm_line(self, p0, p1):
        n = (p1[0] - p0[0], p1[1] - p0[1])
        l = sqrt(n[0]**2 + n[1]**2)
        n = (n[0] / l, n[1] / l)
        return n

    def add_point_to_triangulation(self, point):
        first_triangle = self.find_in_triangle(point)
        self.apply_point_in_triangle(point, first_triangle)
        self.idx += 1

    def apply_point_in_triangle(self, point, triangle):
        t = triangle
        if self.method == SWAPING_METHOD:
            self.apply_swapping_method(t)
        elif self.method == OVERLAPING_METHOD:
            self.remove_overlaping_triangles(t)

    def apply_swapping_method(self, first_triangle):
        overlapping_edge = self.get_overlapping_edge(first_triangle)
        if overlapping_edge is not None:
            self.split_to_two_triangles(overlapping_edge)
        else:
            self.merge_into_triangle(first_triangle)
        self.visualiser.draw_with_looking_for_point()
        self.swap_bad_neighbours(first_triangle)

    def get_overlapping_edge(self, first_triangle):
        point = self.points[self.idx]
        t = first_triangle
        ps = self.points
        for i in range(3):
            i0, i1 = t[i], t[(i+1) % 3]
            p0, p1 = ps[i0], ps[i1]
            if abs(det(p0, p1, point)) < delta:
                return i0, i1
        return None

    def add_triangle(self, i0, i1, i2):
        self.triangle_set.add_triangle(i0, i1, i2)
        if self.is_not_proper_triangle(i0, i1, i2):
            print('Ups...')

    def is_not_proper_triangle(self, i0, i1, i2):
        p0, p1, p2 = self.points[i0], self.points[i1], self.points[i2]
        return abs(det(p0, p1, p2)) < delta

    def merge_into_triangle(self, triangle):
        t = triangle
        self.triangle_set.remove_triangle(*t)
        for i in range(3):
            i0, i1 = t[i], t[(i+1) % 3]
            self.add_triangle(i0, i1, self.idx)

    def split_to_two_triangles(self, edge):
        i0, i1 = edge
        i2 = self.triangle_set[(i0, i1)]
        self.triangle_set.remove_triangle(i0, i1, i2)
        self.add_triangle(i0, self.idx, i2)
        self.add_triangle(i2, self.idx, i1)
        if (i1, i0) in self.triangle_set:
            i3 = self.triangle_set[(i1, i0)]
            self.triangle_set.remove_triangle(i0, i3, i1)
            self.add_triangle(i0, i3, self.idx)
            self.add_triangle(i3, i1, self.idx)

    def swap_bad_neighbours(self, first_triangle):
        t = first_triangle
        stack = [(t[i], t[(i + 1) % 3]) for i in range(3)]
        swapped = set()
        while stack:
            diagonal = stack.pop()
            if diagonal in swapped:
                continue
            swapped.add(diagonal)
            new_diagonals = self.swap_diagonal_if_necessary(diagonal)
            stack.extend(new_diagonals)

    def swap_diagonal_if_necessary(self, diagonal):
        d = diagonal
        dr = (d[1], d[0])
        if d in self.triangle_set and dr in self.triangle_set:
            tr0 = (d[0], d[1], self.triangle_set[d])
            tr1 = (dr[0], dr[1], self.triangle_set[dr])

            self.draw_triangles_with_circle([tr0, tr1])

            if self.should_be_swapped(tr0, tr1):
                self.swap_diagonals_in_triangles(tr0, tr1)
                return [(tr1[1], tr1[2]), (tr1[2], tr1[0])]
        return []

    def draw_triangles_with_circle(self, triangles):
        tr0 = triangles[0]
        tr = [self.points[tr0[i]] for i in range(3)]
        center, r_sq = self.circumscribed_circle_of_triangle(tr)
        self.visualiser.draw_with_triangles_and_circle(
            triangles, center, r_sq)

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

    @ staticmethod
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
        self.add_triangle(tr0[2], tr0[0], tr1[2])
        self.add_triangle(tr1[2], tr1[0], tr0[2])

        self.visualiser.draw_with_triangles(
            [(tr0[2], tr0[0], tr1[2]), (tr1[2], tr1[0], tr0[2])])

    def remove_overlaping_triangles(self, first_triangle):
        edges_to_connect = []
        stack = []
        for i in range(3):
            stack.append((first_triangle[i], first_triangle[(i+1) % 3]))
        self.triangle_set.remove_triangle(*first_triangle)
        while stack:
            diagonal = stack.pop()
            reversed_diagonal = (diagonal[1], diagonal[0])
            if self.should_be_removed(reversed_diagonal):
                self.remove_overlaping_triangle(
                    reversed_diagonal, stack, edges_to_connect)
            else:
                edges_to_connect.append(diagonal)
        self.connect_edges(edges_to_connect)

    def remove_overlaping_triangle(self, diagonal, stack, edges_to_connect):
        stack.extend(self.get_neighbours(diagonal))
        edges_to_connect.extend(self.get_alone_edges(diagonal))
        i2 = self.triangle_set[diagonal]
        self.triangle_set.remove_triangle(*diagonal, i2)
        self.visualiser.draw_with_looking_for_point()

    def should_be_removed(self, diagonal):
        if diagonal not in self.triangle_set:
            return False
        i2 = self.triangle_set[diagonal]
        point = self.points[self.idx]
        triangle = (*diagonal, i2)
        self.draw_triangles_with_circle([triangle])
        return self.is_point_in_circumscribed_circle_of_triangle(point=point, triangle=triangle)

    def get_neighbours(self, diagonal):
        result = []
        if diagonal in self.triangle_set:
            i0, i1 = diagonal
            i2 = self.triangle_set[diagonal]
            if (i2, i1) in self.triangle_set:
                result.append((i1, i2))
            if (i0, i2) in self.triangle_set:
                result.append((i2, i0))
        return result

    def get_alone_edges(self, diagonal):
        result = []
        if diagonal in self.triangle_set:
            i0, i1 = diagonal
            i2 = self.triangle_set[diagonal]
            if (i2, i1) not in self.triangle_set:
                result.append((i1, i2))
            if (i0, i2) not in self.triangle_set:
                result.append((i2, i0))
        return result

    def connect_edges(self, edges_to_connect):
        while edges_to_connect:
            edge = edges_to_connect.pop()
            self.add_triangle(*edge, self.idx)
            self.visualiser.draw_with_looking_for_point()

    def get_result_triangulation(self):
        result = self.triangle_set.get_triangles()
        n = self.idx + 1
        return list(filter(lambda p: p[2] < n, result))

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
    # ps = generate_random_points(100, -1000, 1000)

    ps = []
    for y in range(4):
        for x in range(5):
            ps.append((x, y))
    shuffle(ps)
    # ps = [
    #     (0, 0), (2, 2), (1, 1), (4, 4), (3, 3),
    #     (2, 0)
    tr = Triangulation(ps, visualiser=Visualiser(), method=OVERLAPING_METHOD)
    try:
        triangles = tr.triangulate()
        # pass
    except Exception as exc:
        print(exc)
    print("Made")
    print(tr.is_proper())
    plot = tr.visualiser.get_plot()
    plot.draw()
