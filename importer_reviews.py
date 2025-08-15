from tidb import tidb_client
from pytidb.schema import TableModel, Field, FullTextField
import datetime
import pandas as pd
import numpy as np

class Review(TableModel):
            id: int | None = Field(default=None, primary_key=True)
            recipe_id: int = Field()
            author_id: int = Field()
            author_name: str = Field()
            rating: str = Field(nullable=True)
            review: str = FullTextField(fts_parser="MULTILINGUAL")
            #review_vec: list[float] = embed_fn.VectorField(
            #    source_field="review",
            #    description="Embedding for review"
            #)
            date_submitted: datetime.datetime = Field(
                default_factory=lambda: datetime.datetime.now(datetime.UTC)
            )
            date_modified: datetime.datetime = Field(
                default_factory=lambda: datetime.datetime.now(datetime.UTC)
            )

# Load your CSV file
df = pd.read_csv("documents/reviews.csv")  # change this to your actual file path

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
review_table = tidb_client.create_table(schema=Review, if_exists="skip")

chunk_size = 100
#last_id = 1140900
last_id = tidb_client.query(sql="select max(id) as last_id from review").to_list()[0]['last_id']
print(last_id)
n=0
for chunk in pd.read_csv("documents/reviews.csv", chunksize=chunk_size):
    review_list = []
    chunk = chunk.replace({np.nan: None})
    for _, row in chunk.iterrows():
        review = Review()
        review.id = row['ReviewId']
        review.recipe_id = row['RecipeId']
        review.author_id = row['AuthorId']
        review.author_name = row['AuthorName']
        review.rating = row['Rating']
        review.review = row['Review']
        review.date_submitted = row['DateSubmitted']
        review.date_modified = row['DateModified']
        if(review.id > last_id):
            review_list.append(review)
    if(len(review_list))>0:
        n += 1
        print (f"Inserting records into TiDB for the {n} time...");
        review_table.bulk_insert(review_list)
