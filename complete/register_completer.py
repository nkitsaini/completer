import sys
from pathlib import Path
from .completer import ShellType

def main():
	if len(sys.argv) != 3:
		print("usage: register_completer shell_name path/to/directory/with/scripts")
		exit(1)
	shell = sys.argv[1]
	directory = Path(sys.argv[2])
	ShellType[shell].register_completer(directory)
	print("registered")

if __name__ == "__main__":
	main()
