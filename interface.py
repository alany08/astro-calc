import difflib
import requests
import json

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
            },
            "nlp": {
                "cb": self.nlp,
                "desc": "Use natural language processing to find the proper command to use",
                "aliases": ["natural_language", "language", "lang"]
            }
        })
        self.cutoff = cutoff

    def nlp(self, args=None):

            if not args or len(args) == 0:
                print("Please use nlp `phrase/query`")
                return

            query = " ".join(args)

            # 1. Configuration for Ollama
            # Default port is 11434. Endpoint for generation is /api/generate
            CONFIG_OLLAMA_URL = "http://localhost:11434/api/generate"
            # CHANGE THIS to the model you have installed (e.g., 'mistral', 'llama2', 'gemma')
            CONFIG_MODEL = "deepseek-v3.1:671b-cloud" 
            # 2. Build the Prompt
            CONFIG_SYS_PROMPT = """
You may ONLY respond in valid json. Please do so without any code formatting or backticks.
Your role will be to select the best function to call, along with the arguments. Pay
close attention to the types of arguments accepted, as shown in the available commands.
Here is the JSON format that you will respond in:
{
    "command": "[command identifier that you selected]",
    "args": ["[array of arguments that may be passed in]"]
}
Here are the available commands and their descriptions, DO NOT USE THE `nlp` OR `help` COMMAND:
[[commands]]
Please process the following query: "[[query]]".
            """
            
            # Get the help string using the function we rewrote earlier
            help_context = self.help(returnstring=True)
            
            CONFIG_SYS_PROMPT = CONFIG_SYS_PROMPT.replace("[[query]]", query)
            CONFIG_SYS_PROMPT = CONFIG_SYS_PROMPT.replace("[[commands]]", help_context if help_context else "No commands found.")

            # 3. Query Ollama
            payload = {
                "model": CONFIG_MODEL,
                "prompt": CONFIG_SYS_PROMPT,
                "stream": False,
                "format": "json"  # Forces Ollama to try and output valid JSON
            }

            try:
                response = requests.post(CONFIG_OLLAMA_URL, json=payload)
                response.raise_for_status()
                
                # Extract the actual text response
                data = response.json()
                actual_response = data.get("response", "")
                
                print("LLM Output:", actual_response)
                print("Running command...")
                
                # Optional: You could parse this here to execute the command immediately
                command_data = json.loads(actual_response)
                # return command_data

                self.commands[command_data["command"]]["cb"](args=command_data["args"])

            except requests.exceptions.ConnectionError:
                print("Error: Could not connect to Ollama.")
                print("Please ensure Ollama is running (default: localhost:11434).")
            except Exception as e:
                print(f"An error occurred: {e}")

    def help(self, args=None, returnstring=False):
        """
        Shows available commands. If an optional search string is provided,
        performs a case-insensitive 'grep' over the help index and prints
        matching lines with 5 lines of context above and below.

        If returnstring is True, returns the output string instead of printing.
        """
        output_lines = []

        # Helper to handle printing or accumulating
        def _log(line):
            output_lines.append(line)
            if not returnstring:
                print(line)

        # Build the help index text
        header = "Available commands:"
        all_help_lines = [header]
        for name, meta in self.commands.items():
            aliases = meta.get("aliases", [])
            alias_str = f" (aliases: {', '.join(aliases)})" if aliases else ""
            all_help_lines.append(f"- {name}: {meta.get('desc', '')}{alias_str}")

        # No args: output the full index
        if not args:
            for line in all_help_lines:
                _log(line)
        else:
            # Use only the first argument if multiple are provided
            query = args[0]
            context = 5

            # Find matching line indices (case-insensitive)
            q_lower = query.lower()
            matched_indices = [i for i, line in enumerate(all_help_lines) if q_lower in line.lower()]

            if not matched_indices:
                _log(f"No matches for: {query!r}")
            else:
                # Build and merge context ranges
                ranges = []
                for idx in matched_indices:
                    start = max(0, idx - context)
                    end = min(len(all_help_lines) - 1, idx + context)
                    ranges.append((start, end))
                ranges.sort()

                merged = []
                for s, e in ranges:
                    if not merged or s > merged[-1][1] + 1:
                        merged.append([s, e])
                    else:
                        merged[-1][1] = max(merged[-1][1], e)

                # Output matched contexts with markers
                _log(f"Help index (grep for '{query}', context +/-{context}):")
                for s, e in merged:
                    # Add a separator if there are gaps between ranges (optional, but good for readability)
                    # if s > 0 and (not merged or s > merged[-1][1] + 1): _log("...") 
                    
                    for i in range(s, e + 1):
                        marker = ">" if i in matched_indices else " "
                        _log(f"{marker} {all_help_lines[i]}")

        if returnstring:
            return "\n".join(output_lines)

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