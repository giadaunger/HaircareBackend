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
        print(f"\n=== Processing {product_type} with {focus_area} ===")
        focus_area_record = db.query(FocusArea).filter(
            func.lower(FocusArea.name) == func.lower(focus_area)
        ).first()
        
        if not focus_area_record:
            print(f"Focus area not found: {focus_area}")
            continue
        print(f"Found focus area: {focus_area_record.name}")

        # 1. Hitta inkompatibla ingredienser för porositeten
        incompatible_ingredients = (
            db.query(HaircareIngredient.id)
            .join(IngredientPorosity)
            .filter(
                IngredientPorosity.porosity_id == porosity.id,
                IngredientPorosity.suitability == False
            )
        )

        # 2. Hitta ingredienser för fokusområdet
        focus_ingredients = (
            db.query(HaircareIngredient.id)
            .join(IngredientFocusArea)
            .filter(IngredientFocusArea.focus_area_id == focus_area_record.id)
        )
        print(f"Number of focus ingredients: {focus_ingredients.count()}")
        
        products_with_focus = (
        db.query(HaircareProduct)
        .join(ProductIngredient)
        .filter(
            HaircareProduct.product_type == product_type,
            ProductIngredient.ingredient_id.in_(focus_ingredients)
        )
        .distinct()
        .all()
        )
        print(f"Products with focus ingredients: {len(products_with_focus)}")
        for p in products_with_focus:
            print(f"- {p.product_name}")

        products = db.query(HaircareProduct).filter(
            HaircareProduct.product_type == product_type).all()
        print(f"Total number of {product_type} products in database: {len(products)}")

        # 3. Hämta produkter som har ingredienser för fokusområdet
        product_query = (
            db.query(
                HaircareProduct,
                func.count(distinct(case(
                    (ProductIngredient.ingredient_id.in_(focus_ingredients), ProductIngredient.ingredient_id),
                    else_=None
                ))).label('matching_ingredients')
            )
            .join(ProductIngredient)
            .filter(
                HaircareProduct.product_type == product_type,
                # Säkerställ att produkten har minst en ingrediens från fokusområdet
                HaircareProduct.id.in_(
                    db.query(ProductIngredient.product_id)
                    .filter(ProductIngredient.ingredient_id.in_(focus_ingredients))
                    .group_by(ProductIngredient.product_id)
                    .having(func.count(ProductIngredient.ingredient_id) > 0)
                )
            )
            .group_by(HaircareProduct.id)
        )
        print(f"Number of incompatible ingredients: {incompatible_ingredients.count()}")

        initial_products = product_query.all()
        print(f"Products before incompatibility filter: {len(initial_products)}")
        for p in initial_products:
            print(f"- {p[0].product_name} (matching ingredients: {p[1]})")

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
    
    print(f"Final recommended products: {len(recommended_products)}")
    for p in recommended_products:
        print(f"- {p[0].product_name} (matching ingredients: {p[1]})")

    return FullRecommendations(recommendations=recommendations)


@app.get("/product/{product_id}")
async def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(HaircareProduct).filter(HaircareProduct.id == product_id).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return {
        "id": product.id,
        "product_name": product.product_name,
        "company": product.company,
        "product_type": product.product_type,
        "description": product.description,
        "product_img": product.product_img,
        "ingredients": product.ingredients
    }


@app.post("/product-recommendations")
async def get_product_recommendations(
    request: Request,
    db: Session = Depends(get_db)
):
    body = await request.json()
    porosity = body.get("hair_porosity")
    product_type = body.get("product_type")
    focus_area = body.get("focus_area")
    current_product_id = body.get("current_product_id")

    # Hitta porosity ID
    porosity_record = db.query(HairPorosity).filter(
        func.lower(HairPorosity.name) == func.lower(porosity)
    ).first()
    
    if not porosity_record:
        raise HTTPException(status_code=400, detail="Invalid hair porosity")

    # Hitta focus area ID
    focus_area_record = db.query(FocusArea).filter(
        func.lower(FocusArea.name) == func.lower(focus_area)
    ).first()
    
    if not focus_area_record:
        raise HTTPException(status_code=400, detail="Invalid focus area")

    # Hitta inkompatibla ingredienser
    incompatible_ingredients = (
        db.query(HaircareIngredient.id)
        .join(IngredientPorosity)
        .filter(
            IngredientPorosity.porosity_id == porosity_record.id,
            IngredientPorosity.suitability == False
        )
    )

    # Hitta fokuserade ingredienser
    focus_ingredients = (
        db.query(HaircareIngredient.id)
        .join(IngredientFocusArea)
        .filter(IngredientFocusArea.focus_area_id == focus_area_record.id)
    )

    # Hämta produkter som har ingredienser för fokusområdet
    product_query = (
        db.query(
            HaircareProduct,
            func.count(distinct(case(
                (ProductIngredient.ingredient_id.in_(focus_ingredients), ProductIngredient.ingredient_id),
                else_=None
            ))).label('matching_ingredients')
        )
        .join(ProductIngredient)
        .filter(
            HaircareProduct.product_type == product_type,
            HaircareProduct.id != current_product_id,  # Exkludera nuvarande produkt
            # Säkerställ att produkten har minst en ingrediens från fokusområdet
            HaircareProduct.id.in_(
                db.query(ProductIngredient.product_id)
                .filter(ProductIngredient.ingredient_id.in_(focus_ingredients))
                .group_by(ProductIngredient.product_id)
                .having(func.count(ProductIngredient.ingredient_id) > 0)
            )
        )
        .group_by(HaircareProduct.id)
    )

    # Filtrera bort produkter med inkompatibla ingredienser
    if incompatible_ingredients.count() > 0:
        product_query = product_query.filter(
            ~HaircareProduct.id.in_(
                db.query(ProductIngredient.product_id)
                .filter(ProductIngredient.ingredient_id.in_(incompatible_ingredients))
            )
        )

    # Sortera efter antal matchande fokus-ingredienser
    recommended_products = (
        product_query
        .order_by(text('matching_ingredients DESC'))
        .limit(3)
        .all()
    )

    return {
        "similar_products": [
            {
                "id": p[0].id,
                "product_name": p[0].product_name,
                "company": p[0].company,
                "product_img": p[0].product_img,
                "product_type": p[0].product_type,
                "description": p[0].description
            } 
            for p in recommended_products
        ]
    }