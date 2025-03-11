from setuptools import setup, find_packages
from pathlib import Path

base_path = Path(__file__).parent
long_description = (base_path / "README.md").read_text()

setup(
    name='claudeshell',
    version='0.1.0',
    author='soheil shabani',
    author_email='soheilshabani.79.ss@gmail.com',
    license="MIT",
    description='A command-line interface for Claude AI',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/soheilsh7/claude-cli',
    project_urls={
        "Bug Tracker": "https://github.com/soheilsh7/claude-cli/issues",
        "Documentation": "https://github.com/soheilsh7/claude-cli",
        "Source Code": "https://github.com/soheilsh7/claude-cli",
    },
    packages=find_packages(include=['claude_cli', 'claude_cli.*']),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Operating System :: OS Independent',
        'Environment :: Console',
        'Topic :: Utilities',
    ],
    keywords=['claude', 'ai', 'cli', 'chatbot', 'anthropic', 'command-line'],
    install_requires=[
        'claude-api>=1.0.17',
        'click>=8.0.0',
        'rich>=12.0.0',
        'pyyaml>=6.0',
    ],
    python_requires=">=3.7",
    entry_points={
        'console_scripts': [
            'claude=claude_cli.cli:main',
        ],
    },
)