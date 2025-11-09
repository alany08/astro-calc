import difflib

class Interface:
    def __init__(self, commands={}, cutoff=0.6):
        """example commands
        {
            "name": {
                "cb": callback,
                "desc": description,
                "aliases": ["name1"]
            }
        }
        """

        self.commands = commands
        self.commands.update({
            "help": {
                "cb": self.help,
                "desc": "Shows available commands",
                "aliases": ["?", "h"]
            }
        })
        self.cutoff = cutoff

    def help(self, args=None):
        print("Available commands:")
        for name, meta in self.commands.items():
            aliases = meta.get("aliases", [])
            alias_str = f" (aliases: {', '.join(aliases)})" if aliases else ""
            print(f"- {name}: {meta.get('desc', '')}{alias_str}")

    def _build_index(self):
        # Map both names and aliases (case-insensitive) to the canonical command name
        index = {}
        for name, meta in self.commands.items():
            index[name.lower()] = name
            for alias in meta.get("aliases", []):
                index[alias.lower()] = name
        return index

    def loop(self):
        while True:
            i = input(">>> Command: ").strip()
            if not i:
                continue

            parts = i.split()
            raw_cmd = parts[0]
            args = parts[1:]

            # Build an index for names and aliases
            index = self._build_index()

            # Direct case-insensitive match
            canonical = index.get(raw_cmd.lower())
            if canonical is None:
                # Fuzzy match against all known names/aliases
                keys = list(index.keys())
                matches = difflib.get_close_matches(raw_cmd.lower(), keys, n=3, cutoff=self.cutoff)
                if matches:
                    # Take the best match
                    best_key = matches[0]
                    canonical = index[best_key]
                    print(f"Unknown command '{raw_cmd}'. Using closest match '{canonical}'")
                else:
                    print(f"Unknown command '{raw_cmd}'. Type 'help' to see available commands.")
                    continue

            meta = self.commands[canonical]
            print("-"*30)
            print("Command:", canonical)
            print("Description:", meta.get("desc", ""))
            print("Arguments:", str(args))
            print("-"*30)
            meta["cb"](args)