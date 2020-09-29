SRC = xjdp/
VENV ?= venv

$(VENV): requirements.txt
	@python -m venv $@ --prompt $@::xjdp
	@source $@/bin/activate && pip --disable-pip-version-check install -r $<
	@echo "Enter virtual environment: source venv/bin/activate"

.PHONY: install
install: requirements.txt $(SRC)
	@pip install --user --require-hashes -r $<
	@pip install --user --no-deps .

.PHONY: install_dev
install_dev: venv
	@source $(VENV)/bin/activate && pip install -e .[dev]

tags: $(SRC)
	@ctags --languages=python --python-kinds=-i -R $(SRC)

.PHONY: outdated
outdated:
	@source $(VENV)/bin/activate && pip list --outdated

.PHONY: lint
lint:
	@pylint -f colorized $(SRC)

.PHONY: typecheck
typecheck:
	@mypy $(SRC)
