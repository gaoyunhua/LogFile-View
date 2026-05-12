from models.field_model import FieldModel


class FieldController:
    def __init__(self, field_model):
        self.field_model = field_model

    def get_all_fields(self):
        """Retrieve all field definitions."""
        return self.field_model.get_all_fields()

    def get_field_data(self, field_name):
        """Retrieve the data for a specific field."""
        return self.field_model.get_field_data(field_name)  # Delegate to the model

    def add_field(self, field_name, regex, visibility=False, sorted=False):
        """Add a new field definition."""
        return self.field_model.add_field(field_name, regex, visibility, sorted)

    def update_field(self, old_name, new_name, regex, visibility, sorted_field):
        """Update an existing field definition."""
        return self.field_model.update_field(old_name, new_name, regex, visibility, sorted_field)

    def delete_field(self, field_name):
        """Delete a field definition."""
        return self.field_model.delete_field(field_name)