install-hooks:
	pip3 install pre-commit==2.9.2
	pre-commit install -t pre-commit -t commit-msg
