with open("agent/prompts.py", "r") as f:
    content = f.read()

# find where VALIDATOR_PROMPT is defined
import re
# Remove the second definition
content = re.sub(r'VALIDATOR_PROMPT = """\n(.*?)\n"""\.strip\(\)\n\nVALIDATOR_PROMPT = """\n\1\n"""\.strip\(\)', r'VALIDATOR_PROMPT = """\n\1\n""".strip()', content, flags=re.DOTALL)

with open("agent/prompts.py", "w") as f:
    f.write(content)
