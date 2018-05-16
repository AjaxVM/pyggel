
from .math3d import Vec3, Mat4

# TODO: consider making dirty.py which wraps around things
# and then tracks when they change

# Because, we need to know if a node is dirty so we kno wwhether to rebuild it's matrices
# ie if the scene view/camera changed then we must update all render matrices
# and if the node moved we must update local matrix (and child local matrices)

class Node(object):
    def __init__(self, parent=None):
        self._parent = None
        self._root = None
        self.parent = parent
        self._children = []

        self._transform_matrix = None
        self._view_matrix = None # this should be none if not a Scene
        self._render_matrix = None # view_matrix * matrix

    # parent/child/root properties and functions
    @property
    def parent(self):
        return self._parent
    @parent.setter
    def parent(self, parent):
        if self._parent:
            self._parent._remove_child(self)
            self._root = self

        self._parent = parent
        if parent:
            self._root = parent._root
            parent._add_child(self)
        else:
            self._root = self

    @property
    def root(self):
        return self._root

    def _add_child(self, child):
        self._children.append(child)

    def _remove_child(self, child):
        self._children.remove(child)

    def add_child(self, child):
        child.parent = self

    def remove_child(self, child):
        child.parent = None

    # matrix properties and functions
    @property
    def transform_matrix(self):
        if not self._transform_matrix:
            return self.calculate_transform_matrix()
        return self._transform_matrix

    @property
    def render_matrix(self):
        if not self._render_matrix:
            return self.calculate_render_matrix()
        return self._render_matrix

    def get_local_matrix(self):
        return None

    def calculate_transform_matrix(self):
        # TODO: how to check for dirty?
        mat4 = self.get_local_matrix()

        if self._parent and self._parent._transform_matrix:
            if mat4:
                mat4 = self._parent._transform_matrix * mat4
            else:
                mat4 = self._parent._transform_matrix

        self._transform_matrix = mat4
        return mat4

    def calculate_render_matrix(self):
        # TODO: how to check for dirty?
        mat4 = self._transform_matrix or self.calculate_transform_matrix()

        if self._root._view_matrix:
            if mat4:
                mat4 = self._root._view_matrix * mat4
            else:
                mat4 = self._root._view_matrix

        self._render_matrix = mat4
        return mat4

    def update(self):
        self.calculate_transform_matrix()
        self.calculate_render_matrix()
        for child in self._children:
            child.update()

    def render(self):
        for child in self._children:
            child.render()

class Scene(Node):
    def __init__(self, view=None, camera=None, shader=None):
        super(Scene, self).__init__()

        self.view = view
        self.camera = camera
        self.shader = shader

    def get_view_matrix(self):
        if self.view:
            if self.camera:
                return self.view.matrix * self.camera.matrix
            return self.view.matrix
        elif self.camera:
            return self.camera.matrix

    def calculate_view_matrix(self):
        # todo: how to check dirty?
        self._view_matrix = self.get_view_matrix()

    def update(self):
        # self.calculate_transform_matrix()
        self.calculate_render_matrix()
        self.calculate_view_matrix()
        for child in self._children:
            child.update()

    def render(self):
        # todo: gotta figure out multipass rendering
        # todo: gotta figure out collection of render nodes to sort/clip
        # todo: gotta figure out what default uniforms are
        # todo: gotta figure out what value is needed for gSampler really
        if self.shader:
            self.shader.bind()
            self.shader.uniform('gSampler', 0)
        super(Scene, self).render()

class TransformNode(Node):
    def __init__(self, position=None, rotation=None, scale=None, parent=None):
        super(TransformNode, self).__init__(parent)

        # todo: ensure we get vec3s here...
        self.position = position or Vec3(0)
        self.rotation = rotation or Vec3(0)
        self.scale = scale or Vec3(1)

        # todo: cache our local matrix

    def get_local_matrix(self):
        return Mat4.from_transform(self.position, self.rotation, self.scale)

class RenderNode(Node):
    def __init__(self, mesh, parent=None):
        super(RenderNode, self).__init__(parent)

        self.mesh = mesh

    # TODO: setup a system to instead collect renderable nodes to clip/sort them
    # and render that way instead
    def render(self):
        if isinstance(self._root, Scene) and self._root.shader:
            # todo: gotta figure out what the real uniform is we should be passing
            self._root.shader.uniform('worldLocation', 1, False, self.render_matrix.representation)
        self.mesh.render()
        super(RenderNode, self).render()
