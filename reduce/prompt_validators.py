from prompt_toolkit.validation import Validator, ValidationError


class ChoiceValidator(Validator):
    def __init__(self, choices, allow_empty=False, *args, **kwargs):
        self.choices = set(choices)
        self.allow_empty = allow_empty
        super(Validator, self).__init__(*args, **kwargs)

    def validate(self, document):
        text = document.text

        if text.strip() == '' and self.allow_empty:
            return

        if text not in self.choices:
            raise ValidationError(message=u'Not a valid command.', cursor_position=len(text))
