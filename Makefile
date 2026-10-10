.PHONY: setup verify run

setup:
	@python -c "from pathlib import Path; [Path(p).mkdir(parents=True, exist_ok=True) for p in ['artifacts','evidence','docs','db/migrations','db/seed','src','tests']]"
	@docker compose up -d --wait postgres
	@python scripts/db_setup.py
	@python scripts/create_login_users.py

verify:
	@python scripts/verify.py

run:
	@docker compose up