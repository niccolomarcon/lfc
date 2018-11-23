class Production():
    def __init__(self, driver=None, body=None):
        def type_check(c):
            return type(c) is str

        if all(map(type_check, driver)) and all(map(type_check, body)):
            self.driver = driver.copy()
            self.body = body.copy()
        else:
            raise TypeError

    def from_text(text):
        driver, body = tuple(map(list, text.split('->')))
        return Production(driver, body)

    def __str__(self):
        body = self.body if len(self.body) > 0 else ['𝜀']
        chars = self.driver + ['->'] + body
        return ''.join(chars)