import cv2
import numpy as np
import argparse
import os
import sys
import struct

# Progress bar thanks to devs 'leemes/razz' on StackOverflow
def draw_progress_bar(current, total, prefix='Progress'):
    percent = int(100 * (current / total))
    bar_length = 40
    filled_length = int(bar_length * current // total)
    bar = '█' * filled_length + '-' * (bar_length - filled_length)
    sys.stdout.write(f'\r{prefix}: |{bar}| {percent}% ({current}/{total} frames)')
    sys.stdout.flush()

def encode_to_video(data_bytes, extension, output_name, width, height, fps, min_duration):
    ext_encoded = extension.encode('utf-8')[:64]
    header = struct.pack('Q64s', len(data_bytes), ext_encoded)
    full_payload = header + data_bytes
    payload_bits = np.unpackbits(np.frombuffer(full_payload, dtype=np.uint8)) * 255
    
    pixels_per_frame = width * height
    required_frames = max(int(fps * min_duration), 1)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_name, fourcc, fps, (width, height), isColor=False)
    
    print(f"--- Encoding: {extension} ({len(data_bytes)} bytes) ---")
    
    bits_placed = 0
    for i in range(required_frames):
        frame_bits = np.random.randint(0, 2, pixels_per_frame, dtype=np.uint8) * 255
        
        # Overlya data bits sequentially
        if bits_placed < len(payload_bits):
            remaining = payload_bits[bits_placed:]
            chunk = min(len(remaining), pixels_per_frame)
            frame_bits[:chunk] = remaining[:chunk]
            bits_placed += chunk
            
        out.write(frame_bits.reshape((height, width)))
        draw_progress_bar(i + 1, required_frames, prefix='Encoding')
        
    out.release()
    print(f"\nSaved as: {output_name}")

def decode_from_video(video_path):
    if not os.path.exists(video_path):
        print(f"Error: {video_path} not found.")
        return

    cap = cv2.VideoCapture(video_path)
    all_bits = []
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    print(f"--- Smart Decoding: {video_path} ---")
    frame_count = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret: break
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, 127, 1, cv2.THRESH_BINARY)
        all_bits.append(binary.flatten())
        
        frame_count += 1
        draw_progress_bar(frame_count, total_frames, prefix='Decoding')
    
    cap.release()
    print("\nReassembling file...")

    # Process OP bitstream
    raw_bytes = np.packbits(np.concatenate(all_bits).astype(np.uint8)).tobytes()
    
    if len(raw_bytes) < 72:
        print("Error: Video file is too small for a Smart Header.")
        return

    data_size, ext_raw = struct.unpack('Q64s', raw_bytes[:72])
    extension = ext_raw.decode('utf-8').strip('\x00')
    actual_data = raw_bytes[72 : 72 + data_size]

    # Outptu Logic
    if extension == ".txt":
        print("\nDecoded Message:\n" + "="*30)
        print(actual_data.decode('utf-8', errors='ignore'))
        print("="*30)
    else:
        out_file = f"recovered_file{extension}"
        with open(out_file, 'wb') as f:
            f.write(actual_data)
        print(f"\nDetected filetype {extension}. Saved as: {out_file}")

def main():
    parser = argparse.ArgumentParser(description="Static Architect: Moving Binary Static")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("-e", "--encode", action="store_true", help="Encode mode")
    mode.add_argument("-d", "--decode", action="store_true", help="Decode mode")

    parser.add_argument("-i", "--input", required=True, help="Input file or message")
    parser.add_argument("-o", "--output", help="Optional output video name")
    parser.add_argument("-t", "--text", action="store_true", help="Input is a text message")
    parser.add_argument("--duration", type=float, default=5.0, help="Min video length in seconds")

    args = parser.parse_args()

    if args.encode:
        if args.text:
            data, ext = args.input.encode('utf-8'), ".txt"
        else:
            data = open(args.input, 'rb').read()
            ext = os.path.splitext(args.input)[1] or ".bin"
        
        out_name = args.output or "static_smart.mp4"
        encode_to_video(data, ext, out_name, 1280, 720, 30, args.duration)
    elif args.decode:
        decode_from_video(args.input)

if __name__ == "__main__":
    main()