all: init build clean

init:
	@echo "Install dependencies"
	pip3 install --user -r requirements.txt
build:
	@echo "Compile script to binary"
	python3 -OO /usr/bin/pyinstaller --onefile gmuz.py
clean:
	@echo "Cleanup"
	rm -rf __pycache__ build gmuz.spec

