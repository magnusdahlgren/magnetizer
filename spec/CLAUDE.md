# Magnetizer — context for Claude

## Running tests

```
cd /Users/magnus/Documents/Code/Photo Blog/magnetizer
/usr/local/bin/python3 -m pytest tests/
```

## Test project

A working project for manual testing lives at:

```
/Users/magnus/Documents/Code/Photo Blog/test_project/
```

To rebuild it after code or template changes:

```
cd /Users/magnus/Documents/Code/Photo Blog/test_project
/usr/local/bin/python3 /Users/magnus/Documents/Code/Photo Blog/magnetizer/build.py --flush --resources
```

Use `--resources` alone when only CSS/JS changed (skips the full content rebuild).

## Development approach

This project is built strictly TDD: tests are written first, verified to fail, then the implementation is written. Don't implement anything without a failing test first.
