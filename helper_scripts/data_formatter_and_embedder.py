from tidb import tidb_client, embed_fn
from pytidb.schema import TableModel, Field, FullTextField
from sqlalchemy import Column, Text
from sqlmodel import Field
import datetime
import pandas as pd
import numpy as np

class Recipe(TableModel):
            id: int | None = Field(default=None, primary_key=True)
            name: str = Field()
            author_id: int = Field()
            author_name: str = Field()
            cook_time: str = Field(nullable=True)
            prep_time: str = Field()
            total_time: str = Field()
            date_published: datetime.datetime = Field(
                        default_factory=lambda: datetime.datetime.now(datetime.UTC)
                    )
            description: str = FullTextField(fts_parser="MULTILINGUAL")#Field(max_length=6330, nullable=True)
            images: str = Field(sa_column=Column(Text))
            recipe_category: str = Field(nullable=True)
            keywords: str = Field(max_length=425, nullable=True)
            recipe_ingredient_quantities: str = Field(max_length=280, nullable=True)
            recipe_ingredients: str = Field(max_length=820)
            aggregate_rating: float = Field(nullable=True)
            rating_count: int = Field(nullable=True)
            calories: float = Field()
            fat_content: float = Field()
            saturated_fat_content: float = Field()
            cholesterol_content: float = Field()
            sodium_content: float = Field()
            carbohydrate_content: float = Field()
            fiber_content: float = Field()
            sugar_content: float = Field()
            protein_content: float = Field()
            recipe_servings: float = Field(nullable=True)
            recipe_yield: str = Field(nullable=True)
            recipe_instructions: str = FullTextField(fts_parser="MULTILINGUAL")
            recipe_instructions_vec: list[float] = embed_fn.VectorField(
                source_field="recipe_instructions",
                description="Embedding for recipe instructions"
            )
recipe_table = tidb_client.open_table(table_name = 'recipe')
recipe_list = recipe_table.query(filters={"id": 39}, limit=1).to_list()

for recipe in recipe_list:
    print(recipe['name'])
    print(recipe['description'])
    print(recipe['recipe_category'])
    print(recipe['keywords'][2:-1])
    print(recipe['recipe_ingredients'][2:-1])
    print(recipe['cook_time'])#NULL OR VALID
    print(recipe['prep_time']) 
    print(recipe['total_time'])
    print(recipe['aggregate_rating'])#--
    print(recipe['rating_count'])#-- USE ALL THE RATINGS FOR THIS RECIPE HERE?
    print(recipe['recipe_instructions'][2:-1])#-- USE ALL THE RATINGS FOR THIS RECIPE HERE?

    print("---\n")



# image: No image -> null | character(0)

# 1 image -> "https://www.themealdb.com/images/media/meals/qtqvqw1511812027.jpg"
# more than 1 image -> c("https://www.themealdb.com/images/media/meals/qtqvqw1511812027.jpg", "https://www.themealdb.com/images/media/meals/qtqvqw1511812027.jpg")
# Recipe Name: Chocolate Cake
# Category: Dessert
# Ingredients: flour, cocoa powder, eggs, butter, sugar
# Instructions: Mix ingredients, bake at 180°C for 40 minutes.
