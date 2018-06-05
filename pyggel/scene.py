
from .math3d import Vec3, Mat4

class Node(object):
    # node_type flags if this is a special node that we want collected into a flat list in scene
    node_type = None

    def __init__(self, parent=None):
        self._parent = None
        self._root = None
        self.parent = parent
        self._children = []

        self._transform_matrix = None
        self._view_matrix = None # this should be none if not a Scene
        self._scene_matrix = None # view_matrix * matrix

    # parent/child/root properties and functions
    @property
    def parent(self):
        return self._parent
    @parent.setter
    def parent(self, parent):
        if self._parent:
            self._parent._remove_child(self)
            self.root = self

        self._parent = parent
        if parent:
            self.root = parent._root
            parent._add_child(self)
        else:
            self.root = self

    @property
    def root(self):
        return self._root
    @root.setter
    def root(self, root):
        if self._root and self._root != self:
            self._root._remove_node_from_flat(self)
        self._root = root
        if root and root != self:
            root._add_node_to_flat(self)

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
        if not self._scene_matrix:
            return self.calculate_render_matrix()
        return self._scene_matrix

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

        self._scene_matrix = mat4
        return mat4

    def update(self):
        self.calculate_transform_matrix()
        self.calculate_render_matrix()
        for child in self._children:
            child.update()

    def _add_node_to_flat(self, node):
        # this does nothing if this is a base Node
        pass

    def _remove_node_from_flat(self, node):
        # this does nothing by default
        pass

    def __del__(self):
        if self._root:
            self._root._remove_node_from_flat(self)

    def get_render_position(self):
        return Vec3(0,0,0) * self._scene_matrix

class Scene(Node):
    def __init__(self, view=None, camera=None):
        super(Scene, self).__init__()

        self.view = view
        self.camera = camera

        # store for the various nodes that are flagged as being interesting outside
        # for instance, render and light nodes are important to the render_engine
        # TODO: rather than this have an oct tree that gets updated... derp
        self.flat_nodes = {
            'render_opaque': [],
            'render_transparent': [],
            'light': []
        }

    def get_view_matrix(self):
        if self.view:
            if self.camera:
                return self.view.matrix * self.camera.matrix
            return self.view.matrix
        elif self.camera:
            return self.camera.matrix

    def _add_node_to_flat(self, node):
        nt = node.node_type
        if nt:
            if not nt in self.flat_nodes:
                self.flat_nodes[nt] = []
            self.flat_nodes[nt].append(node)

    def _remove_node_from_flat(self, node):
        nt = node.node_type
        if nt:
            if nt in self.flat_nodes:
                self.flat_nodes[nt].remove(node)

    def calculate_view_matrix(self):
        # todo: how to check dirty?
        self._view_matrix = self.get_view_matrix()

    def update(self):
        # self.calculate_transform_matrix()
        self.calculate_render_matrix()
        self.calculate_view_matrix()
        for child in self._children:
            child.update()

class TransformNode(Node):
    def __init__(self, position=None, rotation=None, scale=None, parent=None):
        super(TransformNode, self).__init__(parent)

        # todo: ensure we get vec3s here...
        self.position = position or Vec3(0)
        self.rotation = rotation or Vec3(0)
        # todo: document this shortcut for scale
        self.scale = Vec3(scale) if scale else Vec3(1)

        # todo: cache our local matrix

    def get_local_matrix(self):
        return Mat4.from_transform(self.position, self.rotation, self.scale)

class BillboardTransformNode(TransformNode):
    def __init__(self, position=None, rotation=None, scale=None, parent=None):
        super(BillboardTransformNode, self).__init__(position, rotation, scale, parent)

    def get_local_matrix(self):
        rot = self.rotation
        if self.root is not self and self.root.camera:
            rot = rot - self.root.camera.rotation
        return Mat4.from_transform(self.position, rot, self.scale)

class RenderNode(Node):
    def __init__(self, mesh, parent=None, transparent=False):
        # flag which type of renderable object we have so it can be handled properly
        self.node_type = 'render_%s'%('transparent' if transparent else 'opaque')
        super(RenderNode, self).__init__(parent)

        self.mesh = mesh
        self.transparent = transparent

class LightNode(Node):
    node_type = 'light'

    # TODO: need a way of updating light position based on parent node...
    # maybe just pass the matrix through to be bound to the shader or something?
    def __init__(self, light, parent=None):
        super(LightNode, self).__init__(parent)

        self.light = light
