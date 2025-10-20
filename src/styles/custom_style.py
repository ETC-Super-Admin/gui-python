from PySide6.QtWidgets import QProxyStyle, QStyle
from PySide6.QtCore import Qt

class NoFocusProxyStyle(QProxyStyle):
    def drawPrimitive(self, element, option, painter, widget=None):
        """
        Override the drawPrimitive method to prevent the focus rectangle from being drawn.
        """
        if element == QStyle.PrimitiveElement.PE_FrameFocusRect:
            return
        super().drawPrimitive(element, option, painter, widget)
