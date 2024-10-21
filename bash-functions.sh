#! /bin/bash
create_venvs() {
    envs_to_create=("dev" "tui")
    mkdir -p "$HOME/.venv"
    for env in "${envs_to_create[@]}"; do
        python -m venv "$HOME/.venv/$env"
        chmod u+x "$HOME/.venv/$env/bin/activate"
        # shellcheck source=/dev/null
        # create and activate venv to install textual
        source "$HOME/.venv/$env/bin/activate"
        pip install textual
        if test "$env" = "dev"; then
            # packages for development environment
            pip install ipython
            pip install isort
            pip install pre-commit
            pip install pyinstaller
            pip install pylint
            pip install setuptools
            pip install sh
            pip install shellcheck-py
            pip install textual-dev
            pip install textual[syntax]
            pip install tmuxp
            pip install trufflehog
        fi
        deactivate
    done
}
