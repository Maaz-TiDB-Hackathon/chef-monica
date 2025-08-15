# import streamlit as st
# from llm import llm
# from tidb import tidb_client, embed_fn
# from langchain_core.prompts import ChatPromptTemplate
# from langchain.chains.combine_documents import create_stuff_documents_chain
# from langchain.chains import create_retrieval_chain
# import json
# from langchain_core.retrievers import BaseRetriever
# from langchain_core.documents import Document
# from typing import List
# import numpy as np
# from chunking import get_table
# from recipe_document_generator import get_recipe_text_dict
# from search_with_filter_tool import RecipeFilters

# #  "name": sanitize_text(recipe.name),
# #         "description": sanitize_text(recipe.description),
# #         "author": sanitize_text(recipe.author_name),
# #         "category": sanitize_text(recipe.recipe_category),
# #         "ingredients": sanitize_text(recipe.recipe_ingredients),
# #         "instructions": sanitize_text(recipe.recipe_instructions),
# #         "cook_time": sanitize_text(recipe.cook_time),
# #         "prep_time": sanitize_text(recipe.prep_time),
# #         "total_time": sanitize_text(recipe.total_time),
# #         "aggregate_rating": sanitize_text(recipe.aggregate_rating),
# #         "rating_count": sanitize_text(recipe.rating_count),
# #         "calories": sanitize_text(recipe.calories),
# #         "fat_content": sanitize_text(recipe.fat_content),
# #         "saturated_fat_content": sanitize_text(recipe.saturated_fat_content),
# #         "cholesterol_content": sanitize_text(recipe.cholesterol_content),
# #         "sodium_content": sanitize_text(recipe.sodium_content),
# #         "carbohydrate_content": sanitize_text(recipe.carbohydrate_content),
# #         "fiber_content": sanitize_text(recipe.fiber_content),
# #         "sugar_content": sanitize_text(recipe.sugar_content),
# #         "protein_content": sanitize_text(recipe.protein_content),
# #         "servings": sanitize_text(recipe.recipe_servings),
# #         "yield": sanitize_text(recipe.recipe_yield),
# #         "image_URLs": getImageURLs(sanitize_text(recipe.images))
# # Create a retriever for movie plots using TiDB


# # class RecipeSearchWithFilterTool(StructuredTool):
# #     name: ClassVar[str]= "search_recipe_with_filter"
# #     description: ClassVar[str]= 'Search recipes using the format { "min_protein": 2.0, "max_calories": 2000.0, "query_text": "A dish with chicken"}'
# #     args_schema: Type[RecipeFilters] = RecipeFilters

# def search_recipes_with_filters(recipeFilters: RecipeFilters) -> List[Document]:
#     # Example: naive cosine similarity search
#     query_vec = embed_fn.get_query_embedding(recipeFilters.query_text, source_type="text") 
#     # top_recipe_chunks = get_table().search(query_vec).limit(3).to_list()
#     # distance_dict = {chunk['recipe_id']: chunk['_distance'] for chunk in top_recipe_chunks}
#     # recipe_text_dict = get_recipe_text_dict(top_recipe_chunks)
    
#     vector_query = """SELECT recipe.id as id,recipe.name as name, recipe.description as description, recipe.author_name as author_name, 
#     recipe.recipe_category as recipe_category, recipe.recipe_ingredients as recipe_ingredients, recipe.recipe_instructions as recipe_instructions, recipe.cook_time as cook_time, recipe.prep_time as prep_time, recipe.total_time as total_time,
#     recipe.aggregate_rating as aggregate_rating, recipe.rating_count as rating_count, recipe.calories as calories, recipe.fat_content as fat_content, recipe.saturated_fat_content as saturated_fat_content, recipe.cholesterol_content as cholesterol_content,
#     recipe.sodium_content as sodium_content, recipe.carbohydrate_content as carbohydrate_content, recipe.fiber_content as fiber_content, recipe.sugar_content as sugar_content, recipe.protein_content as protein_content, recipe.recipe_servings as recipe_servings,
#     recipe.recipe_yield as recipe_yield, recipe.images as images, 
#     min(vec_cosine_distance(recipe_chunk.text_vec, :recipe_instructions_vector)) AS distance
# FROM recipe, recipe_chunk
# WHERE recipe.id = recipe_chunk.recipe_id AND recipe.protein_content> :min_protein AND recipe.calories< :max_calories
# GROUP BY recipe.id
# ORDER BY distance asc
# LIMIT :k"""
#     params = params = {
# "min_protein": recipeFilters.min_protein,
# "max_calories": recipeFilters.max_calories,
# "recipe_instructions_vector": str(query_vec),
# "k": 5    
# }
#     result_list = tidb_client.query(sql=vector_query, params=params).to_list()
#     recipe_text_dict = get_recipe_text_dict(result_list)
#     return [Document(page_content=json.dumps(recipe_text_dict[recipe_chunk['id']]), metadata={"distance": recipe_chunk['distance'], "similarity": 1 - recipe_chunk['distance']}) for recipe_chunk in  result_list]