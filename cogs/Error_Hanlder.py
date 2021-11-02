class NoData(Exception):
    def __init__(self, message='Key Empty'):
        # Call the base class constructor with the parameters it needs
        super(NoData, self).__init__(message)
