from pydantic import BaseModel, Field

class HaircareProductSchema(BaseModel):
    product_name: str = Field(
        description="name of the haircare product, unique and required",
        min_length=1, 
        max_length=100
    )
    product_img: str = Field(
        description="URL to product image",
        max_length=255
    )
    product_type: str = Field(
        description="type of product (shampoo, conditioner, etc.)",
        max_length=50
    )
    company: str = Field(
        description="name of the company that makes the product",
        max_length=100
    )

class HaircareIngredientSchema(BaseModel):
    name: str = Field(
        description="name of the ingredient, unique and required",
        min_length=1,
        max_length=100
    )

class FocusAreaSchema(BaseModel):
    name: str = Field(
        description="name of the focus area, unique and required",
        min_length=1,
        max_length=100
    )

class ProductIngredientSchema(BaseModel):
    product_id: int = Field(
        description="the id linking to the haircare product table, unique including ingredient id + required"
    )
    ingredient_id: int = Field(
        description="the id linking to the ingredient table, unique including product id + required"
    )

class IngredientFocusAreaSchema(BaseModel):
    ingredient_id: int = Field(
        description="the id linking to the ingredient table, unique including focus area id + required"
    )
    focus_area_id: int = Field(
        description="the id linking to the focus area table, unique including ingredient id + required"
    )