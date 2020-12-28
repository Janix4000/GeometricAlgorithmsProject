from plots import Plot, Scene, LinesCollection as LC, PointsCollection as PC


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
        scene = self.draw_clear_triangulation()
        path_lines = self.get_lines(self.path)
        scene.lines.append(
            LC(path_lines, color="red")
        )

    def set_triangulator(self, triangulator):
        self.triangulator = triangulator
        self.n = len(triangulator.points)

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

    def get_main_triangles(self):
        triangles = self.triangulator.triangle_set.get_triangles()
        return list(filter(lambda p: p[2] < self.n, triangles))

    def get_outer_triangles(self):
        triangles = self.triangulator.triangle_set.get_triangles()
        return list(filter(lambda p: p[2] >= self.n, triangles))

    def get_plot(self):
        return Plot(scenes=self.scenes)
