from dataclasses import dataclass, field
import typing as t
import os
import enum
from pathlib import Path
import subprocess

Hint = t.Union[str, t.Tuple[str, str]]

class CompleterException(Exception):
	pass

def bash(cmd: str, expect_to_work: bool = True) -> t.Tuple[int, str, str]:
	process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	process.wait()
	if expect_to_work and process.returncode != 0:
		stdout_text = process.stdout.read().decode()
		stderr_text = process.stderr.read().decode()
		error_msg = f"call to command `{cmd}` failed."
		if len(stdout_text) != 0:
			error_msg += f"\nstdout: \n{stdout_text}"
		if len(stderr_text) != 0:
			error_msg += f"\nstderr: \n{stderr_text}"
		raise CompleterException(error_msg)
	return process.returncode, process.stdout.read().decode(), process.stderr.read().decode()

class CommandEntry(t.NamedTuple):
	name: str
	path: Path

def parse_commands_from_directory(directory: Path) -> t.List[CommandEntry]:
	assert directory.is_dir()
	commands: t.List[CommandEntry] = []
	os.environ["_completer_name"] = "true"
	for completion_script in directory.iterdir():
		if not completion_script.is_file():
			continue
		try:
			_, stdout, _ = bash(f'python3 {completion_script.absolute().as_posix()}')
			name = stdout
			commands.append(CommandEntry(name, completion_script.absolute()))
		except CompleterException as e:
			print(f"Error while working with {completion_script}: {e}")
	os.environ.pop("_completer_name")
	return commands

class ShellType(enum.Enum):
	fish = enum.auto()
	bash = enum.auto()

	def render_hints(self, hints: t.List[Hint]) -> str:
		if self == ShellType.fish:
			rs = ""
			for hint in hints:
				if isinstance(hint, str):
					rs += hint + '\n'
				else:
					rs += hint[0] + '\t' + hint[1] + '\n'
			return rs
		elif self == ShellType.bash:
			rs = ""
			for hint in hints:
				if isinstance(hint, str):
					rs += hint + ' '
				else:
					rs += hint[0] + ' '# TODO: check if bash handles hint
			return rs
		raise NotImplementedError

	def get_command(self, command_name: str, completion_file: Path) -> str:
		if self == ShellType.fish:
			shell_command = f"complete -c {command_name} -e" # erase existing
			shell_command += "\n"
			shell_command += f'complete --command {command_name} --no-files --arguments "(env _completer_shell=fish _completer_args=(commandline -cp) python3 {completion_file.absolute().as_posix()})"'
			return shell_command
		elif self == ShellType.bash:
			function_code = f"""function _Complete(){{
				COMPREPLY=( $( env _completer_args="$COMP_LINE" \
							   _completer_shell=bash python3 {completion_file} ) )
				return 0
			}}\n"""
			shell_command = f"complete -o default -F _Complete {command_name}\n"
			return function_code + shell_command


		raise NotImplementedError

	def register_completer(self, completion_dir: Path):
		if self == ShellType.fish:
			commands = parse_commands_from_directory(completion_dir)

			home_dir = Path.home()
			fish_completion_dir = home_dir/'.config/fish/completions/'
			for command_name, script_path in commands:
				completion_text = ""
				completion_text += self.get_command(command_name, script_path)
				completion_text += "\n"
				fish_completion_file = fish_completion_dir/f'{command_name}.fish'
				fish_completion_file.write_text(completion_text)

		elif self == ShellType.bash:
			commands = parse_commands_from_directory(completion_dir)

			home_dir = Path.home()

			# creating dir
			bash_completion_dir = home_dir/'.bash_completions'
			bash_completion_dir.mkdir(exist_ok=True)

			# registering dir
			registering_line = "for f in ~/.bash_completions/*; do source $f; done"
			bash_copletion_file = home_dir/'.bash_completion'
			bash_copletion_file.touch(exist_ok=True)
			line_exists = False
			for line in bash_copletion_file.read_text().splitlines(keepends=False):
				if line == registering_line:
					line_exists = True
			if not line_exists:
				bash_copletion_file.write_text(bash_copletion_file.read_text() + "\n" + registering_line + "\n")

			# adding files
			for command_name, script_path in commands:
				completion_text = ""
				completion_text += self.get_command(command_name, script_path)
				completion_text += "\n"
				bash_completion_file = bash_completion_dir/f'{command_name}.bash'
				bash_completion_file.write_text(completion_text)
		else:
			raise NotImplementedError


def filter_hints(hints: t.List[Hint], arg: str) -> t.List[Hint]:
	rv = []
	for hint in hints:
		if isinstance(hint, tuple):
			hint_name = hint[0]
		else:
			hint_name = hint
		if hint_name.startswith(arg):
			rv.append(hint)
	return rv


def parse(string: str) -> t.List[str]:
	args = string.split(" ")
	return [arg for arg in args if not arg.startswith("-")]


@dataclass
class Argument:
	name: str
	completer: t.Callable[[], t.List[Hint]]


@dataclass
class Option:
	name: str
	completer: t.Callable[[], t.List[Hint]]


@dataclass
class Command:
	name: str
	arguments: t.List[t.Union[Argument, Option]] = field(default_factory=list)
	sub_commands: t.List['Command'] = field(default_factory=list)

	def complete(self, args: t.List[str]) -> t.List[Hint]:
		hints = []
		# if len(args) == 0:
		# 	args.append("")

		if len(args) > 1:
			for command in self.sub_commands:
				if command.name == args[0]:
					hints.extend(command.complete(args[1:]))
					return hints

		possible_commands: t.List[Hint] = [c.name for c in self.sub_commands]
		hints.extend(filter_hints(possible_commands, args[0]))

		position = len(args) - 1
		if position >= len(self.arguments):
			return hints
		completions = self.arguments[position].completer()
		hints.extend(filter_hints(completions, args[-1]))
		return hints


	def complete_str(self, string: str) -> t.List[Hint]:
		args = parse(string)
		return self.complete(args)


	def run(self):
		if "_completer_name" in os.environ:
			print(self.name, end='')
			return
		shell = os.environ["_completer_shell"]
		args = os.environ["_completer_args"]
		assert args.startswith(self.name + " "), args
		args  = args.replace(self.name + " ", "", 1) # removing command name
		hints = self.complete_str(args)
		rendered_text = ShellType[shell].render_hints(hints)
		print(rendered_text, end="")

