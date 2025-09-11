import streamlit as st
from typing import Optional, List
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
from llm import llm
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate
from typing import ClassVar
from tidb import tidb_client, embed_fn
from recipe_document_generator import get_recipe_text_dict
import json

# 1. Define filter schema
class RecipeFilters(BaseModel):
    min_protein: Optional[float] = Field(default=None, description="Minimum protein in grams")
    max_calories: Optional[int] = Field(default=None, description="Maximum calories")
    max_cook_time: Optional[int] = Field(default=None, description="Maximum cook time in minutes")
    max_prep_time: Optional[int] = Field(default=None, description="Maximum prep time in minutes")
    max_total_time: Optional[int] = Field(default=None, description="Maximum total time in minutes")
    query_text: str = Field(..., description="Remaining query for semantic or full-text search")

# 2. Output parser
parser = PydanticOutputParser(pydantic_object=RecipeFilters)

# 3. Prompt
prompt = PromptTemplate(
    template="""
You are a filter extraction assistant for a recipe search system.

From the user query, extract filters with the exact types given below:
- min_protein: float or null
- max_calories: integer or null
- query_text: string containing the rest of the query, without filter keywords.

Respond in **JSON** only, matching this schema:
{format_instructions}

User query: {query}
""",
    input_variables=["query"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
)

# 4. LLM
#llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# 5. Tool
class SearchWithFilterTool(BaseTool):
    name: ClassVar[str] = "search_with_filter"
    description: ClassVar[str] = "Searches for recipes after extracting typed filters and query text from user input"
    
    def _run(self, query: str):
        prompt_str = prompt.format(query=query)
        output = llm.invoke(prompt_str)
        recipe_filters =  parser.parse(output.content)
        st.write(f"Extracted filters: ")
        st.json(json.loads(recipe_filters.json()))
        return search_recipes_with_filters_vector(recipe_filters, k = 50)

def search_recipes_with_filters_vector(recipeFilters: RecipeFilters, k: int) -> List[dict]:
    query_vec = embed_fn.get_query_embedding(recipeFilters.query_text, source_type="text")     
    vector_query = """SELECT recipe.id as id,recipe.name as name, recipe.description as description, recipe.author_name as author_name, 
    recipe.recipe_category as recipe_category, recipe.recipe_ingredients as recipe_ingredients, recipe.recipe_instructions as recipe_instructions, recipe.cook_time as cook_time, recipe.prep_time as prep_time, recipe.total_time as total_time,
    recipe.aggregate_rating as aggregate_rating, recipe.rating_count as rating_count, recipe.calories as calories, recipe.fat_content as fat_content, recipe.saturated_fat_content as saturated_fat_content, recipe.cholesterol_content as cholesterol_content,
    recipe.sodium_content as sodium_content, recipe.carbohydrate_content as carbohydrate_content, recipe.fiber_content as fiber_content, recipe.sugar_content as sugar_content, recipe.protein_content as protein_content, recipe.recipe_servings as recipe_servings,
    recipe.recipe_yield as recipe_yield, recipe.images as images, 
    min(vec_cosine_distance(recipe_chunk.text_vec, :recipe_query_vector)) AS vs_distance
    FROM recipe, recipe_chunk
    WHERE recipe.id = recipe_chunk.recipe_id 
    """
    params = {
        "recipe_query_vector": str(query_vec),
        "k": k
    }
    if (recipeFilters.min_protein is not None):
        vector_query += " AND recipe.protein_content> :min_protein "
        params["min_protein"] = recipeFilters.min_protein
    if (recipeFilters.max_calories is not None):
        vector_query += " AND recipe.calories< :max_calories "
        params["max_calories"] = recipeFilters.max_calories
    if (recipeFilters.max_cook_time is not None):
        vector_query += " AND TIME_TO_SEC(recipe.d_cook_time)/60 < :max_cook_time "
        params["max_cook_time"] = recipeFilters.max_cook_time
    if (recipeFilters.max_prep_time is not None):
        vector_query += " AND TIME_TO_SEC(recipe.d_prep_time)/60 < :max_prep_time "
        params["max_prep_time"] = recipeFilters.max_prep_time
    if (recipeFilters.max_total_time is not None):
        vector_query += " AND TIME_TO_SEC(recipe.d_total_time)/60 < :max_total_time "
        params["max_total_time"] = recipeFilters.max_total_time

    vector_query += """
    GROUP BY recipe.id
    ORDER BY vs_distance asc
    LIMIT :k"""

    result_list =  tidb_client.query(sql=vector_query, params=params).to_list()
    result_list = result_list[:5] if len(result_list)>5 else result_list
    recipe_text_dict = get_recipe_text_dict(result_list)
    return {
        "status": "success",
        "message": "Operation complete",
        "data": list(recipe_text_dict.values())
    }
    


        