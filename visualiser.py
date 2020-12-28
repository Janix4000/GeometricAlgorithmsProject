from plots import Plot, Scene, LinesCollection as LC, PointsCollection as PC
from math import sqrt
from generators import gen_uniform_circle as generate_circle


class Visualiser:
    def __init__(self):
        self.triangulator = None
        self.n = -1
        self.scenes = []
        self.path = []

    def reset_path(self):
        self.path = []

    def add_to_path(self, triangle):
        self.path.append(triangle)

    def draw_with_path(self):
        scene = self.draw_with_looking_for_point()
        path_lines = self.get_lines(self.path)
        scene.lines.append(
            LC(path_lines, color="red")
        )

    def set_triangulator(self, triangulator):
        self.triangulator = triangulator
        self.n = len(triangulator.points)

    def set_boundaries(self, left, right, top, bot):
        self.left = left
        self.right = right
        self.top = top
        self.bot = bot

    def get_lines(self, triangles):
        ps = self.triangulator.points
        triangles = [[[ps[t[0]], ps[t[1]]], [ps[t[1]], ps[t[2]]], [
            ps[t[2]], ps[t[0]]]] for t in triangles]
        ls = [item for sublist in triangles for item in sublist]
        return ls

    def draw_clear_triangulation(self):
        main_triangles = self.get_main_triangles()
        outer_triangles = self.get_outer_triangles()
        main_lines = self.get_lines(main_triangles)
        outer_lines = self.get_lines(outer_triangles)
        points = self.triangulator.points
        n = self.n
        idx = self.triangulator.idx
        main_points = points[:idx]
        not_used_points = points[idx:n]
        outer_points = points[n:]
        scene = Scene(
            points=[
                PC(main_points, color="green", s=10),
                PC(not_used_points, color="gray", s=10),
                PC(outer_points, color="magenta", s=40)
            ],
            lines=[
                LC(main_lines, color="green"),
                LC(outer_lines, color=(1, 0, 1, 0.1))
            ]
        )
        self.scenes.append(scene)
        return scene

    def draw_with_looking_for_point(self):
        scene = self.draw_clear_triangulation()
        points = [self.triangulator.points[self.triangulator.idx]]
        scene.points.append(
            PC(points, color="red", s=20)
        )
        return scene

    def draw_with_triangles(self, tr0, tr1):
        scene = self.draw_clear_triangulation()
        triangle_lines = self.get_lines([tr0, tr1])
        scene.lines.append(
            LC(triangle_lines, color="cyan")
        )
        return scene

    def draw_with_triangles_and_circle(self, tr0, tr1, center, r_sq):
        scene = self.draw_with_triangles(tr0, tr1)
        circle_lines = self.get_circle_lines(center, r_sq)
        scene.lines.append(
            LC(circle_lines, color='orange')
        )
        return scene

    def get_circle_lines(self, center, r_sq):
        r = sqrt(r_sq)
        points = generate_circle(100, center, r)
        lines = [(points[i], points[(i + 1) % len(points)])
                 for i in range(len(points))]
        return self.validate_lines(lines)

    def validate_lines(self, lines):
        def check(
            p): return self.left < p[0] < self.right and self.bot < p[1] < self.top
        return list(filter(lambda l: check(l[0]) and check(l[1]), lines))

    def get_main_triangles(self):
        triangles = self.triangulator.triangle_set.get_triangles()
        return list(filter(lambda p: p[2] < self.n, triangles))

    def get_outer_triangles(self):
        triangles = self.triangulator.triangle_set.get_triangles()
        return list(filter(lambda p: p[2] >= self.n, triangles))

    def get_plot(self):
        return Plot(scenes=self.scenes)

    def draw_result_triangulation(self):
        scene = self.draw_clear_triangulation()
        scene.points.pop()
        scene.lines.pop()
