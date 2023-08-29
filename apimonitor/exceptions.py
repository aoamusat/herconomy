class InvalidTransactionError(Exception):
    def __init__(self, message="Sender and recipient cannot be the same user."):
        self.message = message
        super().__init__(self.message)
