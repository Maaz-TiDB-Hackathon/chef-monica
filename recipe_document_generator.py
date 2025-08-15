from tidb import tidb_client, embed_fn
from pytidb.schema import TableModel, Field, FullTextField
from pytidb.filters import GT, IN
from sqlalchemy import Column, Text
from sqlmodel import Field
import datetime
from chunking import bulk_insert_recipe_embeddings

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
            # recipe_instructions_vec: list[float] = embed_fn.VectorField(
            #     source_field="recipe_instructions",
            #     description="Embedding for recipe instructions"
            # )

class Review(TableModel):
            id: int | None = Field(default=None, primary_key=True)
            recipe_id: str = Field()
            author_id: int = Field()
            author_name: str = Field()
            rating: str = Field(nullable=True)
            review: str = FullTextField(fts_parser="MULTILINGUAL")
            # review_vec: list[float] = embed_fn.VectorField(
            #     source_field="review",
            #     description="Embedding for review"
            # )
            date_submitted: datetime.datetime = Field(
                default_factory=lambda: datetime.datetime.now(datetime.UTC)
            )
            date_modified: datetime.datetime = Field(
                default_factory=lambda: datetime.datetime.now(datetime.UTC)
            )

def sanitize_text(value):
    """
    Cleans up a value for text embedding.
    - Converts None or non-string types to a string
    - Strips leading/trailing whitespace
    - Ensures empty string instead of None
    """
    if value is None:
        return ""
    if not isinstance(value, str):
        value = str(value)
    return value.strip()

def get_recipe_text_dict(recipe_chunk_list):
    """
    Constructs a dictionary of text representations of recipes for chat.
    """
    # recipe_list = get_recipe_table().query(filters={"id": {IN: [recipe_chunk['recipe_id'] for recipe_chunk in recipe_chunk_list]}}, limit = 3).to_pydantic()
    recipe_text_dict = {}
    for recipe in recipe_chunk_list:
        recipe_text = get_recipe_json(recipe)
        recipe_text_dict[recipe["id"]] = recipe_text
    return recipe_text_dict

def getImageURL(images):
    """
    Returns the image URL for a recipe.
    If no image is provided, returns ''.
    """
    if not images or images == "":
        return ''
    image_list = images.split(', ')
    if len(image_list) == 0:
        return ''
    image = image_list[0].strip()  # URL encode spaces
    image = image.replace('"', '')
    return image

def getImageURLs(images):
    """
    Returns the image URL for a recipe.
    If no image is provided, returns ''.
    """
    if not images or images == "":
        return ''
    image_list = images.split(', ')
    if len(image_list) == 0:
        return ''
    return [image.strip().replace('"','') for image in image_list]  # Strip whitespace from each image URL
    image = image_list[0].strip()  # URL encode spaces
    image = image.replace('"', '')
    return image

def get_recipe_json(recipe):
    """
    Constructs a json representation of a recipe.
    This would be used for displaying the recipe in a user-friendly format.
    It includes all relevant fields.
    Args:
        recipe (dict): The recipe dictionary containing all details.
    Returns:
        dict: A json containing the recipe details
    """
    return {
         "id": recipe["id"],
        "name": sanitize_text(recipe["name"]),
        "description": sanitize_text(recipe["description"]),
        "author": sanitize_text(recipe["author_name"]),
        "category": sanitize_text(recipe["recipe_category"]),
        "ingredients": sanitize_text(recipe["recipe_ingredients"]),
        "instructions": sanitize_text(recipe["recipe_instructions"]),
        "cook_time": sanitize_text(recipe["cook_time"]),
        "prep_time": sanitize_text(recipe["prep_time"]),
        "total_time": sanitize_text(recipe["total_time"]),
        "aggregate_rating": sanitize_text(recipe["aggregate_rating"]),
        "rating_count": sanitize_text(recipe["rating_count"]),
        "calories": sanitize_text(recipe["calories"]),
        "fat_content": sanitize_text(recipe["fat_content"]),
        "saturated_fat_content": sanitize_text(recipe["saturated_fat_content"]),
        "cholesterol_content": sanitize_text(recipe["cholesterol_content"]),
        "sodium_content": sanitize_text(recipe["sodium_content"]),
        "carbohydrate_content": sanitize_text(recipe["carbohydrate_content"]),
        "fiber_content": sanitize_text(recipe["fiber_content"]),
        "sugar_content": sanitize_text(recipe["sugar_content"]),
        "protein_content": sanitize_text(recipe["protein_content"]),
        "servings": sanitize_text(recipe["recipe_servings"]),
        "yield": sanitize_text(recipe["recipe_yield"]),
        "image_URLs": getImageURLs(sanitize_text(recipe["images"]))
    }

def get_recipe_text_for_embedding(recipe):
    """
    Constructs a text representation of a recipe for embedding.
    """
    return f"""Name: {sanitize_text(recipe.name)} 
        | Description: {sanitize_text(recipe.description)}
        | Category: {sanitize_text(recipe.recipe_category)}
        | Keywords: {sanitize_text(recipe.keywords)}
        | Ingredients: {sanitize_text(recipe.recipe_ingredients)}
        | Instructions: {sanitize_text(recipe.recipe_instructions)}
        """

def get_recipe_table():
    """
    Returns the recipe table from TiDB.
    """
    recipe_table = tidb_client.create_table(schema=Recipe, if_exists="skip")
    return recipe_table

def get_review_table():
    """
    Returns the recipe table from TiDB.
    """
    review_table = tidb_client.create_table(schema=Review, if_exists="skip")
    return review_table

def insert_all_recipe_embeddings(last_id: int = 0, batch_size: int = 10):
    """
    Inserts all recipe and review embeddings into the database.
    Args:
        last_id (int): The last recipe ID processed. Defaults to 0.
    """
    recipe_table = get_recipe_table()
    print(f"Starting to insert embeddings for recipes starting from ID {last_id}...")
    recipe_list = recipe_table.query(filters={"id": {GT: last_id}}, order_by={"id": "asc"}, limit=batch_size).to_pydantic()
    recipe_text_dict = {}
    for recipe in recipe_list:
        if recipe.id <= last_id:
            continue
        last_id = recipe.id
        # Prepare the text for embedding
        recipe_text_dict[recipe.id] = get_recipe_text_for_embedding(recipe)
    bulk_insert_recipe_embeddings(recipe_text_dict, batch_size=batch_size)
    insert_all_recipe_embeddings(last_id=last_id, batch_size=batch_size)

#insert_all_recipe_embeddings(37, batch_size=3)  # Start from the beginning with a batch size of 10

#recipe = get_recipe_table().query(filters={"id": 56}).to_pydantic()[0]  # Ensure the table is created
# review_list = get_review_table().query(filters={"recipe_id": recipe.id}).to_pydantic()
#recipe_text = get_recipe_text_for_embedding(recipe)
#recipe_json = get_recipe_json(recipe)
#print(recipe_json)