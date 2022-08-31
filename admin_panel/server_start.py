#!/usr/bin/env python
import uvicorn

from admin_panel import app


def main():
    uvicorn.run(app.app, host="127.0.0.1", port=8000)


if __name__ == '__main__':
    main()
