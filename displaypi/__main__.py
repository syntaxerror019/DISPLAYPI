"""Entry point for `python -m displaypi`."""

from .app import App


def main():
    App().run()


if __name__ == "__main__":
    main()