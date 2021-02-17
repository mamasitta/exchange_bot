import config


class Currency:
    """ Currency class with methods """

    def __init__(self, currency_list):
        self.currency_list = currency_list

    @classmethod
    def get_all(cls):
        connection = config.db
        cur = connection.cursor()
        cur.execute("SELECT * FROM currency")
        result = cur.fetchall()
        currency = [r[0] for r in result]
        return currency

    @classmethod
    def delete_currency(cls):
        connection = config.db
        cur = connection.cursor()
        cur.execute("DELETE FROM currency")
        return True

    @classmethod
    def add_currency(cls, currency_list):
        Currency.delete_currency()
        connection = config.db
        cur = connection.cursor()
        for item in currency_list:
            cur.execute("INSERT INTO currency VALUES ('{}')".format(item))
        cur.close()
        connection.commit()
        return True


