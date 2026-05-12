from PyQt5.QtCore import Qt

def get_header_data(section, orientation, role, visible_fields):
    """Utility function to provide header data for a table."""
    if role == Qt.DisplayRole and orientation == Qt.Horizontal:
        if section == 0:
            return "Raw Log"  # Title for the first column
        else:
            # Return the field name for other columns
            field_names = list(visible_fields.keys())
            if section - 1 < len(field_names):
                return field_names[section - 1]
    return None