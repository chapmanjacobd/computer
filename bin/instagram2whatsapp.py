import json
import glob
import datetime
import sys

def fix_encoding(s):
    try:
        return s.encode('latin1').decode('utf-8')
    except:
        return s

def process_messages():
    files = glob.glob('message_*.json')
    all_messages = []
    
    for f in files:
        with open(f, 'r', encoding='utf-8') as file:
            data = json.load(file)
            messages = data.get('messages', [])
            for m in messages:
                all_messages.append(m)
                
    # Sort messages by timestamp_ms
    all_messages.sort(key=lambda x: x.get('timestamp_ms', 0))
    
    with open('whatsapp_export.txt', 'w', encoding='utf-8') as out:
        out.write("3/13/23, 11:22 - Messages and calls are end-to-end encrypted. Only people in this chat can read, listen to, or share them. *Learn more*\n")
        
        for msg in all_messages:
            ts = msg.get('timestamp_ms')
            if not ts:
                continue
                
            # Convert timestamp to mm/dd/yy, hh:mm
            # timestamp_ms is in milliseconds
            dt = datetime.datetime.fromtimestamp(ts / 1000.0)
            
            # Format time like 3/13/23, 11:22
            date_str = dt.strftime('%-m/%-d/%y, %H:%M')
            
            sender = msg.get('sender_name', 'Unknown')
            sender = fix_encoding(sender)
            
            # Use the first name
            sender_first_name = sender.split(' ')[0] if sender else 'Unknown'
            
            if 'content' in msg:
                content = fix_encoding(msg['content'])
                # Replace newlines in messages so they don't break the log format, though WhatsApp allows newlines.
                # Actually WhatsApp allows newlines in messages.
            else:
                if 'photos' in msg:
                    content = '<Media omitted>'
                elif 'videos' in msg:
                    content = '<Media omitted>'
                elif 'audio_files' in msg:
                    content = '<Media omitted>'
                elif 'gifs' in msg:
                    content = '<Media omitted>'
                elif 'sticker' in msg:
                    content = '<Media omitted>'
                else:
                    content = '<Media omitted>'
                    
            out.write(f"{date_str} - {sender_first_name}: {content}\n")

if __name__ == '__main__':
    process_messages()
    print("Done! Wrote to whatsapp_export.txt")
