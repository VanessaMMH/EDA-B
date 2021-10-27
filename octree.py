import vtk
import random
import time

colors = vtk.vtkNamedColors()

def findAndDraw():
    found = []
    qt.query(busqueda,found)
    for i in range(len(found)):
        sphereSource = vtk.vtkSphereSource()
        xs = found[i].x
        ys = found[i].y
        zs = found[i].z
        sphereSource.SetCenter(xs, ys, zs)
        sphereSource.SetRadius(20)

        sphereSource.SetPhiResolution(100)
        sphereSource.SetThetaResolution(100)

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(sphereSource.GetOutputPort())

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)

        actor.GetProperty().SetColor(0,0,0)

        renderer.AddActor(actor)

def keypress_callback(obj, ev):
    key = obj.GetKeySym()
    if(key == 'l'):
        qt.insert(Point(random.uniform(-399, 399),random.uniform(-400, 400),random.uniform(-400, 400)))
        renderer.RemoveAllViewProps()
        renderer.AddActor(cubeActor)
        findAndDraw()
        qt.show()
        renderWindow.Render()



renderer = vtk.vtkRenderer()
renderWindow = vtk.vtkRenderWindow()
renderWindow.SetWindowName("Octree")
renderWindow.AddRenderer(renderer)

renderWindowInteractor = vtk.vtkRenderWindowInteractor()
renderWindowInteractor.AddObserver('KeyPressEvent', keypress_callback, 1.0)
renderWindowInteractor.SetRenderWindow(renderWindow)


def randomColor():
    return (random.uniform(1, 1000) / 1000, random.uniform(1, 1000) / 1000, random.uniform(1, 1000) / 1000)


def boundedSum(a, b):
    if (a + b > 1.0):
        return 1 - a + b
    else:
        return a + b


class Point:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z


class Cube:
    def __init__(self, x, y, z, w, h, d):
        self.x = x
        self.y = y
        self.z = z
        self.w = w
        self.h = h
        self.d = d

    def contains(self, point):
        if (point.x >= self.x - self.w and point.x <= self.x + self.w and
                point.y >= self.y - self.h and point.y <= self.y + self.h and
                point.z >= self.z - self.d and point.z <= self.z + self.d):
            return True
        return False

    def intersects(self, range):
        if (range.x - range.w > self.x + self.w or range.x + range.w < self.x - self.w or
                range.y - range.h > self.y + self.h or range.y + range.h < self.y - self.h or
                range.z - range.d > self.z + self.d or range.z + range.d < self.z - self.d):
            return False
        return True


class Octree:
    def __init__(self, volumen, n, color):
        self.volumen = volumen
        self.capacity = n
        self.points = []
        self.divided = False
        self.color = color

    def subdivide(self):
        x = self.volumen.x
        y = self.volumen.y
        z = self.volumen.z
        w = self.volumen.w
        h = self.volumen.h
        d = self.volumen.d

        color = self.color

        nefront = Cube(x + w / 2, y + h / 2, z + d / 2, w / 2, h / 2, d / 2)
        self.northeastfront = Octree(
            nefront, self.capacity, (boundedSum(color[0], 0.1), boundedSum(color[1], 0.1), boundedSum(color[2], 0.1)))

        nwfront = Cube(x - w / 2, y + h / 2, z + d / 2, w / 2, h / 2, d / 2)
        self.northwestfront = Octree(
            nwfront, self.capacity, (boundedSum(color[0], 0.2), color[1], color[2]))

        sefront = Cube(x + w / 2, y - h / 2, z + d / 2, w / 2, h / 2, d / 2)
        self.southeastfront = Octree(
            sefront, self.capacity, (color[0], boundedSum(color[1], 0.2), color[2]))

        swfront = Cube(x - w / 2, y - h / 2, z + d / 2, w / 2, h / 2, d / 2)
        self.southwestfront = Octree(
            swfront, self.capacity, (color[0], color[1], boundedSum(color[2], 0.2)))

        neback = Cube(x + w / 2, y + h / 2, z - d / 2, w / 2, h / 2, d / 2)
        self.northeastback = Octree(
            neback, self.capacity, (boundedSum(color[0], 0.5), boundedSum(color[1], 0.5), color[2]))

        nwback = Cube(x - w / 2, y + h / 2, z - d / 2, w / 2, h / 2, d / 2)
        self.northwestback = Octree(
            nwback, self.capacity, (color[0], boundedSum(color[1], 0.7), boundedSum(color[2], 0.5)))

        seback = Cube(x + w / 2, y - h / 2, z - d / 2, w / 2, h / 2, d / 2)
        self.southeastback = Octree(
            seback, self.capacity, (boundedSum(color[0], 0.7), color[1], boundedSum(color[2], 0.7)))

        swback = Cube(x - w / 2, y - h / 2, z - d / 2, w / 2, h / 2, d / 2)
        self.southwestback = Octree(
            swback, self.capacity, (boundedSum(color[0], 0.1), boundedSum(color[1], 0.1), boundedSum(color[2], 0.1)))
        """
        nefront = Cube(x+w/2, y+h/2, z+d/2, w/2, h/2, d/2)
        self.northeastfront = Octree(
            nefront, self.capacity, color)
        nwfront = Cube(x-w/2, y+h/2, z+d/2, w/2, h/2, d/2)
        self.northwestfront = Octree(
            nwfront, self.capacity, randomColor())
        sefront = Cube(x+w/2, y-h/2, z+d/2, w/2, h/2, d/2)
        self.southeastfront = Octree(
            sefront, self.capacity, randomColor())
        swfront = Cube(x-w/2, y-h/2, z+d/2, w/2, h/2, d/2)
        self.southwestfront = Octree(
            swfront, self.capacity, randomColor())
        neback = Cube(x+w/2, y+h/2, z-d/2, w/2, h/2, d/2)
        self.northeastback = Octree(
            neback, self.capacity, randomColor())
        nwback = Cube(x-w/2, y+h/2, z-d/2, w/2, h/2, d/2)
        self.northwestback = Octree(
            nwback, self.capacity, randomColor())
        seback = Cube(x+w/2, y-h/2, z-d/2, w/2, h/2, d/2)
        self.southeastback = Octree(
            seback, self.capacity, randomColor())
        swback = Cube(x-w/2, y-h/2, z-d/2, w/2, h/2, d/2)
        self.southwestback = Octree(
            swback, self.capacity, randomColor()) """

        self.divided = True

    def insert(self, point):
        if (not self.volumen.contains(point)):
            return
        if (len(self.points) < self.capacity):
            new_point = Point(point.x, point.y, point.z)
            self.points.append(new_point)

        else:
            if (not self.divided):
                self.subdivide()
            self.northeastfront.insert(point)
            self.northwestfront.insert(point)
            self.northeastback.insert(point)
            self.northwestback.insert(point)
            self.southeastfront.insert(point)
            self.southwestfront.insert(point)
            self.southeastback.insert(point)
            self.southwestback.insert(point)

    def query(self, rango, found):
        if (not rango.intersects(self.volumen)):
            return found
        for i in range(len(self.points)):
            if (rango.contains(self.points[i])):
                found.append(self.points[i])
        if (self.divided):
            self.northeastfront.query(rango, found)
            self.northwestfront.query(rango, found)
            self.southeastfront.query(rango, found)
            self.southwestfront.query(rango, found)
            self.northeastback.query(rango, found)
            self.northwestback.query(rango, found)
            self.southeastback.query(rango, found)
            self.southwestback.query(rango, found)
        return found

    def show(self):
        cube = vtk.vtkCubeSource()
        cube.SetCenter(self.volumen.x, self.volumen.y, self.volumen.z)
        cube.SetXLength(self.volumen.w * 2)
        cube.SetYLength(self.volumen.h * 2)
        cube.SetZLength(self.volumen.d * 2)
        cube.Update()

        # Mpear
        cubeMapper = vtk.vtkPolyDataMapper()
        cubeMapper.SetInputData(cube.GetOutput())

        # Actor.
        cubeActor = vtk.vtkActor()
        cubeActor.SetMapper(cubeMapper)
        cubeActor.GetProperty().SetOpacity(0.3)
        cubeActor.GetProperty().SetColor(self.color)

        if (self.divided):
            self.northeastfront.show()
            self.northwestfront.show()
            self.northeastback.show()
            self.northwestback.show()
            self.southeastfront.show()
            self.southwestfront.show()
            self.southeastback.show()
            self.southwestback.show()

        for i in range(len(self.points)):
            sphereSource = vtk.vtkSphereSource()

            xs = self.points[i].x
            ys = self.points[i].y
            zs = self.points[i].z
            sphereSource.SetCenter(xs, ys, zs)
            sphereSource.SetRadius(10)

            # Make the surface smooth.
            sphereSource.SetPhiResolution(100)
            sphereSource.SetThetaResolution(100)

            mapper = vtk.vtkPolyDataMapper()
            mapper.SetInputConnection(sphereSource.GetOutputPort())

            actor = vtk.vtkActor()
            actor.SetMapper(mapper)

            actor.GetProperty().SetColor(self.color)

            renderer.AddActor(actor)

        renderer.AddActor(cubeActor)

volumen = Cube(0, 0, 0, 400, 400, 400)
qt = Octree(volumen, 4, (0.0000, 1, 0))

for i in range(5):
    xs = random.uniform(-399, 399)  # -400,400
    ys = random.uniform(-400, 400)  # -400,400
    zs = random.uniform(-400, 400)  # -400,400
    print(i,": ",xs," ",ys," ",zs)
    p = Point(xs, ys, zs)
    qt.insert(p)

qt.show()
xs = random.uniform(-399, 399)
ys = random.uniform(-400, 400)
zs = random.uniform(-400, 400)

busqueda = Cube(xs, ys, zs, 120, 120, 120)
print("busqueda: ",xs," ",ys," ",zs)
cube = vtk.vtkCubeSource()
cube.SetCenter(busqueda.x, busqueda.y, busqueda.z)
cube.SetXLength(busqueda.w*2)
cube.SetYLength(busqueda.h*2)
cube.SetZLength(busqueda.d*2)
cube.Update()
cubeMapper = vtk.vtkPolyDataMapper()
cubeMapper.SetInputData(cube.GetOutput())

findAndDraw()

# Actor.
cubeActor = vtk.vtkActor()
cubeActor.SetMapper(cubeMapper)
cubeActor.GetProperty().SetOpacity(0.2)
cubeActor.GetProperty().SetColor(254, 0, 0)
renderer.AddActor(cubeActor)

renderer.SetBackground((0.0, 0.0, 0.0))

renderWindow.SetSize(1000, 1000)
renderWindow.Render()
renderWindowInteractor.Start()

#p1 = Point(0,0,0)
#p1.impri()
