import streamlit as st
from pytidb import TiDBClient
from pytidb.embeddings import EmbeddingFunction

tidb_client = TiDBClient.connect(
        host=st.secrets["TIDB_HOST"],
        port=int(st.secrets["TIDB_PORT"]),
        username=st.secrets["TIDB_USERNAME"],
        password=st.secrets["TIDB_PASSWORD"],
        database=st.secrets["TIDB_DATABASE"],
    )

embed_fn = EmbeddingFunction("openai/text-embedding-3-small")
#embed_fn = EmbeddingFunction("amazon.titan-embed-text-v2:0")