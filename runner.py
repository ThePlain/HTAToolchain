import json
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.filedialog as tkf

import htaparser


class L18NProxy:
    def __init__(self, path):
        self.container = dict()
        with open(path, 'rb') as stream:
            data = json.load(stream)
            self.container.update(data)

    def __getitem__(self, key):
        return self.container.get(key, key)


L18N = L18NProxy('./l18n.json')


class SubView(tk.Frame):
    def __init__(self, root, controller=None):
        super(SubView, self).__init__(root)
        if controller:
            self.controller = controller

    def attach(self, target):
        raise NotImplementedError

class BoneView(SubView):
    pass


class MeshView(SubView):
    pass


class AnimationView(SubView):
    pass


class MaterialView(SubView):
    pass


class CollisionView(SubView):
    pass


class HierGeomView(SubView):
    pass


class BoneBoundView(SubView):
    pass


class GroupView(SubView):
    pass


class TreeView(SubView):
    def __init__(self, *args, **kwargs):
        super(TreeView, self).__init__(*args, **kwargs)

        self._tree = ttk.Treeview(self, columns=('#0', '#1'))
        self._tree.heading('#0', text=L18N['tree_head'])
        self._tree.heading('#1', text=L18N['raw_id'])
        self._tree['displaycolumns'] = ('#0', )
        self._tree.grid(row=0, column=0, sticky=tk.NS)

        self._scroll_y = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self._tree.yview)
        self._scroll_y.grid(row=0, column=1, sticky=tk.NS)

        self._scroll_x = ttk.Scrollbar(self, orient=tk.HORIZONTAL, command=self._tree.xview)
        self._scroll_x.grid(row=1, column=0, sticky=tk.EW)

        self._tree.configure(yscroll=self._scroll_y)

    def attach(self, target):
        self._tree.delete(*self._tree.get_children())
        self._tree.insert('', tk.END, 'Bone', text='Bone')
        self._tree.insert('', tk.END, 'Mesh', text='Mesh')
        self._tree.insert('', tk.END, 'Animation', text='Animation')
        self._tree.insert('', tk.END, 'Skins', text='Skins')
        self._tree.insert('', tk.END, 'Collision', text='Collision')
        self._tree.insert('', tk.END, 'HierGeom', text='HierGeom')
        self._tree.insert('', tk.END, 'BoneBound', text='BoneBound')
        self._tree.insert('', tk.END, 'Group', text='Group')

        if target:
            if len(target.meshes):
                for item in target.bones:
                    self._tree.insert(
                        'Bone',
                        tk.END,
                        text=item.name,
                        values=(item.name,),
                    )

            if len(target.meshes):
                for item in target.meshes:
                    self._tree.insert(
                        'Mesh',
                        tk.END,
                        text=item.name,
                        values=(item.name,),
                    )

            if len(target.animations):
                for item in target.animations:
                    self._tree.insert(
                        'Animation',
                        tk.END,
                        text=item.name,
                        values=(item.name,),
                    )

            if len(target.skins):
                for num, item in enumerate(target.skins):
                    name = f'Skin{num}'
                    self._tree.insert(
                        'Skins',
                        tk.END,
                        text=name,
                        values=(num,),
                    )

            if len(target.collisions):
                for num, item in enumerate(target.collisions):
                    name = f'Collision{num}'
                    self._tree.insert(
                        'Collision',
                        tk.END,
                        text=name,
                        values=(num,),
                    )

            # TODO: FIX Hier geom load
            if False and len(target.hier_geoms):
                for num, item in enumerate(target.hier_geoms):
                    name = f'HierGeom{num}'
                    self._tree.insert(
                        'HierGeom',
                        tk.END,
                        text=name,
                        values=(num,),
                    )

            if len(target.bounds):
                for num, item in enumerate(target.bounds):
                    name = f'BoneBound{num}'
                    self._tree.insert(
                        'BoneBound',
                        tk.END,
                        text=name,
                        values=(num,),
                    )

            if len(target.groups):
                for item in target.groups:
                    self._tree.insert(
                        'Group',
                        tk.END,
                        text=item.name,
                        values=(item.name,),
                    )


class EditorView(tk.Frame):
    def __init__(self, master):
        super(EditorView, self).__init__(master)
        self._current = None
        self._views = {
            'Bone': BoneView(master, self),
            'Mesh': MeshView(master, self),
            'Animation': AnimationView(master, self),
            'Material': MaterialView(master, self),
            'Collision': CollisionView(master, self),
            'HierGeom': HierGeomView(master, self),
            'BoneBound': BoneBoundView(master, self),
            'Group': GroupView(master, self),
        }

    def open_editor(self, target):
        editor_name = type(target).__name__
        self._current = self._views.get(editor_name, None)

        if self._current:
            self._current.attach(target)
            self._current.tkraise()


class Application(tk.Tk):
    def __init__(self, *args, **kwargs):
        super(Application, self).__init__(*args, *kwargs)
        self.minsize(640, 480)
        self.title(L18N['title'])

        # Main menu
        filemenu = tk.Menu(self, tearoff=0)
        self.bind('<Control-o>', self._cmd_open)
        filemenu.add_command(
            label=L18N['open'],
            command=self._cmd_open,
            accelerator="Ctrl+O"
        )
        self.bind('<Control-s>', self._cmd_save)
        filemenu.add_command(
            label=L18N['save'],
            command=self._cmd_save,
            accelerator="Ctrl+S"
        )
        self.bind('<Control-S>', self._cmd_save_as)
        filemenu.add_command(
            label=L18N['save_as'],
            command=self._cmd_save_as,
            accelerator="Ctrl+Shift+S"
        )
        self.bind('<Control-q>', self._cmd_close)
        filemenu.add_command(
            label=L18N['exit'],
            command=self._cmd_close,
            accelerator="Ctrl+Q"
        )

        self._menu = tk.Menu(self)
        self._menu.add_cascade(label=L18N['file'], menu=filemenu)
        self.config(menu=self._menu)

        # Template
        self._tree_view = TreeView(self)
        self._tree_view.grid()

        self._edit_view = EditorView(self)
        self._edit_view.pack(side=tk.RIGHT, fill=tk.Y)

        # Runtime requires
        self._target_item = None
        self._target_path = None

        self._tree_view.attach(self._target_item)

    def _cmd_open(self, event=None):
        self._target_path = tkf.askopenfile(
            filetypes=(
                (L18N['gam_file_type'], '*.gam'),
                (L18N['sam_file_type'], '*.sam'),
            )
        ).name

        self._target_item = htaparser.Parser()
        self._target_item.load('hta', self._target_path)
        self._tree_view.attach(self._target_item)

    def _cmd_save_as(self, event=None):
        self._target_path = tkf.asksaveasfile(
            filetypes=(
                (L18N['gam_file_type'], '*.gam'),
                (L18N['sam_file_type'], '*.sam'),
            )
        )
        self._cmd_save()

    def _cmd_save(self, event=None):
        # TODO: Process save
        pass

    def _cmd_close(self, event=None):
        self.destroy()

if __name__ == '__main__':
    app = Application()
    app.mainloop()
