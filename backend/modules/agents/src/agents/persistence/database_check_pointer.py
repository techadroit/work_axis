from llm_module.checkpoointer.sqlite_checkpointer import AppSqliteCheckpointer


class DatabaseCheckPointer:
    def __init__(self, checkpointer):
        self.checkpointer = checkpointer

    def get_checkpoint(self):
        return self.checkpointer

_sql_checkpointer = AppSqliteCheckpointer()


def provide_checkpointer():
    checkpointer = _sql_checkpointer.create_checkpoint()
    return checkpointer
