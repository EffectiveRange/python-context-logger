# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/EffectiveRange/python-context-logger/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                            |    Stmts |     Miss |   Branch |   BrPart |   Cover |   Missing |
|-------------------------------- | -------: | -------: | -------: | -------: | ------: | --------: |
| context\_logger/\_\_init\_\_.py |        2 |        0 |        0 |        0 |    100% |           |
| context\_logger/filter.py       |       23 |        0 |        4 |        0 |    100% |           |
| context\_logger/logger.py       |       92 |        8 |       14 |        0 |     92% |90-91, 105-106, 129-130, 142-143 |
| tests/loggerTest.py             |       86 |        0 |        8 |        4 |     96% |26->exit, 43->exit, 70->exit, 106->exit |
|                       **TOTAL** |  **203** |    **8** |   **26** |    **4** | **95%** |           |


## Setup coverage badge

Below are examples of the badges you can use in your main branch `README` file.

### Direct image

[![Coverage badge](https://raw.githubusercontent.com/EffectiveRange/python-context-logger/python-coverage-comment-action-data/badge.svg)](https://htmlpreview.github.io/?https://github.com/EffectiveRange/python-context-logger/blob/python-coverage-comment-action-data/htmlcov/index.html)

This is the one to use if your repository is private or if you don't want to customize anything.

### [Shields.io](https://shields.io) Json Endpoint

[![Coverage badge](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/EffectiveRange/python-context-logger/python-coverage-comment-action-data/endpoint.json)](https://htmlpreview.github.io/?https://github.com/EffectiveRange/python-context-logger/blob/python-coverage-comment-action-data/htmlcov/index.html)

Using this one will allow you to [customize](https://shields.io/endpoint) the look of your badge.
It won't work with private repositories. It won't be refreshed more than once per five minutes.

### [Shields.io](https://shields.io) Dynamic Badge

[![Coverage badge](https://img.shields.io/badge/dynamic/json?color=brightgreen&label=coverage&query=%24.message&url=https%3A%2F%2Fraw.githubusercontent.com%2FEffectiveRange%2Fpython-context-logger%2Fpython-coverage-comment-action-data%2Fendpoint.json)](https://htmlpreview.github.io/?https://github.com/EffectiveRange/python-context-logger/blob/python-coverage-comment-action-data/htmlcov/index.html)

This one will always be the same color. It won't work for private repos. I'm not even sure why we included it.

## What is that?

This branch is part of the
[python-coverage-comment-action](https://github.com/marketplace/actions/python-coverage-comment)
GitHub Action. All the files in this branch are automatically generated and may be
overwritten at any moment.