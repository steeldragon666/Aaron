import cadquery as cq
from . import core


class DesignTypes:
    DirectDesignType = 0
    ParametricDesignType = 1


class DistanceUnits:
    MillimeterDistanceUnits = 0


class BooleanTypes:
    DifferenceBooleanType = 0
    IntersectionBooleanType = 1
    UnionBooleanType = 2


class _TempBody:
    def __init__(self, shape):
        self.shape = shape


class TemporaryBRepManager:
    _inst = None

    @staticmethod
    def get():
        if TemporaryBRepManager._inst is None:
            TemporaryBRepManager._inst = TemporaryBRepManager()
        return TemporaryBRepManager._inst

    def createBox(self, obb):
        L, W, H = obb.dims
        c = obb.center
        return _TempBody(cq.Solid.makeBox(L, W, H, pnt=cq.Vector(c.x - L / 2, c.y - W / 2, c.z - H / 2)))

    def createCylinderOrCone(self, p1, r1, p2, r2):
        assert abs(r1 - r2) < 1e-12
        d = p2.v() - p1.v()
        return _TempBody(cq.Solid.makeCylinder(r1, d.Length, pnt=p1.v(), dir=d.normalized()))

    def createTorus(self, c, axis, R, r):
        return _TempBody(cq.Solid.makeTorus(R, r, pnt=c.v(), dir=axis.v()))

    def booleanOperation(self, target, tool, t):
        if t == BooleanTypes.UnionBooleanType:
            target.shape = target.shape.fuse(tool.shape).clean()
        elif t == BooleanTypes.DifferenceBooleanType:
            target.shape = target.shape.cut(tool.shape).clean()
        else:
            target.shape = target.shape.intersect(tool.shape).clean()
        return target.shape.Volume() > 0

    def transform(self, body, m):
        ang, ax, org = m.rot
        import math
        body.shape = body.shape.rotate(org.v(), org.v() + ax.v(), math.degrees(ang))
        return True


class BRepBody:
    def __init__(self, shape):
        self._shape = shape
        self.name = ""
        self.appearance = None
        self.opacity = 1.0

    @property
    def volume(self):
        return self._shape.Volume()          # cm3 (model built in cm)

    def bbox(self):
        return self._shape.BoundingBox()


class BRepBodies:
    def __init__(self):
        self._b = []

    @property
    def count(self):
        return len(self._b)

    def add(self, temp, base_feature=None):
        assert base_feature is not None and base_feature.editing, "parametric add needs an open base feature"
        b = BRepBody(temp.shape)
        self._b.append(b)
        return b

    def itemByName(self, n):
        for b in self._b:
            if b.name == n:
                return b
        return None


class BaseFeature:
    def __init__(self):
        self.editing = False
        self.name = ""

    def startEdit(self):
        self.editing = True
        return True

    def finishEdit(self):
        self.editing = False
        return True


class _BaseFeatures:
    def add(self):
        return BaseFeature()


class _Features:
    def __init__(self):
        self.baseFeatures = _BaseFeatures()


class Component:
    def __init__(self, name=""):
        self.name = name
        self.bRepBodies = BRepBodies()
        self.occurrences = Occurrences()
        self.features = _Features()


class Occurrence:
    def __init__(self, comp):
        self.component = comp


class Occurrences:
    def __init__(self):
        self._o = []

    @property
    def count(self):
        return len(self._o)

    def addNewComponent(self, m):
        o = Occurrence(Component())
        self._o.append(o)
        return o


class UserParameter:
    def __init__(self, name, vi, unit, comment):
        self.name, self.unit, self.comment = name, unit, comment
        if vi.s is not None:
            num, u = vi.s.split()
            assert u == "mm" == unit
            self.value = float(num) / 10.0      # internal cm
        else:
            self.value = vi.r


class UserParameters:
    def __init__(self):
        self._p = []

    @property
    def count(self):
        return len(self._p)

    def item(self, i):
        return self._p[i]

    def add(self, name, vi, unit, comment):
        assert name.replace("_", "").isalnum(), name
        assert all(p.name != name for p in self._p), "duplicate " + name
        p = UserParameter(name, vi, unit, comment)
        self._p.append(p)
        return p


class _UnitsManager:
    internalUnits = "cm"

    def convert(self, v, frm, to):
        f = {"cm": 10.0, "mm": 1.0}
        return v * f[frm] / f[to]


class _FusionUnitsManager:
    distanceDisplayUnits = None


class Design:
    def __init__(self):
        self.rootComponent = Component("root")
        self.userParameters = UserParameters()
        self.appearances = core._Appearances()
        self.unitsManager = _UnitsManager()
        self.fusionUnitsManager = _FusionUnitsManager()
        self.designType = None

    @staticmethod
    def cast(o):
        return o if isinstance(o, Design) else None
