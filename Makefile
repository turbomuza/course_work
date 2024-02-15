.PHONY: all build run

all: build

config:
	@echo "skam configs"
	python3 rb.py $(urls)

build: config
	@echo "create binary files"
	pyinstaller --onefile --name run_script --distpath . main.py

run: build
	@echo "runnely script...."
	./run_script