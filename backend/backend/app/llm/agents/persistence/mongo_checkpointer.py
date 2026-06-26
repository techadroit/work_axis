from langgraph.checkpoint.mongodb import AsyncMongoDBSaver

from backend.app.llm.agents.persistence.database_check_pointer import DatabaseCheckPointer


def create_mongo_checkpointer():
    return DatabaseCheckPointer(checkpointer=AsyncMongoDBSaver())