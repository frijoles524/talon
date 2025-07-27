import sys
import os
import tempfile
import json
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QObject, QCoreApplication, QEvent
from ui_components.ui_base_full import UIBaseFull
from ui_components.ui_title_text import UITitleText
from ui_components.ui_header_text import UIHeaderText
from ui_components.ui_image import UIImage
from ui_components.ui_button import UIButton



class ResizeHandler(QObject):
    def __init__(self, overlay, img_label, buttons):
        super().__init__(overlay)
        self.overlay = overlay
        self.img_label = img_label
        self.buttons = buttons

    def eventFilter(self, obj, event):
        if obj is self.overlay and event.type() == QEvent.Resize:
            self.position_elements()
        return False

    def position_elements(self):
        W = self.overlay.width()
        H = self.overlay.height()
        pix = self.img_label.pixmap()
        if pix:
            pix_h = pix.height()
            pix_y = (H - pix_h) // 2
            bottom = pix_y + pix_h
        else:
            bottom = H // 2
        spacing = 200
        for btn in self.buttons:
            btn.adjustSize()
        widths = [btn.width() for btn in self.buttons]
        total_width = sum(widths) + spacing * (len(self.buttons) - 1)
        x = (W - total_width) // 2
        y = bottom + 100
        for btn, w in zip(self.buttons, widths):
            btn.move(x, y)
            x += w + spacing



def main():
    app = QApplication.instance() or QApplication(sys.argv)
    base = UIBaseFull()
    overlay = base.primary_overlay
    title_label = UITitleText("Warning: This is not a fresh Windows installation.", parent=overlay)
    header_label = UIHeaderText("Continuing may cause irreversable system corruption or data loss.", parent=overlay)
    img_label = UIImage("icon-warning.png", parent=overlay, horizontal_buffer=0.45)
    img_label.lower()
    buttons = [UIButton("Continue", (255, 204, 0), parent=overlay), UIButton("   Exit   ", (144, 238, 144), parent=overlay)]
    buttons[0].clicked.connect(lambda: [overlay.close() for overlay in base.overlays])
    buttons[1].clicked.connect(lambda: sys.exit(0))
    handler = ResizeHandler(overlay, img_label, buttons)
    overlay.installEventFilter(handler)
    handler.position_elements()
    title_label.raise_()
    header_label.raise_()
    for b in buttons:
        b.raise_()
    base.show()
    sys.exit(app.exec_())



if __name__ == "__main__":
    main()
