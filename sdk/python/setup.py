from setuptools import setup, find_packages

setup(
    name="agentloop-sdk",
    version="2.0.0",
    description="AgentLoop SDK - Closed-loop outcome intelligence for AI agents",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="AgentLoop",
    url="https://github.com/agentloop/agentloop-sdk",
    packages=find_packages(),
    install_requires=[
        "httpx>=0.27.0",
        "pydantic>=2.0.0",
    ],
    python_requires=">=3.9",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)

# history: feat: add Python SDK package structure and setup