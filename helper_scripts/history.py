from pytidb.schema import TableModel, Field
from tidb import tidb_client
from typing import List
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage, messages_from_dict, messages_to_dict
import datetime

class DBChatMessageHistory(BaseChatMessageHistory):
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.client = tidb_client

        class ChatHistory(TableModel):
            id: int | None = Field(default=None, primary_key=True)
            session_id: str = Field()
            message_type: str = Field()
            message_json: str = Field()
            created_at: datetime.datetime = Field(
                        default_factory=lambda: datetime.datetime.now(datetime.UTC)
                    )
        self.ChatHistory = ChatHistory
        self.table = tidb_client.create_table(schema=ChatHistory, if_exists="skip")

    def add_message(self, message: BaseMessage) -> None:
        msg_type = message.type
        msg_json = messages_to_dict([message])[0]
        record = self.ChatHistory(
            session_id=self.session_id,
            message_type=msg_type,
            message_json=str(msg_json),
            created_at=datetime.datetime.now(datetime.UTC)
        )
        self.table.insert(record)

    def get_messages(self) -> List[BaseMessage]:
        results = self.table.query(filters={"session_id": self.session_id}, order_by={"created_at": "desc"})
        return results.to_list().map(lambda x: messages_from_dict([x.message_json])[0])

    def clear(self) -> None:
        self.client.delete(self.table, filters={"session_id": self.session_id})
