1. `python -m venv venv`
   Har project me sabse pehle virtual environment banao.

2. Venv activate karo.
   Windows PowerShell: `.\venv\Scripts\Activate.ps1`

3. Runtime dependencies install karo.
   Command: `pip install -r requirements.txt`

4. Dev dependencies alag se install karo.
   Command: `pip install -r requirements-dev.txt`
   Isme generally `ruff`, `mypy`, `pre-commit`, `pytest` hote hain.

5. Professional quality tools ka standard setup:
   - Lint + Format: Ruff
   - Type Checking: mypy
   - Hooks: pre-commit
   - Testing: pytest

6. Ruff ko single source of truth rakho lint + format ke liye.
   - Lint: `ruff check .`
   - Format: `ruff format .`

7. Mypy ko type-checking ke liye `pyproject.toml` me configure karo.
   Run command: `mypy`

8. Pre-commit hooks setup karo.
   Command: `pre-commit install`
   Isse commit ke time code quality checks automatic chal sakte hain.

9. Testing policy project phase ke hisab se define karo.
   - Agar early phase ho to tests manual mode me rakho.
   - Manual run command: `pytest`

10. VS Code setup ko bhi repo me version-control karo.
    - `.vscode/settings.json`: format/lint behavior standardize karta hai.
    - `.vscode/extensions.json`: team ko recommended extensions suggest karta hai.

11. `.gitignore` professional rakho.
    Venv, cache, temp, build artifacts commit nahi hone chahiye.

12. Har project me minimum docs maintain karo:
    - `README.md` (project use/setup)
    - `SETUP.md` (professional setup checklist)
    - `docs/` (internal flow/architecture notes)

13. Git remote verify karo push se pehle.
    Command: `git remote -v`
