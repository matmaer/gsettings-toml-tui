def generate_cicd_stars_chart():
    tools = {
        "hatch": "https://github.com/pypa/hatch",
        "pdm": "https://github.com/pdm-project/pdm",
        "poetry": "https://github.com/python-poetry/poetry",
        "pyflow": "https://github.com/wonderworks-software/PyFlow",
        "rye": "https://github.com/astral-sh/rye",
        "uv": "https://github.com/astral-sh/uv",
    }

    star_count_params = []
    for _, url in tools.items():
        short_name = url.replace("https://github.com/", "")
        star_count_params.append(short_name)

    params = "&".join(star_count_params)
    print(f"https://star-history.com/#{params}")
