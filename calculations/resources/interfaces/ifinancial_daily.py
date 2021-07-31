class IFinancialDaily:
    """ Base Class """

    def __init__(self):
        """ Constructor """
        pass

    @staticmethod
    def query_data():
        """ query_data """
        print('Base class for query_data')

    @classmethod
    def main_daily(cls):
        """ main_daily """
        print('Base class for main_daily')

    @classmethod
    def main(cls):
        """ main """
        print('Base class for main')
