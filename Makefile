
all: check

.PHONY: check
check:
	mypy --strict util.py
	mypy --strict cache.py
	mypy --strict database.py
	mypy --strict history.py
	mypy --strict crawler.py
	mypy --strict problem.py
	mypy --strict stats.py
	mypy --strict pick.py
	mypy --strict start.py
	mypy --strict done.py
	mypy --strict app.py

.PHONY: test
test:
	uvicorn app:app --reload --host 0.0.0.0 --port 8080 --lifespan auto --no-server-header --no-date-header

