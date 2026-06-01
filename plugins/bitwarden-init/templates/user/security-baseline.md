## Write Secure Code by Default

**Security is not a feature. It's a baseline.**

- Sanitize all external input: user data, API responses, file contents, environment variables.
- Never hardcode secrets or credentials — even in examples.
- Use parameterized queries — never concatenate user input into SQL or shell commands.
- When in doubt about a security implication, raise it.
- All code must withstand a detailed security review.
