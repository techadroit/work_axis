from langchain_core.prompts import PromptTemplate


def format_prompt(prompt, **kwargs):
    return PromptTemplate.from_template(template=prompt).format(**kwargs)
