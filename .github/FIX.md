# Fix Instructions
Fix these:
1. app/handlers/callbacks.py line 7-9: Add import
2. app/handlers/callbacks.py lines 264,266,273: Break long lines
3. app/ui/formatters.py: Add type hints
4. Run: isort app/ --profile black
5. Run: black app/ --line-length 120
