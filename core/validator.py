class CanonicalValidator:
    def validate(self, msg):
        if hasattr(msg, "quantity") and msg.quantity <= 0:
            raise ValueError("Quantity must be positive")
        if hasattr(msg, "price") and msg.price <= 0:
            raise ValueError("Price must be positive")
