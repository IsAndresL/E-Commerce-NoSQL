from app.models.ecommerce import DashboardResponse, OrderDetails, UserProfile
from app.services.ecommerce_service import ECommerceService

class ECommerceDashboardService:
    def __init__(self, ecommerce_service: ECommerceService | None = None):
        self.ecommerce_service = ecommerce_service or ECommerceService()

    def build_dashboard(self, user_id: str, order_id: str) -> DashboardResponse:
        profile = self.ecommerce_service.get_user_profile(user_id) or UserProfile()
        orders = self.ecommerce_service.get_recent_orders(user_id)
        user_has_order = self.ecommerce_service.user_has_order(user_id, order_id)

        if user_has_order:
            order_details = self.ecommerce_service.get_order_details(order_id) or OrderDetails()
            items = self.ecommerce_service.get_order_items(order_id)
        else:
            order_details = OrderDetails()
            items = []

        return DashboardResponse(
            user_id=user_id,
            order_id=order_id,
            profile=profile,
            orders=orders,
            order_details=order_details,
            items=items,
        )