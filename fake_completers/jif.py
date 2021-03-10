from complete import Command, Argument
command = Command("jif", sub_commands=[
	Command("git", sub_commands=[
		Command("latest"),
		Command("fetch"),
		Command("remove-all-changes")])])
command.run()
