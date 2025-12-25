# Security Policy

## Supported Versions

We release patches for security vulnerabilities in the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

We take the security of the Siglent Oscilloscope Control package seriously. If you believe you have found a security vulnerability, please report it to us as described below.

### Please Do Not

- **Do not** open a public GitHub issue for security vulnerabilities
- **Do not** discuss the vulnerability publicly until it has been addressed

### Please Do

1. **Report via GitHub Security Advisory**
   - Go to the repository's Security tab
   - Click "Report a vulnerability"
   - Provide detailed information about the vulnerability

2. **Include in Your Report**
   - Type of vulnerability
   - Full paths of source file(s) related to the vulnerability
   - Location of the affected source code (tag/branch/commit or direct URL)
   - Step-by-step instructions to reproduce the issue
   - Proof-of-concept or exploit code (if possible)
   - Impact of the issue, including how an attacker might exploit it

### What to Expect

- **Acknowledgment**: We will acknowledge receipt of your vulnerability report within 48 hours
- **Communication**: We will keep you informed about the progress of addressing the vulnerability
- **Timeline**: We aim to address critical vulnerabilities within 7 days
- **Credit**: We will credit you in the security advisory (unless you prefer to remain anonymous)

## Security Considerations

### Network Security

This package communicates with oscilloscopes over TCP/IP networks. Please consider:

- **Network Isolation**: Ensure oscilloscopes are on isolated or trusted networks
- **Authentication**: The SCPI protocol does not provide authentication - rely on network security
- **Encryption**: SCPI communication is unencrypted - avoid transmitting over untrusted networks
- **Firewall Rules**: Configure firewalls to restrict access to oscilloscope ports (typically 5024)

### Input Validation

The package performs input validation, but users should:

- Validate IP addresses before connecting
- Sanitize user inputs when building SCPI commands
- Handle connection errors appropriately
- Avoid exposing oscilloscope control to untrusted networks

### Dependency Security

We regularly monitor our dependencies for security vulnerabilities:

- PyQt6
- NumPy
- Matplotlib

Run `pip list --outdated` regularly to check for dependency updates.

### Best Practices

When using this package:

1. **Keep Updated**: Always use the latest version of the package
2. **Virtual Environments**: Use virtual environments to isolate dependencies
3. **Network Security**: Ensure oscilloscopes are on secure, isolated networks
4. **Access Control**: Limit who can execute oscilloscope control scripts
5. **Code Review**: Review any custom SCPI commands before execution
6. **Logging**: Enable logging to monitor oscilloscope communications

### Known Limitations

- No built-in authentication mechanism (relies on network security)
- SCPI commands are sent as plain text
- No rate limiting on commands
- Connection timeout defaults may need adjustment for slow networks

## Security Updates

Security updates will be released as soon as possible after a vulnerability is confirmed. Updates will be announced via:

- GitHub Security Advisories
- Release notes in CHANGELOG.md
- Git tags for version releases

## Scope

This security policy applies to:

- The `siglent` Python package
- All modules under `siglent/`
- Example scripts in `examples/`
- Documentation and guides

## Questions

If you have questions about this security policy, please open a GitHub issue with the "question" label (for non-sensitive questions) or contact via the Security Advisory system for sensitive matters.

## Additional Resources

- [OWASP Top Ten](https://owasp.org/www-project-top-ten/)
- [Python Security Best Practices](https://python.readthedocs.io/en/stable/library/security_warnings.html)
- [PyPI Security Policy](https://pypi.org/security/)
