with open('agent/core.py', 'r') as f:
    lines = f.readlines()

# Fix each problematic line with correct indentation
# These lines are inside while loop > elif > if action > else block
# Correct indentation is 16 spaces (4 levels of 4 spaces each)

fixes = {
    347: '                    observation = f"Tool {action} unavailable: {error}. {degradation_note}"\n',
    349: '                    conversation += f"\\n\\nASSISTANT: {response}\\n\\nOBSERVATION: {observation}\\n\\nContinue:"\n',
    350: '            else:\n',
    351: '                thought = parsed.get("thought", response)\n',
    352: '                self.logger.log_thought(thought)\n',
    353: '                conversation += f"\\n\\nASSISTANT: {response}\\n\\nContinue:"\n',
    354: '        # Calculate tool efficiency for episodic memory\n',
    355: '        self.tool_results = tool_results\n',
}

for line_num, new_content in fixes.items():
    lines[line_num - 1] = new_content
    print(f"Fixed line {line_num}")

with open('agent/core.py', 'w') as f:
    f.writelines(lines)

print("File saved successfully")
