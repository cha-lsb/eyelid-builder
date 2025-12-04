"""
Build the eyelid widget using pyside. 
The UI calls eyelid_ctl internally to build the system
"""

import pdb  # noqa
from typing import Optional
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from PySide6.QtCore import *

import maya.cmds as cmds
from eyelid_builder import core as eyelid_core

__version__ = "0.1.4"


class EyelidGui(QDialog):
    """GUI to create an eyelid setup """
    def __init__(self, parent: Optional[QWidget]=None):
        super().__init__(parent)
        self.setWindowTitle(f"Eyelid builder {__version__}")
        self.init_ui()

    def init_ui(self):
        #changing selection preferences to track selection order
        cmds.selectPref(trackSelectionOrder=True)

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        self.ls_lineEdits = []

        row_one_layout = self.init_row1()
        row_two_layout = self.init_row2()
        row_three_layout = self.init_row3()
        row_vertex = self.init_row_vertex()
        row_end_layout = self.init_end_row()


        main_layout.addLayout(row_one_layout)
        main_layout.addLayout(row_two_layout)
        main_layout.addLayout(row_three_layout)
        main_layout.addLayout(row_vertex)
        main_layout.addLayout(row_end_layout)
        main_layout.setAlignment(row_end_layout, Qt.AlignRight | Qt.AlignBottom)
        
    def init_row1(self):
        row_one_layout = QHBoxLayout()
        load_sel_btn = QPushButton('Eyeball mesh')
        load_sel_btn.setToolTip("Select your left or right eye mesh")
        self.selection_mesh = QLineEdit()
        self.ls_lineEdits.append(self.selection_mesh)

        row_one_layout.addWidget(load_sel_btn)
        row_one_layout.addWidget(self.selection_mesh)

        # Signals/Slots
        self.selection_mesh.textChanged.connect(self.on_text_changed)
        load_sel_btn.clicked.connect(self.on_load_mesh)

        return row_one_layout

    def init_row2(self):
        row_two_layout = QHBoxLayout()
        load_ctl_btn = QPushButton('Eye controler')
        load_ctl_btn.setToolTip("Select your eye controler related to your right or left eye")
        self.ctl_selection = QLineEdit()
        self.ls_lineEdits.append(self.ctl_selection)

        row_two_layout.addWidget(load_ctl_btn)
        row_two_layout.addWidget(self.ctl_selection)

        # Signals/Slots
        self.ctl_selection.textChanged.connect(self.on_text_changed)
        load_ctl_btn.clicked.connect(self.on_load_ctl)

        return row_two_layout

    def init_row3(self):
        row_three_layout = QHBoxLayout()
        name_label = QLabel('name')
        self.name_le = QLineEdit()
        row_three_layout.addWidget(name_label)
        row_three_layout.addWidget(self.name_le)

        return row_three_layout

    def init_row_vertex(self):
        row_vertex = QGridLayout()

        load_up_btn = QPushButton('Add vertex up')
        load_dn_btn = QPushButton('Add vertex down')        
        clear_up_btn = QPushButton('Clear')
        clear_dn_btn = QPushButton('Clear')
        row_vertex.addWidget(load_up_btn, 0, 0)
        row_vertex.addWidget(load_dn_btn, 0, 1)
        row_vertex.addWidget(clear_up_btn, 2, 0)
        row_vertex.addWidget(clear_dn_btn, 2, 1)

        self.up_selection = QListWidget()
        self.dn_selection = QListWidget()
        row_vertex.addWidget(self.up_selection, 1, 0)
        row_vertex.addWidget(self.dn_selection, 1, 1)
        self.up_selection.setSelectionMode(QListWidget.ExtendedSelection)
        self.dn_selection.setSelectionMode(QListWidget.ExtendedSelection)

        # Signals/Slots
        load_up_btn.clicked.connect(self.on_load_vertex_up)
        load_dn_btn.clicked.connect(self.on_load_vertex_dn)
        clear_up_btn.clicked.connect(self.on_clear_vertex_up)
        clear_dn_btn.clicked.connect(self.on_clear_vertex_dn)

        self.up_selection.itemSelectionChanged.connect(self.on_vertex_select_maya_up)
        self.dn_selection.itemSelectionChanged.connect(self.on_vertex_select_maya_dn)

        return row_vertex

    def init_end_row(self):

        row_end_layout = QHBoxLayout()
        ok_btn = QPushButton('Ok')
        cancel_btn = QPushButton('Cancel')
        row_end_layout.addSpacing(10)
        row_end_layout.addWidget(ok_btn)
        row_end_layout.addWidget(cancel_btn)

        ok_btn.clicked.connect(self.on_ok_clicked)
        cancel_btn.clicked.connect(self.close)

        return row_end_layout

    # ----- SLOTS
    def on_ok_clicked(self):
        name = self.name_le.text()
        all_valids = []

        for line_edit in self.ls_lineEdits:
            is_valid = self.check_input(line_edit)
            all_valids.append(is_valid)            
        if not all(all_valids):
            return

        if not name:
            self.name_le.setText('eyelid')

        self.do_it()

    def on_text_changed(self):
        line_edit = self.sender()
        self.check_input(line_edit)

    def on_load_mesh(self):
        selectionM = cmds.ls(sl=True, type='transform')
        if not selectionM:
            return

        selM = selectionM[-1]

        #accepting only meshes
        if cmds.listRelatives(selM, shapes=True, type='mesh'):
            self.selection_mesh.setText(selM)
        else:
            self.selection_mesh.setPlaceholderText("Selected object must be a mesh")

    def on_load_ctl(self):
        selectionC = cmds.ls(sl=True, type='transform')
        if not selectionC:
            return

        selC = selectionC[-1]
        self.ctl_selection.setText(selC)
        
    def on_load_vertex_up(self):
        selectionVU = cmds.ls(os=True, fl=True)
        if not selectionVU:
            return

        sel = selectionVU
        self.up_selection.addItems(sel)

    def on_load_vertex_dn(self):
        selectionVD = cmds.ls(os=True, fl=True)
        if not selectionVD:
            return

        sel = selectionVD
        self.dn_selection.addItems(sel)

    def on_clear_vertex_up(self):
        self.clear_vertex_from_list_widget(list_widget=self.up_selection)

    def on_clear_vertex_dn(self):
        self.clear_vertex_from_list_widget(list_widget=self.dn_selection)

    def on_vertex_select_maya_up(self):
        selected_itemsUp = self.up_selection.selectedItems()
        #pdb.set_trace()
        to_select = []
        for item in selected_itemsUp:
            to_select.append(item.text())

        cmds.select(to_select, r=True)

    def on_vertex_select_maya_dn(self):
        selected_items = self.dn_selection.selectedItems()
        #pdb.set_trace()
        to_select = []
        for item in selected_items:
            to_select.append(item.text())

        cmds.select(to_select, r=True)


    # ----- REGULAR METHODS
    def check_input(self, line_edit):
        if not cmds.objExists(line_edit.text()):
            self.color_line_edit_in_red(line_edit)
            return False
        if not cmds.nodeType(line_edit.text()) == 'transform':
            self.color_line_edit_in_red(line_edit)
            return False

        self.color_line_edit_in_green(line_edit)
        return True

    @staticmethod
    def _color_line_edit(widget: QLineEdit, color: str):
        """
        Color the given line edit with the given color, 
        using style sheet. A string is expected

        Args:
            widget (QLineEdit): line edit to color
            color (str): what color to apply to the line edit
        """
        widget.setStyleSheet(f'border: 1px solid {color};')

    def color_line_edit_in_red(self, line_edit: QLineEdit):
        self._color_line_edit(line_edit, "red")

    def color_line_edit_in_green(self, line_edit: QLineEdit):
        self._color_line_edit(line_edit, "green")

    def clear_vertex_from_list_widget(self, list_widget: QListWidget):
        selected_items = list_widget.selectedItems()
        if not selected_items:  # remove everything
            list_widget.clear()
        else:
            for item in selected_items:
                row = list_widget.row(item)
                to_delete = list_widget.takeItem(row)
                del to_delete

    def do_it(self):
        """Run the actual building operation inside maya"""
        eyeball = self.selection_mesh.text()
        name = self.name_le.text()
        eyeCtl = self.ctl_selection.text()
        vertexUp = [self.up_selection.item(index).text() for index in range(self.up_selection.count())]
        vertexDown = [self.dn_selection.item(index).text() for index in range(self.dn_selection.count())]

        if self.up_selection.count() >= 2 and self.dn_selection.count() >= 2:
            eyelid_core.do_it(eyeball, vertexUp, vertexDown, name, eyeCtl)
        else:
            QMessageBox.warning(self, "Oops!", "Please add up and down vertices to proceed.")


if __name__ == "__main__":
    import eyelid.eyelid_widget as eyelidwg
    win = eyelidwg.EyelidGui()
    win.show()
