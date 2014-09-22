from imageserver.app import app


if __name__ == "__main__":
    app.run(use_debugger=True, use_reloader=True, debug=True, host='0.0.0.0', port=8001)
