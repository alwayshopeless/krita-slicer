from krita import *
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel,
    QHBoxLayout, QPushButton, QInputDialog,
    QComboBox, QSpinBox
)

class KritaSlicerUnified(Extension):
    def __init__(self, parent):
        super().__init__(parent)

    def setup(self):
        pass

    def action(self):
        pass

    def createActions(self, window):
        action = window.createAction(
            "slice_layer_action_unified",
            "Slice Layer",
            "tools/scripts"
        )
        action.triggered.connect(self.slice_layer)

    # Unified dialog
    def open_unified_dialog(self, qwin):
        dialog = QDialog(qwin)
        dialog.setWindowTitle("Slice Settings")
        layout = QVBoxLayout(dialog)

        layout.addWidget(QLabel("Rows:"))
        rows = QSpinBox()
        rows.setRange(1, 500)
        rows.setValue(1)
        layout.addWidget(rows)

        layout.addWidget(QLabel("Columns:"))
        cols = QSpinBox()
        cols.setRange(1, 500)
        cols.setValue(10)
        layout.addWidget(cols)

        btn_ok = QPushButton("Slice")
        layout.addWidget(btn_ok)

        result = {"rows": None, "cols": None}

        def accept():
            result["rows"] = rows.value()
            result["cols"] = cols.value()
            dialog.accept()

        btn_ok.clicked.connect(accept)

        dialog.exec_()
        return result["rows"], result["cols"]

    def slice_normal(self, doc, node, rows, cols):
        group = doc.createNode("Slices (Grid)", "grouplayer")
        doc.rootNode().addChildNode(group, None)

        rect = node.bounds()
        layer_x, layer_y = rect.x(), rect.y()
        layer_w, layer_h = rect.width(), rect.height()

        base_x = node.position().x()
        base_y = node.position().y()

        xs = [(i * layer_w) // cols for i in range(cols + 1)]
        ys = [(i * layer_h) // rows for i in range(rows + 1)]

        idx = 1

        for r in range(rows):
            for c in range(cols):
                x0, x1 = xs[c], xs[c + 1]
                y0, y1 = ys[r], ys[r + 1]
                w, h = x1 - x0, y1 - y0

                slice_layer = doc.createNode(f"Slice {idx}", "paintlayer")
                group.addChildNode(slice_layer, None)

                px = node.pixelData(layer_x + x0, layer_y + y0, w, h)
                slice_layer.setPixelData(px, base_x + x0, base_y + y0, w, h)

                idx += 1

        doc.refreshProjection()

    def slice_layer(self):
        app = Krita.instance()
        doc = app.activeDocument()
        win = app.activeWindow()
        v = win.activeView() if win else None

        if not doc or not v:
            return

        selected_nodes = v.selectedNodes()
        if not selected_nodes:
            return

        src_node = selected_nodes[0]
        qwin = win.qwindow()

        rows, cols = self.open_unified_dialog(qwin)
        if not rows or not cols:
            return

        self.slice_normal(doc, src_node, rows, cols)

Krita.instance().addExtension(KritaSlicerUnified(Krita.instance()))
