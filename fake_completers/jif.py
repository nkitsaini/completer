from complete import Command, Argument
command = Command("jif", sub_commands=[
	Command("git", sub_commands=[
		Command("fastcommit"),
		Command("mr-start"),
		Command("mr-finish"),
		Command("mr-reply"),
		Command("latest"),
		Command("fetch"),
		Command("remove-all-changes"),
		Command("remove-untracked-changes"),
		Command("stage"),
		Command("unstage"),
		Command("delete-branch"),
		Command("rename-branch"),
		Command("latest"),
		Command("fetch"),
		Command("fetch"),
		])])
command.run()
