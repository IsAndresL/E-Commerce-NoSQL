from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import products, ecommerce

app = FastAPI(title="E-commerce API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(products.router, prefix="/products")
app.include_router(ecommerce.router, prefix="/ecommerce")


@app.get("/", include_in_schema=False)
async def root():
	return {
		"service": "E-commerce API",
		"frontend": "http://localhost:5173",
		"docs": "/docs",
		"dashboard_data": "/ecommerce/dashboard-data",
	}
