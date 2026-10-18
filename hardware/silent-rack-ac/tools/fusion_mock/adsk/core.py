import math
import cadquery as cq


class _Enum:
    pass


class DocumentTypes(_Enum):
    FusionDesignDocumentType = 0


class ViewOrientations(_Enum):
    IsoTopRightViewOrientation = 7


class DefaultModelingOrientations(_Enum):
    YUpModelingOrientation = 0
    ZUpModelingOrientation = 1


class Point3D:
    def __init__(self, x, y, z):
        self.x, self.y, self.z = x, y, z

    @staticmethod
    def create(x=0.0, y=0.0, z=0.0):
        return Point3D(x, y, z)

    def v(self):
        return cq.Vector(self.x, self.y, self.z)


class Vector3D(Point3D):
    @staticmethod
    def create(x=0.0, y=0.0, z=0.0):
        return Vector3D(x, y, z)


class Matrix3D:
    def __init__(self):
        self.rot = None

    @staticmethod
    def create():
        return Matrix3D()

    def setToRotation(self, angle, axis, origin):
        self.rot = (angle, axis, origin)
        return True


class OrientedBoundingBox3D:
    @staticmethod
    def create(center, lengthDir, widthDir, length, width, height):
        o = OrientedBoundingBox3D()
        assert (lengthDir.x, lengthDir.y, lengthDir.z) == (1, 0, 0)
        assert (widthDir.x, widthDir.y, widthDir.z) == (0, 1, 0)
        o.center, o.dims = center, (length, width, height)
        return o


class ValueInput:
    def __init__(self, s=None, r=None):
        self.s, self.r = s, r

    @staticmethod
    def createByString(s):
        assert isinstance(s, str)
        return ValueInput(s=s)

    @staticmethod
    def createByReal(r):
        return ValueInput(r=float(r))


class Color:
    @staticmethod
    def create(r, g, b, a):
        for c in (r, g, b, a):
            assert isinstance(c, int) and 0 <= c <= 255
        c = Color()
        c.rgba = (r, g, b, a)
        return c


class ColorProperty:
    def __init__(self):
        self.value = None
        self.id = "opaque_albedo"

    @staticmethod
    def cast(o):
        return o if isinstance(o, ColorProperty) else None


class _Props:
    def __init__(self):
        self._p = [ColorProperty()]

    @property
    def count(self):
        return len(self._p)

    def item(self, i):
        return self._p[i]

    def itemById(self, i):
        return self._p[0] if i == "opaque_albedo" else None


class Appearance:
    def __init__(self, name):
        self.name = name
        self.appearanceProperties = _Props()


class _Appearances:
    def __init__(self, names=()):
        self._a = {n: Appearance(n) for n in names}

    def itemByName(self, n):
        return self._a.get(n)

    def addByCopy(self, base, name):
        assert base is not None
        self._a[name] = Appearance(name)
        return self._a[name]


class _Lib:
    def __init__(self, name, apps):
        self.name = name
        self.appearances = _Appearances(apps)


class _Libs:
    def __init__(self):
        self._l = [_Lib("Fusion Material Library", ()),
                   _Lib("Fusion Appearance Library", ("Plastic - Matte (Yellow)",))]

    @property
    def count(self):
        return len(self._l)

    def item(self, i):
        return self._l[i]


class _Camera:
    viewOrientation = None
    isFitView = False


class _Viewport:
    def __init__(self):
        self.camera = _Camera()

    def refresh(self):
        pass

    def fit(self):
        pass


class _Progress:
    isCancelButtonShown = False
    progressValue = 0
    wasCancelled = False

    def show(self, title, msg, mn, mx, delay):
        assert "%v" in msg and "%m" in msg
        return True

    def hide(self):
        return True


class _UI:
    def __init__(self):
        self.messages = []

    def createProgressDialog(self):
        return _Progress()

    def messageBox(self, text, title=""):
        self.messages.append((title, text))
        print("---- messageBox [%s] ----\n%s\n-------------------------" % (title, text))


class _Docs:
    def __init__(self, app):
        self.app = app

    def add(self, t):
        from . import fusion
        assert t == DocumentTypes.FusionDesignDocumentType
        self.app.activeProduct = fusion.Design()
        return self.app.activeProduct


class _GenPrefs:
    defaultModelingOrientation = DefaultModelingOrientations.ZUpModelingOrientation


class _Prefs:
    generalPreferences = _GenPrefs()


class Application:
    _inst = None

    def __init__(self):
        self.userInterface = _UI()
        self.documents = _Docs(self)
        self.activeProduct = None
        self.materialLibraries = _Libs()
        self.preferences = _Prefs()
        self.activeViewport = _Viewport()

    @staticmethod
    def get():
        if Application._inst is None:
            Application._inst = Application()
        return Application._inst
