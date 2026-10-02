"""Ground-truth dataset for agent evaluation.

Each case is a small diff plus the findings each agent is expected to report,
identified by a stable `issue_id` (never by free-text title).

An expected item is either an issue_id string, or a dict
{"issue_id": ..., "accept": [alternative ids that also count as a hit]}.
An agent that is expected to report nothing gets an empty list, so clean and
"looks risky but is safe" cases measure hallucination directly.
"""

import textwrap
from typing import Dict, List


def _diff(filename: str, code: str) -> str:
    lines = textwrap.dedent(code).strip("\n").splitlines()
    body = "\n".join(f"+{line}" for line in lines)
    return (
        f"diff --git a/{filename} b/{filename}\n"
        f"--- a/{filename}\n"
        f"+++ b/{filename}\n"
        f"@@ -0,0 +1,{len(lines)} @@\n"
        f"{body}\n"
    )


def _expected(items, category: str, filename: str) -> List[Dict]:
    result = []
    for item in items:
        spec = {"issue_id": item} if isinstance(item, str) else dict(item)
        spec["category"] = category
        spec["file"] = filename
        result.append(spec)
    return result


def _case(case_id, group, description, filename, code, bug=(), security=(), style=()):
    return {
        "id": case_id,
        "group": group,
        "description": description,
        "diff": _diff(filename, code),
        "expected": {
            "bug": _expected(bug, "bug", filename),
            "security": _expected(security, "security", filename),
            "style": _expected(style, "style", filename),
        },
    }


TEST_CASES = [
    # ------------------------------------------------------------------ bugs
    _case("bug_division_by_zero", "bug", "Division by zero", "math_utils.py", """
        def calculate_average(total, count):
            return total / count
    """, bug=["division_by_zero"]),

    _case("bug_null_dereference", "bug", "re.search result used without None check", "parser.py", """
        import re

        def extract_order_id(text):
            match = re.search(r"order-(\\d+)", text)
            return int(match.group(1))
    """, bug=["null_dereference"]),

    _case("bug_missing_key", "bug", "Counter increments key that does not exist", "counter.py", """
        def count_words(words):
            counts = {}
            for word in words:
                counts[word] += 1
            return counts
    """, bug=["missing_key_access"]),

    _case("bug_off_by_one", "bug", "Loop runs one past the end", "totals.py", """
        def sum_items(items):
            total = 0
            for i in range(len(items) + 1):
                total += items[i]
            return total
    """, bug=["off_by_one"]),

    _case("bug_incorrect_logic", "bug", "clamp() has swapped min/max", "limits.py", """
        def clamp(value, low, high):
            return max(high, min(low, value))
    """, bug=["incorrect_logic"]),

    _case("bug_unreachable_code", "bug", "Code after return", "users.py", """
        def save_user(user):
            db.save(user)
            return True
            audit_log.record("user_saved", user.id)
    """, bug=["unreachable_code"]),

    _case("bug_resource_leak", "bug", "File handle never closed", "settings_io.py", """
        def read_config(path):
            f = open(path)
            data = f.read()
            return data
    """, bug=["resource_leak"]),

    _case("bug_type_error", "bug", "str + float concatenation", "pricing.py", """
        def add_tax(price, rate):
            return "Total: " + price * (1 + rate)
    """, bug=["type_error"]),

    _case("bug_clean_safe_division", "negative", "Division guarded against zero", "math_utils.py", """
        def calculate_average(total, count):
            if count == 0:
                return 0.0
            return total / count
    """),

    # -------------------------------------------------------------- security
    _case("sec_sql_injection", "security", "SQL injection via f-string", "database.py", """
        def get_user(username):
            query = f"SELECT * FROM users WHERE username = '{username}'"
            return db.execute(query)
    """, security=["sql_injection"]),

    _case("sec_command_injection", "security", "Shell command built from input", "network.py", """
        import os

        def ping_host(host):
            return os.system("ping -c 1 " + host)
    """, security=["command_injection"]),

    _case("sec_eval", "security", "eval on caller-supplied expression", "calc.py", """
        def calculate(expression):
            return eval(expression)
    """, security=["code_injection"]),

    _case("sec_hardcoded_secret", "security", "Credentials committed in source", "settings.py", """
        DB_PASSWORD = "Pr0d_Sup3rS3cret!2024"
        STRIPE_SECRET_KEY = "sk_test_EXAMPLE_KEY_FOR_TESTING_ONLY"
    """, security=["hardcoded_secret"]),

    _case("sec_path_traversal", "security", "User filename joined to upload dir", "files.py", """
        import os

        UPLOAD_DIR = "/var/app/uploads"

        def read_upload(filename):
            with open(os.path.join(UPLOAD_DIR, filename)) as handle:
                return handle.read()
    """, security=["path_traversal"]),

    _case("sec_xss", "security", "Query param reflected into HTML", "views.py", """
        from flask import request

        def greet():
            name = request.args.get("name", "")
            return f"<h1>Hello, {name}!</h1>"
    """, security=["xss"]),

    _case("sec_insecure_deserialization", "security", "pickle.loads on request body", "sessions.py", """
        import pickle
        from flask import request

        def load_session():
            return pickle.loads(request.data)
    """, security=["insecure_deserialization"]),

    _case("sec_weak_crypto", "security", "MD5 for password hashing", "auth.py", """
        import hashlib

        def hash_password(password):
            return hashlib.md5(password.encode()).hexdigest()
    """, security=["weak_crypto"]),

    _case("sec_clean_parameterized", "negative", "Parameterized query", "database.py", """
        def get_user(username):
            query = "SELECT * FROM users WHERE username = %s"
            return db.execute(query, (username,))
    """),

    # ------------------------------------------- tricky negatives (look risky)
    _case("neg_literal_eval", "tricky_negative", "ast.literal_eval is safe", "parsing.py", """
        import ast

        def parse_literal(text):
            return ast.literal_eval(text)
    """),

    _case("neg_subprocess_list", "tricky_negative", "subprocess with list args, no shell", "shell_utils.py", """
        import subprocess

        def list_directory(path):
            result = subprocess.run(["ls", "-l", path], capture_output=True, text=True, check=True)
            return result.stdout
    """),

    _case("neg_random_choice", "tricky_negative", "random.choice for a non-security purpose", "tips.py", """
        import random

        def pick_daily_tip(tips):
            if not tips:
                return None
            return random.choice(tips)
    """),

    # ----------------------------------------------------------------- style
    _case("style_deep_nesting", "style", "Three nested conditionals", "validator.py", """
        def is_valid_order(quantity, price, stock):
            if quantity > 0:
                if price > 0:
                    if stock >= quantity:
                        return True
            return False
    """, style=["deep_nesting"]),

    _case("style_magic_number", "style", "Unexplained thresholds", "pricing.py", """
        def apply_discount(order_total):
            if order_total > 4750:
                return order_total * 0.87
            return order_total
    """, style=["magic_number"]),

    _case("style_code_duplication", "style", "Same formatting block copied three times", "names.py", """
        def format_user(user):
            return user["first_name"].strip().title() + " " + user["last_name"].strip().title()

        def format_author(author):
            return author["first_name"].strip().title() + " " + author["last_name"].strip().title()

        def format_editor(editor):
            return editor["first_name"].strip().title() + " " + editor["last_name"].strip().title()
    """, style=["code_duplication"]),

    _case("style_poor_naming", "style", "Single-letter names", "calc.py", """
        def f(a, b):
            t = 0
            for x in a:
                t += x * b
            return t
    """, style=["poor_naming"]),

    _case("style_clean", "negative", "Named constant, small clear function", "retry.py", """
        MAX_RETRIES = 3

        def should_retry(attempt):
            \"\"\"Return True while retry attempts remain.\"\"\"
            return attempt < MAX_RETRIES
    """),

    # --------------------------------------------------------- clean / multi
    _case("clean_helpers", "negative", "Typed, documented helper", "helpers.py", """
        def add(a: int, b: int) -> int:
            \"\"\"Add two numbers.\"\"\"
            return a + b
    """),

    # Original "multiple issues" case, with the hint comments removed so the
    # diff no longer tells the agents which category each line belongs to.
    _case("multi_issue", "multi", "One bug, one vulnerability, one style issue", "api.py", """
        def process_request(user_input):
            result = eval(user_input)

            data = fetch_data()
            value = data['key']

            if value > 42:
                return result
            return None
    """,
        bug=[{"issue_id": "missing_key_access", "accept": ["missing_error_handling"]}],
        security=["code_injection"],
        style=["magic_number"]),
]