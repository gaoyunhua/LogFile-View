from PyQt5.QtWidgets import QHeaderView, QStyleOptionHeader, QStyle
from PyQt5.QtCore import Qt, QRect  # Ensure QRect is imported
from PyQt5.QtGui import QPainter

class CustomHeaderView(QHeaderView):
    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)
        self.setSectionsMovable(True)  # Allow users to move columns
        self.setDefaultAlignment(Qt.AlignCenter)  # Center-align header text
        self.setSectionResizeMode(QHeaderView.Interactive)  # Allow resizing by dragging

    def paintSection(self, painter, rect, logicalIndex):
        painter.save()

        # Create a style option for the header
        option = QStyleOptionHeader()
        self.initStyleOption(option)
        option.rect = rect
        option.section = logicalIndex

        # Draw the header background
        # self.style().drawControl(QStyle.CE_Header, option, painter)

        # Draw the header text with word wrapping
        text = self.model().headerData(logicalIndex, self.orientation(), Qt.DisplayRole)
        if text:
            text_rect = rect.adjusted(4, 4, -4, -4)  # Add padding
            painter.setPen(Qt.black)  # Ensure the text color is visible

            # Set font
            font = painter.font()
            font.setPointSize(10)  # Adjust font size if needed
            painter.setFont(font)

            # Calculate the required height for the text
            font_metrics = painter.fontMetrics()
            text_height = font_metrics.boundingRect(text_rect, Qt.AlignCenter | Qt.TextWordWrap, text).height()

            # Update the rect height if the text wraps
            if text_height > rect.height():
                rect.setHeight(text_height + 8)  # Add some padding

            # Draw the text
            painter.drawText(text_rect, Qt.AlignCenter | Qt.TextWordWrap, text)

        # Draw the border around the section
        painter.setPen(Qt.gray)  # Set the border color
        painter.drawRect(rect)  # Draw the border rectangle

        painter.restore()

    def rectForIndex(self, logicalIndex):
        """Get the rectangle for a specific section."""
        x = self.sectionPosition(logicalIndex)  # Get the x-coordinate of the section
        width = self.sectionSize(logicalIndex)  # Get the width of the section
        return self.rect().adjusted(x, 0, x + width, self.height())

    def sizeHint(self):
        """Dynamically calculate the height of the header based on the wrapped text."""
        size = super().sizeHint()
        max_height = size.height()  # Start with the default height

        # Iterate through all sections to calculate the maximum required height
        for logicalIndex in range(self.model().columnCount()):
            text = self.model().headerData(logicalIndex, self.orientation(), Qt.DisplayRole)
            if text:
                # Use QFontMetrics to calculate the height of the wrapped text
                font_metrics = self.fontMetrics()
                section_width = self.sectionSize(logicalIndex)  # Get the width of the section
                text_rect = QRect(0, 0, section_width - 8, 0)  # Create a rect with the section width and no height
                text_height = font_metrics.boundingRect(text_rect, Qt.AlignCenter | Qt.TextWordWrap, text).height()
                # print(f"Text rect for section {logicalIndex}: {text_rect}, Text height: {text_height}, Text: {text}")
                max_height = max(max_height, text_height + int(text_height/4))  # Add padding

        size.setHeight(max_height)  # Set the calculated maximum height
        return size