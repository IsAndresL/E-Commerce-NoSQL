def list_products():
    return [{"id": "1", "name": "Producto demo"}]


class ProductService:
    """Compatibility wrapper for lambdas that expect a ProductService class."""
    def list_products(self):
        return list_products()