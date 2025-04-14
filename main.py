from src.server import server  # noqa

if __name__ == "__main__":
    import sys

    try:
        server.run(transport="stdio")
    except Exception as e:
        print(e, file=sys.stderr)
