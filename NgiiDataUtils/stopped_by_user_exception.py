#########################
# Define User Exception
#########################
class StoppedByUserException(Exception):
    def __init__(self, message=""):
        # Call the base class constructor with the parameters it needs
        super(StoppedByUserException, self).__init__(message)