from typing import Optional, List
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
from llm import llm
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate
from typing import ClassVar
from tidb import tidb_client, embed_fn
from recipe_document_generator import get_recipe_text_dict
from langchain_core.documents import Document
import json
from pytidb.fusion import _normalize_score


# 1. Define filter schema
class RecipeFilters(BaseModel):
    min_protein: Optional[float] = Field(default=0.0, description="Minimum protein in grams")
    max_calories: Optional[int] = Field(default=4000.0, description="Maximum calories")
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
        if(recipe_filters.min_protein is None):
            recipe_filters.min_protein = 0.0
        if(recipe_filters.max_calories is None):
            recipe_filters.max_calories = 4000
        print(recipe_filters)
        #return search_recipes_with_filters(recipe_filters)
        return search_recipes_with_filters_hybrid(recipe_filters)

# Example usage
#tool = FilterExtractorTool()
#result = tool.run("Find me Italian pasta under 500 calories with at least 20g protein")
#print(result.dict())

def search_recipes_with_filters(recipeFilters: RecipeFilters) -> List[Document]:
    # Example: naive cosine similarity search
    query_vec = embed_fn.get_query_embedding(recipeFilters.query_text, source_type="text")
    # top_recipe_chunks = get_table().search(query_vec).limit(3).to_list()
    # distance_dict = {chunk['recipe_id']: chunk['_distance'] for chunk in top_recipe_chunks}
    # recipe_text_dict = get_recipe_text_dict(top_recipe_chunks)
    
    vector_query = """SELECT recipe.id as id,recipe.name as name, recipe.description as description, recipe.author_name as author_name, 
    recipe.recipe_category as recipe_category, recipe.recipe_ingredients as recipe_ingredients, recipe.recipe_instructions as recipe_instructions, recipe.cook_time as cook_time, recipe.prep_time as prep_time, recipe.total_time as total_time,
    recipe.aggregate_rating as aggregate_rating, recipe.rating_count as rating_count, recipe.calories as calories, recipe.fat_content as fat_content, recipe.saturated_fat_content as saturated_fat_content, recipe.cholesterol_content as cholesterol_content,
    recipe.sodium_content as sodium_content, recipe.carbohydrate_content as carbohydrate_content, recipe.fiber_content as fiber_content, recipe.sugar_content as sugar_content, recipe.protein_content as protein_content, recipe.recipe_servings as recipe_servings,
    recipe.recipe_yield as recipe_yield, recipe.images as images, 
    min(vec_cosine_distance(recipe_chunk.text_vec, :recipe_instructions_vector)) AS distance
FROM recipe, recipe_chunk
WHERE recipe.id = recipe_chunk.recipe_id AND recipe.protein_content> :min_protein AND recipe.calories< :max_calories
GROUP BY recipe.id
ORDER BY distance asc
LIMIT :k"""
    params = params = {
"min_protein": recipeFilters.min_protein,
"max_calories": recipeFilters.max_calories,
"recipe_instructions_vector": str(query_vec),
"k": 5    
}
    result_list = tidb_client.query(sql=vector_query, params=params).to_list()
    recipe_text_dict = get_recipe_text_dict(result_list)
    return [Document(page_content=json.dumps(recipe_text_dict[recipe_chunk['id']]), metadata={"id": recipe_chunk['id'], "distance": recipe_chunk['distance'], "similarity": 1 - recipe_chunk['distance']}) for recipe_chunk in  result_list]

def search_recipes_with_filters_hybrid(recipeFilters: RecipeFilters) -> List[Document]:
    semantic_list = search_recipes_with_filters_vector(recipeFilters=recipeFilters, k = 50) # Since sometimes number of results may get reduced due to post-filtering
    fulltext_list = search_recipes_with_filters_fulltext(recipeFilters=recipeFilters, k = 10)
    sorted_list = normalized_fusion(semantic_list, fulltext_list);
    return sorted_list[:5]

def search_recipes_with_filters_fulltext(recipeFilters: RecipeFilters, k: int) -> List[Document]:
    query = """SELECT recipe.id as id,recipe.name as name, recipe.description as description, recipe.author_name as author_name, 
    recipe.recipe_category as recipe_category, recipe.recipe_ingredients as recipe_ingredients, recipe.recipe_instructions as recipe_instructions, recipe.cook_time as cook_time, recipe.prep_time as prep_time, recipe.total_time as total_time,
    recipe.aggregate_rating as aggregate_rating, recipe.rating_count as rating_count, recipe.calories as calories, recipe.fat_content as fat_content, recipe.saturated_fat_content as saturated_fat_content, recipe.cholesterol_content as cholesterol_content,
    recipe.sodium_content as sodium_content, recipe.carbohydrate_content as carbohydrate_content, recipe.fiber_content as fiber_content, recipe.sugar_content as sugar_content, recipe.protein_content as protein_content, recipe.recipe_servings as recipe_servings,
    recipe.recipe_yield as recipe_yield, recipe.images as images, 
    fts_match_word(:query_text, description) AS match_score
FROM recipe
WHERE recipe.protein_content> :min_protein AND recipe.calories< :max_calories
AND fts_match_word(:query_text,description)
ORDER BY match_score asc
LIMIT :k"""
    params = params = {
"min_protein": recipeFilters.min_protein,
"max_calories": recipeFilters.max_calories,
"query_text": recipeFilters.query_text,
"k": k    
}
    result_list = tidb_client.query(sql=query, params=params).to_list()
    recipe_text_dict = get_recipe_text_dict(result_list)
    return [Document(page_content=json.dumps(recipe_text_dict[recipe_chunk['id']]), metadata={"id": recipe_chunk['id'],"match_score": recipe_chunk['match_score']}) for recipe_chunk in  result_list]

def search_recipes_with_filters_vector(recipeFilters: RecipeFilters, k: int) -> List[Document]:
    # Example: naive cosine similarity search
    query_vec = embed_fn.get_query_embedding(recipeFilters.query_text, source_type="text") 
    # top_recipe_chunks = get_table().search(query_vec).limit(3).to_list()
    # distance_dict = {chunk['recipe_id']: chunk['_distance'] for chunk in top_recipe_chunks}
    # recipe_text_dict = get_recipe_text_dict(top_recipe_chunks)
    
    vector_query = """SELECT recipe.id as id,recipe.name as name, recipe.description as description, recipe.author_name as author_name, 
    recipe.recipe_category as recipe_category, recipe.recipe_ingredients as recipe_ingredients, recipe.recipe_instructions as recipe_instructions, recipe.cook_time as cook_time, recipe.prep_time as prep_time, recipe.total_time as total_time,
    recipe.aggregate_rating as aggregate_rating, recipe.rating_count as rating_count, recipe.calories as calories, recipe.fat_content as fat_content, recipe.saturated_fat_content as saturated_fat_content, recipe.cholesterol_content as cholesterol_content,
    recipe.sodium_content as sodium_content, recipe.carbohydrate_content as carbohydrate_content, recipe.fiber_content as fiber_content, recipe.sugar_content as sugar_content, recipe.protein_content as protein_content, recipe.recipe_servings as recipe_servings,
    recipe.recipe_yield as recipe_yield, recipe.images as images, 
    min(vec_cosine_distance(recipe_chunk.text_vec, :recipe_instructions_vector)) AS vs_distance
FROM recipe, recipe_chunk
WHERE recipe.id = recipe_chunk.recipe_id AND recipe.protein_content> :min_protein AND recipe.calories< :max_calories
GROUP BY recipe.id
ORDER BY vs_distance asc
LIMIT :k"""
    params = params = {
"min_protein": recipeFilters.min_protein,
"max_calories": recipeFilters.max_calories,
"recipe_instructions_vector": str(query_vec),
"k": k  
}
    result_list =  tidb_client.query(sql=vector_query, params=params).to_list()
    recipe_text_dict = get_recipe_text_dict(result_list)
    return [Document(page_content=json.dumps(recipe_text_dict[recipe_chunk['id']]), metadata={"id": recipe_chunk['id'],"vs_distance": recipe_chunk['vs_distance']}) for recipe_chunk in  result_list]

def normalized_fusion(semantic_list: List[Document], fulltext_list: List[Document]):
    """
    Merge two lists of search results using Normalization + Weighted Sum.
    
    semantic_list: list of Document — e.g. semantic search results
    fulltext_list: list of Document — e.g. full-text search results

    Returns: list of (Document) sorted by best score
    """
    for semantic_document in semantic_list:
        normalized_score = _normalize_score(semantic_document.metadata["vs_distance"], "cosine")
        semantic_document.metadata["normalized_score"] = normalized_score
    
    for fulltext_document in fulltext_list:
        normalized_score = _normalize_score(fulltext_document.metadata["match_score"], "bm25")
        fulltext_document.metadata["normalized_score"] = normalized_score
    
    document_dict = {}
    for semantic_document in semantic_list:
        document_dict[semantic_document.metadata["id"]] = semantic_document
    for fulltext_document in fulltext_list:
        if(fulltext_document.metadata["id"] in document_dict):
            doc = document_dict[fulltext_document.metadata["id"]]
            doc.metadata["normalized_score"]+=fulltext_document.metadata["normalized_score"]
            doc.metadata["match_score"]=fulltext_document.metadata["match_score"]
        else:
            document_dict[fulltext_document.metadata["id"]] = fulltext_document
    
    def score(document: Document):
        return document.metadata["normalized_score"]

    return sorted(document_dict.values(), key=score, reverse=True)
    


        