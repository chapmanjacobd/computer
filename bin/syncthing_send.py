#!/usr/bin/python3
import argparse
import json
import os
import time

import requests
from library.utils import processes


def get_syncthing_api_url(args, endpoint):
    return f"http://{args.host}:{args.port}/rest/{endpoint}"


def syncthing_api_call(args, endpoint, method="GET", data=None):
    url = get_syncthing_api_url(args, endpoint)
    try:
        if method == "GET":
            response = requests.get(url, headers={"X-API-Key": args.api_key})
        elif method == "POST":
            response = requests.post(url, headers={"X-API-Key": args.api_key}, data=json.dumps(data))
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print("API call to %s failed %s", url, e)
        return None


def main(args):
    try:
        version = syncthing_api_call(args, "system/version")
        assert version and version['version']
    except Exception as e:
        print(f"Error connecting to Syncthing API: {e}")
        print("Please check your host, port, and API key.")
        return

    folder_id = None
    folder_name = None
    all_folders = syncthing_api_call(args, "config/folders")
    if all_folders:
        for folder in all_folders:
            folder_name = os.path.expanduser(folder['path'])
            if os.path.samefile(folder_name, args.folder_path):
                folder_id = folder['id']
                break
    if not folder_id:
        print(f"Error: Could not find a Syncthing folder with the path '{args.folder_path}'.")
        return

    print(f"Monitoring folder ID '{folder_id}' located at '{folder_name}'...")
    deleted_files = set()

    while True:
        try:
            browse_path = f"db/browse?folder={folder_id}"
            files_to_check = syncthing_api_call(args, browse_path)

            if files_to_check:
                local_device_info = syncthing_api_call(args, "system/status")
                local_device_id = local_device_info['myID'] if local_device_info else None

                for file_info in files_to_check:
                    file_name = file_info['name']
                    file_path = os.path.join(args.folder_path, file_name)

                    if file_info['type'] == 'directory':
                        continue

                    try:
                        file_status_path = f"db/file?folder={folder_id}&file={file_name}"
                        file_status = syncthing_api_call(args, file_status_path)

                        if not file_status:
                            continue
                        elif file_status['local']['blocksHash'] != file_status['global']['blocksHash']:
                            continue
                        elif file_status['local']['blocksHash'] in deleted_files:
                            continue

                        is_synced_on_remote = False
                        if file_status.get('availability'):
                            for device in file_status['availability']:
                                if (
                                    device['id'] != local_device_id and not device['fromTemporary']
                                ):  # TODO check what fromTemporary actually is...
                                    is_synced_on_remote = True
                                    break

                        if is_synced_on_remote:
                            if os.path.exists(file_path):
                                print(f"File '{file_path}' is synced to at least one device. Deleting...")
                                os.unlink(file_path)
                            else:
                                print(f"File '{file_path}' not found locally. Skipping.")

                            deleted_files.add(file_status['local']['blocksHash'])

                    except Exception as e:
                        print(f"Error processing file '{file_name}'")
                        continue

            time.sleep(args.interval)

        except KeyboardInterrupt:
            print("\nMonitoring stopped by user.")
            break
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            print(f"Sleeping for {args.interval} seconds before retrying...")
            time.sleep(args.interval)


if __name__ == "__main__":
    KEY = os.getenv('SYNCTHING_API_KEY')
    HOST = os.getenv('SYNCTHING_HOST')
    PORT = os.getenv('SYNCTHING_PORT')

    parser = argparse.ArgumentParser(
        description="Monitor a Syncthing send-only folder and delete files after they are synced to another device which has ignoreDeletes set"
    )
    parser.add_argument(
        "--host",
        default=HOST or 'localhost',
        help="The host of the Syncthing instance (e.g., '127.0.0.1' or 'localhost').",
    )
    parser.add_argument("--port", type=int, default=PORT or 8384, help="The port of the Syncthing web interface.")
    parser.add_argument(
        "--api-key",
        default=KEY,
        help="The API key from your Syncthing settings. Can also be set via SYNCTHING_API_KEY environment variable.",
    )
    parser.add_argument(
        "--interval", "-I", type=int, default=5 * 60, help="The time in seconds to wait between checks."
    )
    parser.add_argument("--timeout", default="24h", help="The max time to wait")
    parser.add_argument("folder_path", help="A Syncthing send-only folder root")
    args = parser.parse_args()

    if not args.api_key:
        parser.error(
            "The API key is required. Please provide it via --api-key or set the SYNCTHING_API_KEY environment variable."
        )

    processes.timeout(args.timeout)

    main(args)
