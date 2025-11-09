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
                "desc": "Shows available commands (help `word` to search index, > marks result)",
                "aliases": ["?", "h"]
            }
        })
        self.cutoff = cutoff

    def help(self, args=None):
        """
        Shows available commands. If an optional search string is provided,
        performs a case-insensitive 'grep' over the help index and prints
        matching lines with 5 lines of context above and below.
        """
        # Build the help index text
        header = "Available commands:"
        lines = [header]
        for name, meta in self.commands.items():
            aliases = meta.get("aliases", [])
            alias_str = f" (aliases: {', '.join(aliases)})" if aliases else ""
            lines.append(f"- {name}: {meta.get('desc', '')}{alias_str}")

        # No args: print the full index
        if not args:
            for line in lines:
                print(line)
            return

        # Use only the first argument if multiple are provided
        query = args[0]
        context = 5

        # Find matching line indices (case-insensitive)
        q_lower = query.lower()
        matched_indices = [i for i, line in enumerate(lines) if q_lower in line.lower()]

        if not matched_indices:
            print(f"No matches for: {query!r}")
            return

        # Build and merge context ranges
        ranges = []
        for idx in matched_indices:
            start = max(0, idx - context)
            end = min(len(lines) - 1, idx + context)
            ranges.append((start, end))
        ranges.sort()

        merged = []
        for s, e in ranges:
            if not merged or s > merged[-1][1] + 1:
                merged.append([s, e])
            else:
                merged[-1][1] = max(merged[-1][1], e)

        # Print matched contexts with markers
        print(f"Help index (grep for '{query}', context +/-{context}):")
        for s, e in merged:
            for i in range(s, e + 1):
                marker = ">" if i in matched_indices else " "
                print(f"{marker} {lines[i]}")

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
                    print(f"Unknown command '{raw_cmd}'. Using closest match '{best_key}'")
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