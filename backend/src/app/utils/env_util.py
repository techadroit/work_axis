from dotenv import find_dotenv, load_dotenv

def load_environment(path):
    aws_path = find_dotenv(path)
    load_dotenv(aws_path)