# Python Helper Tools

Custom Python helper tools created during conversations to avoid repetitive code.

## Purpose

When you find yourself writing the same code repeatedly (e.g., reading IL files, parsing data), you can create a reusable helper tool instead.

## Creating Helpers

Use the `create_python_helper()` function from `python_tool_creator.py`:

```python
create_python_helper(
    tool_name="read_il_file_content",
    description="Read IL file and return its content as a string",
    function_body='''
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()
return content
''',
    parameters='{"file_path": "str"}',
    return_type="str"
)
```

## Usage

After creation, helpers are immediately available and persist across sessions.

## Best Practices

- ✅ File I/O operations
- ✅ Data transformation
- ✅ Simple calculations
- ✅ String manipulation
- ❌ Complex business logic (use regular tools instead)
- ❌ SKILL execution (use skill_tools instead)

