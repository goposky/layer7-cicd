all: init build clean

init:
	@echo "Install dependencies"
	pip3 install --user -r requirements.txt
build:
	@echo "Compile script to binary"
	python3 -OO /usr/bin/pyinstaller --onefile temp.py
clean:
	@echo "Cleanup"
	rm -rf __pycache__ build temp.spec

