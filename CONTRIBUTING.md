# Contributing to Helpr

Thank you for your interest in contributing to Helpr! This document provides guidelines for contributing to the project.

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for all contributors.

## How to Contribute

### Reporting Bugs

If you find a bug, please create an issue on GitHub with:
- A clear, descriptive title
- Steps to reproduce the issue
- Expected behavior
- Actual behavior
- Your environment (OS, Python version, etc.)
- Any relevant logs or screenshots

### Suggesting Features

Feature requests are welcome! Please create an issue with:
- A clear description of the feature
- The problem it solves
- Any alternative solutions you've considered
- Examples of how it would be used

### Pull Requests

1. **Fork the repository** and create your branch from `main`
2. **Make your changes** following the code style guidelines
3. **Test your changes** thoroughly
4. **Update documentation** if needed
5. **Commit your changes** with clear, descriptive commit messages
6. **Push to your fork** and submit a pull request

#### Pull Request Guidelines

- Keep PRs focused on a single feature or fix
- Include a clear description of what the PR does
- Reference any related issues
- Ensure all tests pass (if applicable)
- Update README.md if you change functionality

## Development Setup

1. Clone your fork:
   ```bash
   git clone https://github.com/YOUR-USERNAME/helpr.git
   cd helpr
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Copy the environment template:
   ```bash
   cp env.template .env
   ```

5. Configure your `.env` file with your Plex credentials

6. Run the application:
   ```bash
   python run.py
   ```

## Code Style

- Follow PEP 8 guidelines for Python code
- Use meaningful variable and function names
- Add comments for complex logic
- Keep functions focused and concise
- Use type hints where appropriate

## Testing

Before submitting a PR:
- Test all modified functionality manually
- Verify the invite form works
- Verify the admin dashboard loads correctly
- Check that library configuration is saved properly
- Test with both SQLite and PostgreSQL (if possible)

## Security

- Never commit sensitive information (tokens, passwords, etc.)
- Use environment variables for all secrets
- Follow security best practices
- Report security vulnerabilities privately (see SECURITY.md)

## License

By contributing to Helpr, you agree that your contributions will be licensed under the GPL-3.0 License.

## Questions?

Feel free to open an issue for any questions about contributing!
