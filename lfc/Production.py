from .utils import is_list_of


class Production:
    def __init__(self, driver: list, body: list) -> 'Production':
        """
        Create a new Production from two lists of strings
        :param driver:
        :param body:
        """
        if is_list_of(driver, str) and is_list_of(body, str):
            self.driver, self.body = driver.copy(), body.copy()
        else:
            raise TypeError

    def from_text(text: str) -> 'Production':
        """
        Create a new Production from a string in this format: "driver->body"
        :return:
        """
        driver, body = tuple(map(list, text.split('->')))
        return Production(driver, body)

    def copy(self) -> 'Production':
        return Production(self.driver, self.body)

    def __str__(self) -> str:
        body = self.body if len(self.body) > 0 else ['𝜀']
        chars = self.driver + ['->'] + body
        return ''.join(chars)

    def __hash__(self) -> int:
        return self.__str__().__hash__()

    def __eq__(self, other: 'Production') -> bool:
        if type(other) is not Production:
            raise TypeError
        return self.__str__() == other.__str__()