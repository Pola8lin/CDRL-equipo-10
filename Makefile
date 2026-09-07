.PHONY: setup verify run

setup:
	@python -c "from pathlib import Path; [Path(p).mkdir(parents=True, exist_ok=True) for p in ['artifacts','evidence','docs','db/migrations','db/seed','src','tests']]"
	@python scripts/db_setup.py

verify:
	@python -m pytest -q

run:
	@docker compose up