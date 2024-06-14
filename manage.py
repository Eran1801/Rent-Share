#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import environ


def main():
    """Run administrative tasks."""
    # call env vars
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TelAviv.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)
    
def load_env():
    env = environ.Env()
    # Define the path to the .env file
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'TelAviv', '.env')
    env.read_env(env_path)
    
    return env

if __name__ == '__main__':
    main()
