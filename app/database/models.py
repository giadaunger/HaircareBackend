from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, ForeignKey, UniqueConstraint

class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)


class HaircareProduct(Base):
    __tablename__ = "haircare_products"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    product_name: Mapped[str] = mapped_column(String(100), unique=True)
    product_img: Mapped[str] = mapped_column(String(255))
    product_type: Mapped[str] = mapped_column(String(50)) 
    company: Mapped[str] = mapped_column(String(100))
    
    ingredients: Mapped[list["ProductIngredient"]] = relationship(back_populates="product")

    def __repr__(self):
        return f"<HaircareProduct={self.product_name}>"


class HaircareIngredient(Base):
    __tablename__ = "haircare_ingredients"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    
    products: Mapped[list["ProductIngredient"]] = relationship(back_populates="ingredient")
    focus_areas: Mapped[list["IngredientFocusArea"]] = relationship(back_populates="ingredient")

    def __repr__(self):
        return f"<HaircareIngredient={self.name}>"


class FocusArea(Base):
    __tablename__ = "focus_areas"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    
    ingredients: Mapped[list["IngredientFocusArea"]] = relationship(back_populates="focus_area")

    def __repr__(self):
        return f"<FocusArea={self.name}>"


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