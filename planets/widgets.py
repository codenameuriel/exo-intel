from django_filters.widgets import RangeWidget

class LabeledRangeWidget(RangeWidget):
    """
    A custom RangeWidget that adds 'min' and 'max' placeholder text
    to the input fields
    """
    def __init__(self, min_placeholder=None, max_placeholder=None, attrs=None):
        super().__init__(attrs)

        if min_placeholder:
            self.widgets[0].attrs['placeholder'] = min_placeholder
        if max_placeholder:
            self.widgets[1].attrs['placeholder'] = max_placeholder