from venv import logger
import environ
import os


def load_env():
    env = environ.Env()
    # Assuming .env is in the root directory of your Django project
    env_path = os.path.join('/Users/eranlevy/VS projects/Project/TelAviv/TelAviv', '.env')
    print(f'Loading environment variables from: {env_path}')  # Add this line for debugging
    env.read_env(env_path)
    return env