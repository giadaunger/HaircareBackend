from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.db_setup import get_db, init_db
from app.database.schemas import BaseModel
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy import select, update, delete, insert, and_, or_, distinct, text, case
from sqlalchemy.sql.expression import func
from typing import Dict, List
from app.database.models import ProductIngredient, HaircareIngredient, HaircareProduct, HairPorosity, IngredientPorosity, IngredientFocusArea, FocusArea 

@asynccontextmanager
async def lifespan(app: FastAPI):
  init_db()
  yield

app =  FastAPI(lifespan=lifespan)

# Middleware
origin = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:5174"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origin,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


class ProductFocus(BaseModel):
    product_type: str
    focus_area: str

class RecommendationRequest(BaseModel):
    hair_porosity: str
    product_focus: Dict[str, str]  # product_type -> focus_area

class ProductResponse(BaseModel):
    id: int
    product_name: str
    company: str
    product_img: str
    product_type: str
    description: str

class RecommendationResponse(BaseModel):
    main_recommendation: ProductResponse
    similar_products: List[ProductResponse]

class FullRecommendations(BaseModel):
    recommendations: Dict[str, RecommendationResponse]

@app.post("/recommendations", response_model=FullRecommendations)
async def get_recommendations(
    request: RecommendationRequest,
    db: Session = Depends(get_db)
):
    recommendations = {}
    
    porosity = db.query(HairPorosity).filter(
        func.lower(HairPorosity.name) == func.lower(request.hair_porosity)
    ).first()
    
    if not porosity:
        raise HTTPException(status_code=400, detail="Invalid hair porosity")

    for product_type, focus_area in request.product_focus.items():
        focus_area_record = db.query(FocusArea).filter(
            func.lower(FocusArea.name) == func.lower(focus_area)
        ).first()
        
        if not focus_area_record:
            continue

        # 1. Hitta inkompatibla ingredienser för porositeten
        incompatible_ingredients = (
            db.query(HaircareIngredient.id)
            .join(IngredientPorosity)
            .filter(
                IngredientPorosity.porosity_id == porosity.id,
                IngredientPorosity.suitability == False
            )
        )

        # 2. Hitta ingredienser för fokusområdet (för ranking senare)
        focus_ingredients = (
            db.query(HaircareIngredient.id)
            .join(IngredientFocusArea)
            .filter(IngredientFocusArea.focus_area_id == focus_area_record.id)
        )

        # 3. Börja med alla produkter av rätt typ
        product_query = (
            db.query(
                HaircareProduct,
                func.count(distinct(case(
                    (ProductIngredient.ingredient_id.in_(focus_ingredients), ProductIngredient.ingredient_id),
                    else_=None
                ))).label('matching_ingredients')
            )
            .join(ProductIngredient)
            .filter(HaircareProduct.product_type == product_type)
            .group_by(HaircareProduct.id)
        )

        # 4. Filtrera bort produkter med inkompatibla ingredienser
        if incompatible_ingredients.count() > 0:
            product_query = product_query.filter(
                ~HaircareProduct.id.in_(
                    db.query(ProductIngredient.product_id)
                    .filter(ProductIngredient.ingredient_id.in_(incompatible_ingredients))
                )
            )

        # 5. Sortera efter antal matchande fokus-ingredienser
        recommended_products = (
            product_query
            .order_by(text('matching_ingredients DESC'))
            .limit(4)
            .all()
        )

        if not recommended_products:
            continue

        main_product = recommended_products[0][0]
        similar_products = [p[0] for p in recommended_products[1:]]

        recommendations[product_type] = RecommendationResponse(
            main_recommendation=ProductResponse(
                id=main_product.id,
                product_name=main_product.product_name,
                company=main_product.company,
                product_img=main_product.product_img,
                product_type=main_product.product_type,
                description=main_product.description
            ),
            similar_products=[
                ProductResponse(
                    id=p.id,
                    product_name=p.product_name,
                    company=p.company,
                    product_img=p.product_img,
                    product_type=p.product_type,
                    description=p.description
                ) for p in similar_products
            ]
        )

    if not recommendations:
        raise HTTPException(
            status_code=404, 
            detail="No recommendations found for the given criteria"
        )

    return FullRecommendations(recommendations=recommendations)