import json
import subprocess
from collections import defaultdict

def main():
    result = subprocess.run(['cargo', 'clippy', '--message-format=json'], capture_output=True, text=True)
    
    missing_docs = defaultdict(list)
    
    for line in result.stdout.splitlines():
        try:
            msg = json.loads(line)
        except:
            continue
        if msg.get('reason') != 'compiler-message':
            continue
        message = msg.get('message', {})
        if message.get('code') and message['code'].get('code') == 'clippy::missing_errors_doc':
            spans = message.get('spans', [])
            for span in spans:
                if span.get('is_primary'):
                    missing_docs[span['file_name']].append({
                        'line': span['line_start'],
                        'text': span.get('text', [{}])[0].get('text', '').strip()
                    })
    
    for file_name, errors in missing_docs.items():
        print(f"{file_name}:")
        for err in errors:
            print(f"  Line {err['line']}: {err['text']}")

if __name__ == '__main__':
    main()
