## Inspiration

I wanted to build a smart, conversational food assistant that goes beyond just returning recipes. Existing recipe search engines often fail to consider nutrition, dietary restrictions, and context from reviews. By combining recipe data with USDA’s nutrition database and adding natural language understanding, we aimed to create a tool that helps users make informed, personalized food choices.

## What it does

Foodie is an AI-powered food assistant that allows users to:

Search millions of recipes from food.com.

Get summarized insights from reviews to understand community feedback.

Retrieve nutritional information from the USDA database.

Ask natural language questions like “What’s a healthy pasta recipe under 500 calories?” and receive context-rich answers.

## How we built it

Data ingestion: Over 5.2 million recipes and reviews from food.com, plus nutrition data from USDA. Imported into TiDB for structured storage.

Embedding pipeline: Recipes and reviews were chunked, then encoded into 1536-dimensional embeddings using OpenAI’s text-embedding-3-small, enabling semantic vector search.

Search stack:

Vector Search Tool (VST) finds semantically relevant recipes.

Query Param Extractor (QPE) identifies filters like calories, ingredients, or cuisine.

Full-text Search (FTS) finds keyword-based food matches.

Reasoning engine: OpenAI’s gpt-4.1-nano LLM runs a ReAct loop, orchestrating between search tools, parsing results, and combining structured + unstructured data.

User interface: Built on Streamlit, providing a clean conversational UI for asking questions and receiving results with recipe + nutrition info.

## Challenges we ran into

Scale: Handling 5.2M+ recipes with embeddings required efficient chunking, batching, and database optimization.

Query complexity: Adding vector search using only the appropriate fields, formatting it and chunking it before embedding, so that semantic meaning are captured. Extracting filters and query text from the user input by leveraging LLMs ability.

Nutrition Info Complexity: Finding the right food item from USDA database using full-text search + LLM and then returning the nutrition information for that food item.

Reasoning orchestration: Designing the LLM prompts and reasoning loop to consistently return accurate, structured answers was non-trivial.

## Accomplishments that we're proud of

Successfully integrated multiple data sources (food.com + USDA) into one unified system.

Built a scalable vector search pipeline capable of handling millions of recipes.

Created a conversational food assistant that feels intuitive and useful, rather than just a recipe search engine.

## What we learned

Embeddings dramatically improve search relevance compared to plain keyword search.

LLMs are powerful for reasoning across heterogeneous data sources, but require careful tool orchestration.

Clean data pipelines and schema design are critical for scalability in real-world food/nutrition applications.

## What's next for Foodie

Personalization: Tailor recommendations based on dietary preferences, allergies, and past user interactions.

Meal planning: Suggest weekly meal plans with balanced nutrition.

Cost awareness: Integrate grocery pricing APIs to show recipe costs and optimize for budget.

Voice assistant integration: Enable hands-free cooking queries.

Mobile app version: Expand beyond Streamlit for on-the-go recipe and nutrition discovery.

## TiDB Cloud Account Email

khanmohammadmaaz@gmail.com
