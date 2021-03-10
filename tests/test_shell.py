from complete import Command, Argument, Option
import os

def test_fish(monkeypatch, capsys):
	root_command = Command('root', [Argument('hii', lambda: [("one", "does one thing"), "two"])])
	monkeypatch.setenv('_completer_shell', 'fish')
	monkeypatch.setenv('_completer_args', 'root ')
	root_command.run()
	captured = capsys.readouterr()
	assert captured.out == """one\tdoes one thing\ntwo\n"""
	
