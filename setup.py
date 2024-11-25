from setuptools import setup, find_packages

setup(
    name="unicef-api",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'flask==3.0.0',
        'flask-sqlalchemy==3.1.1',
        'flask-migrate==4.0.5',
        'flask-login==0.6.3',
        'langchain==0.3.7',
        'langchain-google-genai==0.0.3',
        'python-dotenv==1.0.0',
        'requests==2.31.0',
        'pydantic==2.5.2',
        'flask-limiter==3.5.0',
        'bcrypt==4.0.1',
        'pytest==8.0.0',
        'pytest-asyncio==0.23.5',
    ],
) 