class NotEnoughProductQuantityError(Exception):

    def __init__(self, *args, product_id: int):
        super().__init__(*args)
        self.product_id = product_id


class ProductQuantityOutOfRangeError(Exception):

    def __init__(self, *args, product_id: int):
        super().__init__(*args)
        self.product_id = product_id
