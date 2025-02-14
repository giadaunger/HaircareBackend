from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, ForeignKey, UniqueConstraint, Text, Boolean

class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)


class HaircareProduct(Base):
    __tablename__ = "haircare_products"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    product_name: Mapped[str] = mapped_column(String(100), unique=True)
    company: Mapped[str] = mapped_column(String(100))
    price: Mapped[int] = mapped_column(Integer)
    product_img: Mapped[str] = mapped_column(String(255))
    product_type: Mapped[str] = mapped_column(String(50)) 
    description: Mapped[str] = mapped_column(String(5000))
    
    ingredients: Mapped[list["ProductIngredient"]] = relationship(back_populates="product")

    def __repr__(self):
        return f"<HaircareProduct={self.product_name}>"


class HaircareIngredient(Base):
    __tablename__ = "haircare_ingredients"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ingredient: Mapped[str] = mapped_column(Text, unique=True)
    
    products: Mapped[list["ProductIngredient"]] = relationship(back_populates="ingredient")
    focus_areas: Mapped[list["IngredientFocusArea"]] = relationship(back_populates="ingredient")
    porosity_associations: Mapped[list["IngredientPorosity"]] = relationship(back_populates="ingredient")

    def __repr__(self):
        return f"<HaircareIngredient={self.ingredient}>"


class FocusArea(Base):
    __tablename__ = "focus_areas"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    
    ingredients: Mapped[list["IngredientFocusArea"]] = relationship(back_populates="focus_area")

    def __repr__(self):
        return f"<FocusArea={self.name}>"
    

class IngredientPorosity(Base):
    __tablename__ = "ingredient_porosity"

    ingredient_id: Mapped[int] = mapped_column(ForeignKey("haircare_ingredients.id"), primary_key=True)
    porosity_id: Mapped[int] = mapped_column(ForeignKey("hair_porosity.id"), primary_key=True)
    suitability: Mapped[bool] = mapped_column(Boolean, nullable=False)  # True = suitable, False = not_suitable

    ingredient: Mapped["HaircareIngredient"] = relationship(back_populates="porosity_associations")
    porosity: Mapped["HairPorosity"] = relationship(back_populates="ingredients")

    

class HairPorosity(Base):
    __tablename__ = "hair_porosity"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(20), unique=True)  

    ingredients: Mapped[list["IngredientPorosity"]] = relationship(back_populates="porosity")


class ProductIngredient(Base):
    __tablename__ = "product_ingredients"
    product_id: Mapped[int] = mapped_column(ForeignKey("haircare_products.id"), primary_key=True)
    ingredient_id: Mapped[int] = mapped_column(ForeignKey("haircare_ingredients.id"), primary_key=True)
    
    product: Mapped["HaircareProduct"] = relationship(back_populates="ingredients")
    ingredient: Mapped["HaircareIngredient"] = relationship(back_populates="products")


class IngredientFocusArea(Base):
    __tablename__ = "ingredient_focus_areas"
    ingredient_id: Mapped[int] = mapped_column(ForeignKey("haircare_ingredients.id"), primary_key=True)
    focus_area_id: Mapped[int] = mapped_column(ForeignKey("focus_areas.id"), primary_key=True)
    
    ingredient: Mapped["HaircareIngredient"] = relationship(back_populates="focus_areas")
    focus_area: Mapped["FocusArea"] = relationship(back_populates="ingredients")