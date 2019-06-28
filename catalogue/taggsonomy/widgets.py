from django.forms import widgets


class ColorInputWidget(widgets.Input):
    input_type = 'color'
    template_name = 'taggsonomy/widgets/colorinput.html'
