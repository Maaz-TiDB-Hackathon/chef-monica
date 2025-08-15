from tidb import tidb_client
import numpy as np

query = """SELECT recipe.id,name, description, min(vec_cosine_distance(recipe_chunk.text_vec, :recipe_instructions_vector)) AS distance
FROM recipe, recipe_chunk
WHERE recipe.id = recipe_chunk.recipe_id AND recipe.protein_content> :protein_content AND recipe.carbohydrate_content> :carbohydrate_content and recipe.calories> :calories
GROUP BY recipe.id
ORDER BY distance
LIMIT 5"""

vector_size = 1536
random_vector = np.random.rand(vector_size)  # Generates random floats between 0 and 1
recipe_instructions_vector = str(random_vector.tolist())

params = {
    "protein_content": 20,
    "carbohydrate_content": 50,
    "calories": 100,
    "recipe_instructions_vector": recipe_instructions_vector     
    }
answer_list = tidb_client.query(sql = query, params = params).to_list()
print(answer_list)