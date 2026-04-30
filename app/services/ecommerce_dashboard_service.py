from app.core.config import get_settings
from app.db.redis import RedisCache, get_redis_cache
from app.models.ecommerce import DashboardResponse, OrderDetails, UserProfile
from app.services.ecommerce_service import ECommerceService


class ECommerceDashboardService:
    def __init__(
        self,
        ecommerce_service: ECommerceService | None = None,
        cache: RedisCache | None = None,
    ):
        self.ecommerce_service = ecommerce_service or ECommerceService()
        self.cache = cache or RedisCache()
        self.cache_ttl_seconds = get_settings().redis_cache_ttl_seconds

    async def get_dashboard_data(self, user_id: str, order_id: str):
        cache_key = f"dashboard:{user_id}:{order_id}"
        cached = await self.cache.get(cache_key)
        if cached:
            return cached  # ya es un DashboardResponse serializado

        profile = self.ecommerce_service.get_user_profile(user_id) or UserProfile()
        orders = self.ecommerce_service.get_recent_orders(user_id)
        user_has_order = self.ecommerce_service.user_has_order(user_id, order_id)

        if user_has_order:
            order_details = self.ecommerce_service.get_order_details(order_id) or OrderDetails()
            items = self.ecommerce_service.get_order_items(order_id)
        else:
            order_details = OrderDetails()
            items = []

        dashboard = DashboardResponse(
            user_id=user_id,
            order_id=order_id,
            profile=profile,
            orders=orders,
            order_details=order_details,
            items=items,
        )

        await self.cache.set(cache_key, dashboard, ex=self.cache_ttl_seconds)
        return dashboard

    def build_dashboard(self, user_id: str, order_id: str) -> DashboardResponse:
        cache_key = self.cache.build_key("dashboard", user_id, order_id)
        cached_dashboard = self.cache.get_json(cache_key)
        if cached_dashboard:
            return DashboardResponse.model_validate(cached_dashboard)

        profile = self.ecommerce_service.get_user_profile(user_id) or UserProfile()
        orders = self.ecommerce_service.get_recent_orders(user_id)
        user_has_order = self.ecommerce_service.user_has_order(user_id, order_id)

        if user_has_order:
            order_details = self.ecommerce_service.get_order_details(order_id) or OrderDetails()
            items = self.ecommerce_service.get_order_items(order_id)
        else:
            order_details = OrderDetails()
            items = []

        dashboard = DashboardResponse(
            user_id=user_id,
            order_id=order_id,
            profile=profile,
            orders=orders,
            order_details=order_details,
            items=items,
        )

        self.cache.set_json(
            cache_key,
            dashboard.model_dump(mode="json"),
            ttl_seconds=self.cache_ttl_seconds,
        )

        return dashboard
