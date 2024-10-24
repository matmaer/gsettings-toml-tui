def generate_cicd_stars_chart():
    tools = {
        "conda": "https://github.com/conda/conda",
        "enscons": "https://github.com/dholth/enscons",
        "flit": "https://github.com/pypa/flit",
        "hatch": "https://github.com/pypa/hatch",
        "maturin": "https://github.com/PyO3/maturin",
        "pdm": "https://github.com/pdm-project/pdm",
        "pip": "https://github.com/pypa/pip",
        "pipenv": "https://github.com/pypa/pipenv",
        "pipx": "https://github.com/pypa/pipx",
        "poetry": "https://github.com/python-poetry/poetry",
        "pyenv": "https://github.com/pyenv/pyenv",
        "pyflow": "https://github.com/wonderworks-software/PyFlow",
        "rye": "https://github.com/astral-sh/rye",
        "setuptools": "https://github.com/pypa/setuptools",
        "twine": "https://github.com/pypa/twine",
        "uv": "https://github.com/astral-sh/uv",
        "virtualenv": "https://github.com/pypa/virtualenv",
    }

    star_count_params = []
    for _, url in tools.items():
        short_name = url.replace("https://github.com/", "")
        star_count_params.append(short_name)

    params = "&".join(star_count_params)
    print(f"https://star-history.com/#{params}")
