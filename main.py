from interface import Interface
from formulas import exports as Formulas
from units import exports as Units

all_commands = {}
all_commands.update(Formulas)
all_commands.update(Units)

i = Interface(all_commands)

# i.loop()
i.loop()