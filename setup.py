from setuptools import setup

setup(
    name='clinical-auth-copilot',
    version='0.2.2',
    py_modules=[],
    install_requires=[],
    extras_require={
        'dev': [],
        'runtime': [
            'fastapi>=0.115',
            'uvicorn>=0.30',
            'sqlmodel>=0.0.22',
            'strawberry-graphql[fastapi]>=0.275',
            'pydantic>=2.7',
            'python-multipart>=0.0.9',
            'boto3>=1.35',
            'openai>=1.40',
            'anthropic>=0.34',
            'pytest>=8.0',
            'httpx>=0.27',
        ],
    },
)
