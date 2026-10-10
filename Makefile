.PHONY: setup verify run

setup:
	@python -c "from pathlib import Path; [Path(p).mkdir(parents=True, exist_ok=True) for p in ['artifacts','evidence','docs','db/migrations','db/seed','src','tests']]"
	@docker compose up -d --wait postgres
	@python scripts/db_setup.py

verify: setup
	@python -m pytest -v --junitxml=artifacts/pytest-results.xml

run:
	@docker compose up