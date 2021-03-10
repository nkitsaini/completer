from complete import Command, Argument, Option


command = Command('nkit', sub_commands=[
	Command('hey',),
	Command('note',),
	Command('send',),
	Command('notes', sub_commands=[
		Command('show_notes'),
		Command('remove'),
		Command('create'), 
	])])

command.run()
