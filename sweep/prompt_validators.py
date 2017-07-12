from prompt_toolkit.validation import Validator, ValidationError


class ChoiceValidator(Validator):
    def __init__(self, choices, commands, allow_empty=False, *args, **kwargs):
        self.choices = set(choices)
        self.commands = set(commands)
        self.allow_empty = allow_empty
        super(Validator, self).__init__(*args, **kwargs)

    def validate(self, document):
        text = document.text

        if text.strip() == '' and self.allow_empty:
            return
        elif text.strip() == '' and not self.allow_empty:
            raise ValidationError(message=u'Empty input not allowed.', cursor_position=len(text))

        valid = False

        if text in self.choices:
            valid = True

        if text.split()[0] in self.commands:
            # commands can have args afterwards
            valid = True

        if not valid:
            raise ValidationError(message=u'Not a valid choice.', cursor_position=len(text))
