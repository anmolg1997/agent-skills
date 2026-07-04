# Security Policy

## Reporting a vulnerability

Please report security issues privately through GitHub's [private vulnerability reporting](https://docs.github.com/en/code-security/security-advisories/guidance-on-reporting-and-writing-information-about-vulnerabilities/privately-reporting-a-security-vulnerability) on this repository (Security tab, "Report a vulnerability"). Do not open a public issue for a suspected vulnerability.

We aim to acknowledge reports within a few days and to address confirmed issues promptly.

## Scope and what to look for

These are Claude Code skills. Two behaviors are worth understanding when assessing risk:

- **The scripts fetch remote URLs.** `pm.py fetch` and `ai.py fetch` retrieve incident source pages (with an archive.org fallback) and strip them to text. They do not execute fetched content, but they do make outbound network requests to third-party sites.
- **The skills run locally with your permissions.** Like any Claude Code skill, the workflows can invoke the bundled Python scripts. They use only the Python standard library and `curl`, and they do not write outside paths you pass them.

In-scope reports include: a way to make the scripts execute untrusted fetched content, a path traversal or arbitrary-write in the CLI, or a supply-chain risk in the bundled data or manifests. Out of scope: the content of third-party postmortems we link to, and issues in Claude Code itself.

## Supported versions

The latest `main` is supported. Fixes are released on `main` and noted in `CHANGELOG.md`.
