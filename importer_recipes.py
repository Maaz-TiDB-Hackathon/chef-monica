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

# Load your CSV file
df = pd.read_csv("documents/recipes.csv")  # change this to your actual file path

# 1. Null values per column
null_counts = df.isnull().sum()

# 2. Max length per column (for object/string columns)
max_lengths = df.select_dtypes(include=['object']).applymap(lambda x: len(str(x)) if pd.notnull(x) else 0).max()

# Combine both into a summary
summary = pd.DataFrame({
    'null_count': null_counts,
    'max_length': max_lengths
})

for i in range(len(summary['null_count'])):
    if summary['null_count'][i] > 0:
        print(f"Column '{summary.index[i]}' has {summary['null_count'][i]} null values.")
    if summary['max_length'][i] > 250:
        print(f"Column '{summary.index[i]}' has a max length of {summary['max_length'][i]}, which exceeds the limit of 250 characters.")


#Create the table in TiDB
recipe_table = tidb_client.create_table(schema=Recipe, if_exists="skip")

chunk_size = 100
last_recipe_id = 409317
n=0
for chunk in pd.read_csv("documents/recipes.csv", chunksize=chunk_size):
    recipe_list = []
    chunk = chunk.replace({np.nan: None})
    for _, row in chunk.iterrows():
        recipe = Recipe()
        recipe.id = row['RecipeId']
        recipe.name = row['Name']
        recipe.author_id = row['AuthorId']
        recipe.author_name = row['AuthorName']
        recipe.cook_time = row['CookTime']
        recipe.prep_time = row['PrepTime']
        recipe.total_time = row['TotalTime']
        recipe.date_published = row['DatePublished']
        recipe.description = row['Description']
        recipe.images = row['Images']
        recipe.recipe_category = row['RecipeCategory']
        recipe.keywords = row['Keywords']
        recipe.recipe_ingredient_quantities = row['RecipeIngredientQuantities']
        recipe.recipe_ingredients = row['RecipeIngredientParts']
        recipe.aggregate_rating = row['AggregatedRating']
        recipe.rating_count = row['ReviewCount']
        recipe.calories = row['Calories']
        recipe.fat_content = row['FatContent']
        recipe.saturated_fat_content = row['SaturatedFatContent']
        recipe.cholesterol_content = row['CholesterolContent']
        recipe.sodium_content = row['SodiumContent']
        recipe.carbohydrate_content = row['CarbohydrateContent']
        recipe.fiber_content = row['FiberContent']
        recipe.sugar_content = row['SugarContent']
        recipe.protein_content = row['ProteinContent']
        recipe.recipe_servings = row['RecipeServings']
        recipe.recipe_yield = row['RecipeYield']
        recipe.recipe_instructions = row['RecipeInstructions']
        if(recipe.id > last_recipe_id):
            recipe_list.append(recipe)
        
    if(len(recipe_list) > 0):
        n += 1
        print (f"Inserting records into TiDB for the {n} time...");
        recipe_table.bulk_insert(recipe_list)