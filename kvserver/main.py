# mymodule.py
import argparse, threading, keyboard, time, os
from kvserver.server import SocketServer

setup_data = '''{
    "exclude_dirs":[
        "env",
        "venv"
    ],
    "exclude_files":[
        ".gitignore"
    ],
    "ignore_pattern":[
        ".gitignore"
    ]

}'''

def start_server(server):
    while True:
        server.recv_conn()

def main():
    parser = argparse.ArgumentParser(description="A simple greeting module.")
    parser.add_argument("port", nargs="?", type=int, default=7000, help="The port to run the server on (default: 5000)")
    args = parser.parse_args()

    
    observer_path = os.path.join(os.getcwd(), "setup.json")
    if not os.path.exists(observer_path):
        with open(observer_path, "w")as f:f.write(setup_data)

    # server = SocketServer(args.port)
    # threading.Thread(target=lambda:start_server(server), daemon=True).start()
    # time.sleep(.1)
    # # print("Press R to reload\n ")
    # print(f"\n\n Press Q to exit")
    # while True:
    #     key = keyboard.read_key()
    #     # if key == "r" or key == "R":
    #     #     print(f"Reloading...")
    #     #     server.on_reload()
    #     if key == "q" or key == "Q":
    #         break
    
    server = SocketServer(port=args.port)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n› Server shutdown complete.")

if __name__ == "__main__":
    main()


# pip install <package-name> --target /path/to/folder

# pip install -r requirements.txt --target /path/to/folder