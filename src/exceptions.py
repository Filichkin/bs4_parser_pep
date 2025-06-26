class ParserFindTagException(Exception):
    """Вызывается, когда парсер не может найти тег."""
    pass


class VersionsListNotFoundException(Exception):
    """Вызывается, когда список с версиями Python не найден."""
    def __init__(self, message='Не найден список с версиями Python'):
        self.message = message
        super().__init__(self.message)
