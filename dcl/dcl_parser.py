import os
import re

class DCLParsedCommand:
    def __init__(self, raw_line):
        self.raw_line = raw_line.strip()
        self.is_comment = False
        self.label = None
        self.is_assignment = False
        self.assign_var = None
        self.assign_val = None
        self.verb = None
        self.args = []
        self.qualifiers = {}
        self.parse()

    def parse(self):
        line = self.raw_line
        if not line:
            self.is_comment = True
            return

        # Strip leading '$'
        if line.startswith('$'):
            line = line[1:].strip()
            
        if not line or line.startswith('!'):
            self.is_comment = True
            return

        # Check for label at start of line: LABEL:
        label_match = re.match(r'^([A-Za-z0-9_$%]+):\s*(.*)$', line)
        if label_match:
            self.label = label_match.group(1).upper()
            line = label_match.group(2).strip()
            if not line or line.startswith('!'):
                return

        # Check for symbol assignment:
        # e.g., X = "HELLO" or X = 100 or X := HELLO
        assign_match = re.match(r'^([A-Za-z0-9_$]+)\s*(:=|=)\s*(.*)$', line)
        if assign_match:
            self.is_assignment = True
            self.assign_var = assign_match.group(1).upper()
            self.assign_val = assign_match.group(3).strip()
            if (self.assign_val.startswith('"') and self.assign_val.endswith('"')) or \
               (self.assign_val.startswith("'") and self.assign_val.endswith("'")):
                self.assign_val = self.assign_val[1:-1]
            return

        # Tokenize by whitespace, preserving quotes
        raw_tokens = []
        cur_token = []
        in_quotes = False
        quote_char = None
        
        for ch in line:
            if ch == '"':
                if not in_quotes:
                    in_quotes = True
                else:
                    in_quotes = False
                cur_token.append(ch)
            elif ch.isspace() and not in_quotes:
                if cur_token:
                    raw_tokens.append("".join(cur_token))
                    cur_token = []
            else:
                cur_token.append(ch)
                
        if cur_token:
            raw_tokens.append("".join(cur_token))

        if not raw_tokens:
            self.is_comment = True
            return

        # Expand attached qualifiers on tokens (e.g. "PRINT/QUEUE=LP0:" -> ["PRINT", "/QUEUE=LP0:"]
        # or "SALES.RPT/DELETE" -> ["SALES.RPT", "/DELETE"])
        KNOWN_SWITCHES = {'DELETE', 'ALL', 'FULL', 'CONFIRM', 'NOWAIT', 'VERIFY', 'NOVERIFY', 'ENTRY', 'QUEUE', 'START', 'STOP', 'PAGE', 'FEED'}

        def split_token_qualifiers(tok, is_verb=False):
            quals = []
            curr = tok
            while True:
                m = re.search(r'/([A-Za-z_][A-Za-z0-9_$]*)(?:([=:])([^/]*))?$', curr)
                if not m:
                    break
                q_full = m.group(0)
                q_name = m.group(1).upper()
                sep = m.group(2)
                prefix = curr[:m.start()]
                if not prefix:
                    quals.insert(0, curr)
                    curr = ''
                    break
                is_qual = False
                if sep is not None:
                    is_qual = True
                elif q_name in KNOWN_SWITCHES:
                    is_qual = True
                elif is_verb and prefix.isalpha():
                    is_qual = True
                elif re.search(r'\.[A-Za-z0-9]+$', prefix):
                    is_qual = True

                if is_qual:
                    quals.insert(0, q_full)
                    curr = prefix
                else:
                    break
            return curr, quals

        expanded_tokens = []
        for idx, tok in enumerate(raw_tokens):
            base, quals = split_token_qualifiers(tok, is_verb=(idx == 0))
            if base:
                expanded_tokens.append(base)
            expanded_tokens.extend(quals)

        QUAL_REGEX = re.compile(r'^/([A-Za-z_][A-Za-z0-9_$]*)(?:([=:])(.*))?$')

        def is_qualifier(tok):
            m = QUAL_REGEX.match(tok)
            if not m:
                return False
            q_name = m.group(1).upper()
            sep = m.group(2)
            if sep is not None:
                return True
            if q_name in KNOWN_SWITCHES:
                return True
            if m.group(1).isupper() and not os.path.exists(tok):
                return True
            return False

        # First token is the verb (unless it is a qualifier)
        first_t = expanded_tokens[0]
        if is_qualifier(first_t):
            self.verb = ""
        else:
            self.verb = first_t.upper()
            expanded_tokens = expanded_tokens[1:]

        for tok in expanded_tokens:
            if is_qualifier(tok):
                m = QUAL_REGEX.match(tok)
                q_name = m.group(1).upper()
                sep = m.group(2)
                q_val_raw = m.group(3)
                q_val = True
                if sep is not None:
                    q_val = q_val_raw
                    if isinstance(q_val, str) and q_val.startswith('"') and q_val.endswith('"'):
                        q_val = q_val[1:-1]
                self.qualifiers[q_name] = q_val
            else:
                clean_arg = tok
                if clean_arg.startswith('"') and clean_arg.endswith('"'):
                    clean_arg = clean_arg[1:-1]
                self.args.append(clean_arg)
