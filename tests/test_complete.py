from complete import Command, Argument, Option


def test_argument_completion():
	completer = Command("ROOT", sub_commands=[
		Command("first", [
			Argument("arg1", lambda: ["one", "two", "onsite"])
		])
	])
	assert ["one", "onsite"] == completer.complete_str("first on")


def test_command_completion():
	completer = Command("ROOT", sub_commands=[
		Command("first", [ Argument("arg1", lambda: ["one", "two", "onsite"]) ]),
		Command("second", [ Argument("arg1", lambda: ["one", "two", "onsite"]) ]),
		Command("seventh", [ Argument("arg1", lambda: ["one", "two", "onsite"]) ])
	])
	assert ["second", "seventh"] == completer.complete_str("se")

def test_nested_completion():
	completer = Command("ROOT", sub_commands=[
		Command(
			"first",
			[Argument("arg1", lambda: ["one", "two", "onsite"])] ,
			[Command("com1", [
				Argument("arg2", lambda: [("one", "help"), "two", "onsite"]),
			])],
		),
		Command("second", [ Argument("arg1", lambda: ["one", "two", "onsite"]) ]),
		Command("seventh", [ Argument("arg1", lambda: ["one", "two", "onsite"]) ])
	])
	assert ["com1"] == completer.complete_str("first com1")
	assert [("one", "help"), "two", "onsite"] == completer.complete_str("first com1 ")
	assert [("one", "help"), "onsite"] == completer.complete_str("first com1 o")

