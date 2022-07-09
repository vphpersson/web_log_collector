from setuptools import setup, find_packages

setup(
    name='web_log_collector',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'fastapi',
        'starlette',
        'python-jose',
        'uvicorn',
        'typed_argument_parser @ git+https://github.com/vphpersson/typed_argument_parser.git#egg=typed_argument_parser',
        'ecs_py @ git+https://github.com/vphpersson/ecs_py.git#egg=ecs_py',
        'ecs_tools_py @ git+https://github.com/vphpersson/ecs_tools_py.git#egg=ecs_tools_py'
    ]
)
