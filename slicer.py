from krita import *
from PyQt5.QtWidgets import QInputDialog

class KritaSlicer(Extension):

    def __init__(self, parent):
        super().__init__(parent)

    def setup(self):
        pass

    def action(self):
        pass

    def createActions(self, window):
        action = window.createAction(
            "slice_layer_action",
            "Slice Layer to parts",
            "tools/scripts"
        )
        action.triggered.connect(self.slice_layer)

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

        node = selected_nodes[0]
        qwin = win.qwindow()

        rows, ok = QInputDialog.getInt(qwin, "Rows", "Rows:", 1, 1, 500)
        if not ok:
            return

        cols, ok = QInputDialog.getInt(qwin, "Columns", "Columns:", 10, 1, 500)
        if not ok:
            return

        group = doc.createNode("Slices", "grouplayer")
        doc.rootNode().addChildNode(group, None)

        rect = node.bounds()
        layer_x, layer_y = rect.x(), rect.y()
        layer_w, layer_h = rect.width(), rect.height()

        base_x = node.position().x()
        base_y = node.position().y()

        xs = [ (i * layer_w) // cols for i in range(cols+1) ]
        ys = [ (i * layer_h) // rows for i in range(rows+1) ]

        slice_index = 0

        for r in range(rows):
            for c in range(cols):
                x0 = xs[c]
                x1 = xs[c+1]
                y0 = ys[r]
                y1 = ys[r+1]

                w = x1 - x0
                h = y1 - y0

                slice_layer = doc.createNode(f"Slice {slice_index+1}", "paintlayer")
                group.addChildNode(slice_layer, None)

                px = node.pixelData(layer_x + x0, layer_y + y0, w, h)
                slice_layer.setPixelData(px, base_x+ x0, base_y + y0, w, h)

                slice_index += 1

        doc.refreshProjection()


Krita.instance().addExtension(KritaSlicer(Krita.instance()))
