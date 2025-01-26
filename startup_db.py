from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app.db_setup import get_db
from app.database.models import HaircareIngredient, HaircareProduct, IngredientFocusArea, ProductIngredient, FocusArea
from datetime import datetime

db: Session = next(get_db())

try:
    # Creates ingredients
    ingredients_data = [
        {'ingredient': 'Water'},
        {'ingredient': 'Stearyl Alcohol'},
        {'ingredient': 'Cetyl Alcohol'},
        {'ingredient': 'Stearamidopropyl Dimethylamine'},
        {'ingredient': 'Parfum/Fragrance'},
        {'ingredient': 'Phenoxyethanol'},
        {'ingredient': 'Propylene Glycol'},
        {'ingredient': 'Dicetyldimonium Chloride'},
        {'ingredient': 'Glutamic Acid'},
        {'ingredient': 'Quaternium-80'},
        {'ingredient': 'Methylparaben'},
        {'ingredient': 'Tocopheryl Acetate'},
        {'ingredient': 'Propylparaben'},
        {'ingredient': 'EDTA'},
        {'ingredient': 'Limonene'},
        {'ingredient': 'Glycerin'},
        {'ingredient': 'Sodium Chloride'},
        {'ingredient': 'Linalool'},
        {'ingredient': 'Hexyl Cinnamal'},
        {'ingredient': 'Histidine'},
        {'ingredient': 'Microcitrus Australasica Fruit Extract'}
    ]

    for ingredient_data in ingredients_data:
        ingredient = HaircareIngredient(**ingredient_data)
        db.add(ingredient)

    db.commit()


    # Creates fokus areas
    focus_areas_data = [
        {'name': 'Dry scalp'},
        {'name': 'Oily scalp'},
        {'name': 'Dandruff control'},
        {'name': 'Split end treatment'},
        {'name': 'Deep hydration'},
        {'name': 'Hair growth stimulation'},
        {'name': 'Balance oil production'},
        {'name': 'Moisture retention'},
        {'name': 'Color protection'},
        {'name': 'Frizz control'}
    ]

    for focus_area_data in focus_areas_data:
        focus_area = FocusArea(**focus_area_data)
        db.add(focus_area)

    db.commit()


    # Cteates products
    products_data = [
        {
            'product_name': 'Color Brilliance',
            'company': 'Wella Professionals Invigo',
            'product_img': '/images/conditioner1.png',
            'product_type': 'conditioner',
            'description': 'Wella Professionals Invigo Color Brilliance Conditioner for Coarse Hair is a professional color-preserving conditioner for colored hair. This professional conditioner is designed to preserve the vibrancy of color and improve the hair surface, while leaving your hair smooth, shiny and irresistibly soft to the touch. This color-preserving conditioner contains Color Brilliance-Blend™ and Lime Caviar, an ingredient known for being rich in various antioxidants and vitamins, and actively helps control the oxidation process that occurs after coloring. Available in two sizes: 200 ml and 1000 ml. Your routine for instant color brilliance for medium to fine colored hair.'
        },
    ]

    for product_data in products_data:
        product = HaircareProduct(**product_data)
        db.add(product)

    db.commit()


    # Koppla produkter till ingredienser
    product_ingredients_data = [
        {'product_id': 1, 'ingredient_id': 1},  
        {'product_id': 1, 'ingredient_id': 2},  
        {'product_id': 1, 'ingredient_id': 3},  
        {'product_id': 1, 'ingredient_id': 4}, 
        {'product_id': 1, 'ingredient_id': 5},  
        {'product_id': 1, 'ingredient_id': 6},
        {'product_id': 1, 'ingredient_id': 7},  
        {'product_id': 1, 'ingredient_id': 8},  
        {'product_id': 1, 'ingredient_id': 9},  
        {'product_id': 1, 'ingredient_id': 10}, 
        {'product_id': 1, 'ingredient_id': 11},  
        {'product_id': 1, 'ingredient_id': 12},
        {'product_id': 1, 'ingredient_id': 13},  
        {'product_id': 1, 'ingredient_id': 14},  
        {'product_id': 1, 'ingredient_id': 15},  
        {'product_id': 1, 'ingredient_id': 16}, 
        {'product_id': 1, 'ingredient_id': 17},  
        {'product_id': 1, 'ingredient_id': 18},
        {'product_id': 1, 'ingredient_id': 19}, 
        {'product_id': 1, 'ingredient_id': 20},  
        {'product_id': 1, 'ingredient_id': 21}
    ]

    for pi_data in product_ingredients_data:
        pi = ProductIngredient(**pi_data)
        db.add(pi)

    db.commit()


    # Koppla ingredienser till fokusområden
    ingredient_focus_areas_data = [
        {'ingredient_id': 2, 'focus_area_id': 5},  # Stearyl Alcohol - Deep hydration
        {'ingredient_id': 3, 'focus_area_id': 5},  # Cetyl Alcohol - Deep hydration
        {'ingredient_id': 9, 'focus_area_id': 8},  # Glutamic Acid - Moisture retention
        {'ingredient_id': 12, 'focus_area_id': 9}, # Tocopheryl Acetate - Color protection (antioxidant)
        {'ingredient_id': 16, 'focus_area_id': 8}, # Glycerin - Moisture retention
        {'ingredient_id': 21, 'focus_area_id': 9}  # Microcitrus Australasica Fruit Extract - Color protection
    ]

    for ifa_data in ingredient_focus_areas_data:
        ifa = IngredientFocusArea(**ifa_data)
        db.add(ifa)

    db.commit()
  
    
    print("Hudvårdsprodukter och ingredienser har lagts till i databasen!")

except Exception as e:
    db.rollback()
    print(f"Ett fel uppstod: {e}")

finally:
    db.close()