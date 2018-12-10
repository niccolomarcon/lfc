from .utils import is_list_of


class Production:
    @property
    def driver(self) -> list:
        return self._driver

    @driver.setter
    def driver(self, value: list):
        if not is_list_of(value, str):
            raise TypeError('driver is not a list of strings')

        if len(value) == 0:
            raise ValueError('driver is empty')

        self._driver = value.copy()

    @property
    def body(self) -> list:
        return self._body

    @body.setter
    def body(self, value: list):
        if not is_list_of(value, str):
            raise TypeError('body is not a list of strings')

        self._body = value.copy()

    def __init__(self, driver: list, body: list) -> 'Production':
        """
        Create a new Production from two lists of strings
        :param driver:
        :param body:
        """
        self.driver, self.body = driver, body

    def from_text(text: str) -> 'Production':
        """
        Create a new Production from a string in this format: "driver->body"
        :return:
        """
        if type(text) != str:
            raise TypeError('text is not a string')

        n_arrows = text.count('->')
        if n_arrows == 0:
            raise ValueError('no arrow (->) in _prd text')
        if n_arrows > 1:
            raise ValueError('too many arrows (->) in _prd text')

        driver, body = tuple(map(list, text.split('->')))
        return Production(driver, body)

    def copy(self) -> 'Production':
        """
        Create a copy of the _prd
        :return:
        """
        return Production(self.driver, self.body)

    def __str__(self) -> str:
        body = self.body if len(self.body) > 0 else ['𝜀']
        chars = self.driver + ['->'] + body
        return ''.join(chars)

    def __hash__(self) -> int:
        return self.__str__().__hash__()

    def __eq__(self, other: 'Production') -> bool:
        if type(other) is not Production:
            return False
        return self.__str__() == other.__str__()

    def __copy__(self):
        return self.copy()
