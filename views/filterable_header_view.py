from PyQt5.QtWidgets import QStyle
from PyQt5.QtCore import Qt, QRect, QPoint, pyqtSignal
from PyQt5.QtGui import QPainter, QColor, QPen, QPolygon
from views.custom_header_view import CustomHeaderView
from views.column_filter_popup import ColumnFilterPopup


class FilterableHeaderView(CustomHeaderView):
    """Header view with filter dropdown buttons and sort indicators."""
    filterApplied = pyqtSignal(int, object)  # (column_index, set or None)

    BUTTON_SIZE = 14
    BUTTON_MARGIN = 4

    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)
        self.active_filters = set()  # columns with active filters
        self._popup = None

    def paintSection(self, painter, rect, logicalIndex):
        """Paint the header section with filter button and sort indicator."""
        super().paintSection(painter, rect, logicalIndex)

        # Draw filter dropdown button in top-right corner
        btn_rect = self._get_button_rect(rect)
        self._draw_filter_button(painter, btn_rect, logicalIndex)

        # Draw sort indicator
        if self.sortIndicatorSection() == logicalIndex:
            self._draw_sort_indicator(painter, rect)

    def _get_button_rect(self, section_rect):
        """Get the rectangle for the filter button in a section."""
        x = section_rect.right() - self.BUTTON_SIZE - self.BUTTON_MARGIN
        y = section_rect.top() + self.BUTTON_MARGIN
        return QRect(x, y, self.BUTTON_SIZE, self.BUTTON_SIZE)

    def _draw_filter_button(self, painter, btn_rect, logicalIndex):
        """Draw the filter dropdown triangle button."""
        painter.save()

        # Highlight if filter is active on this column
        if logicalIndex in self.active_filters:
            painter.setBrush(QColor(70, 130, 180))  # Steel blue for active
            painter.setPen(QPen(QColor(70, 130, 180)))
        else:
            painter.setBrush(QColor(100, 100, 100))
            painter.setPen(QPen(QColor(100, 100, 100)))

        # Draw small downward triangle
        cx = btn_rect.center().x()
        top_y = btn_rect.top() + 4
        bot_y = btn_rect.bottom() - 4
        triangle = QPolygon([
            QPoint(cx - 4, top_y),
            QPoint(cx + 4, top_y),
            QPoint(cx, bot_y)
        ])
        painter.drawPolygon(triangle)
        painter.restore()

    def _draw_sort_indicator(self, painter, rect):
        """Draw sort direction arrow on the left side of the header."""
        painter.save()
        painter.setBrush(QColor(50, 50, 50))
        painter.setPen(Qt.NoPen)

        cx = rect.left() + 10
        cy = rect.center().y()

        if self.sortIndicatorOrder() == Qt.AscendingOrder:
            # Up arrow
            triangle = QPolygon([
                QPoint(cx, cy - 4),
                QPoint(cx - 4, cy + 3),
                QPoint(cx + 4, cy + 3)
            ])
        else:
            # Down arrow
            triangle = QPolygon([
                QPoint(cx - 4, cy - 3),
                QPoint(cx + 4, cy - 3),
                QPoint(cx, cy + 4)
            ])

        painter.drawPolygon(triangle)
        painter.restore()

    def mousePressEvent(self, event):
        """Handle mouse clicks - detect filter button clicks."""
        pos = event.pos()
        logical_index = self.logicalIndexAt(pos)

        if logical_index >= 0:
            # Get section rect
            section_pos = self.sectionPosition(logical_index)
            section_size = self.sectionSize(logical_index)
            section_rect = QRect(section_pos, 0, section_size, self.height())
            btn_rect = self._get_button_rect(section_rect)

            if btn_rect.contains(pos):
                # Filter button clicked - show popup
                self._show_filter_popup(logical_index, btn_rect)
                return

        # Pass through to parent for sorting, resizing, moving
        super().mousePressEvent(event)

    def _show_filter_popup(self, logical_index, btn_rect):
        """Show the column filter popup below the button."""
        model = self.model()
        if model is None:
            return

        # Get the source model (proxy model's source)
        source_model = model
        if hasattr(model, 'sourceModel'):
            source_model = model.sourceModel()

        # Collect unique values from the source model for this column
        unique_values = set()
        for row in range(source_model.rowCount()):
            index = source_model.index(row, logical_index)
            data = source_model.data(index, Qt.DisplayRole)
            cell_value = str(data) if data else ""
            unique_values.add(cell_value)

        # Determine currently checked values
        currently_checked = None
        if hasattr(model, 'column_filters') and logical_index in model.column_filters:
            currently_checked = model.column_filters[logical_index]

        # Show popup
        global_pos = self.mapToGlobal(QPoint(btn_rect.left(), btn_rect.bottom()))
        self._popup = ColumnFilterPopup(
            logical_index, list(unique_values), currently_checked, self
        )
        self._popup.filterApplied.connect(self._on_filter_applied)
        self._popup.move(global_pos)
        self._popup.show()

    def _on_filter_applied(self, column_index, allowed_values):
        """Handle filter applied from popup."""
        if allowed_values is None:
            self.active_filters.discard(column_index)
        else:
            self.active_filters.add(column_index)

        self.filterApplied.emit(column_index, allowed_values)
        self.viewport().update()
