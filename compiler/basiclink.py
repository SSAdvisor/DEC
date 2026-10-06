import sys
import json
import struct
import os
import shutil

def main():
    args = sys.argv[1:]
    if len(args) < 2:
        print("Usage: basiclink.py [-o output] <input1.bobj> [input2.bobj ...]")
        return
        
    output_file = "a.out"
    if "-o" in args:
        idx = args.index("-o")
        output_file = args[idx+1]
        args.pop(idx)
        args.pop(idx)
        
    bobj_files = [arg for arg in args if arg.endswith('.bobj')]
    odl_files = [arg for arg in args if arg.endswith('.odl')]
    
    # 0. Parse ODL file
    overlay_tree = {}
    if odl_files:
        with open(odl_files[0], 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith(';'):
                    continue
                # Super simple ODL parser for the concept
                if line.startswith('.ROOT'):
                    overlay_tree['ROOT'] = line.split()[1]
                elif '.FCTR' in line:
                    parts = line.split(':')
                    if len(parts) == 2:
                        name = parts[0].strip()
                        fctr = parts[1].replace('.FCTR', '').strip()
                        overlay_tree[name] = fctr
        print(f"Parsed ODL File: {overlay_tree}")

    # 1. Load all bobj files
    segments = []
    for f in bobj_files:
        with open(f, 'r') as bobj_f:
            obj = json.load(bobj_f)
            segments.append({
                'module': obj['module'],
                'bytecode': bytearray(obj['bytecode']),
                'strings': obj.get('strings', [])
            })
            
    # For now, we will merge all strings into a global string pool
    global_strings = []
    # And we just concatenate bytecode as different "segments"
    # A real ODL parser would determine the overlay tree here.
    
    # Pack the payload
    # Format: 
    # [MAGIC "RSTS"] [PAYLOAD_SIZE (4)] [NUM_SEGMENTS (2)]
    # Segments: [NAME (16)] [SIZE (4)] [DATA ...]
    
    payload = bytearray()
    
    # Number of segments
    num_segments = len(segments)
    payload.extend(struct.pack('<H', num_segments))
    
    segment_data_offset = 0
    segment_data_pool = bytearray()
    
    for seg in segments:
        name_bytes = seg['module'].encode('utf-8')[:15]
        name_bytes = name_bytes.ljust(16, bytes([0]))
        size = len(seg['bytecode'])
        
        payload.extend(name_bytes)
        payload.extend(struct.pack('<I', size))
        
        segment_data_pool.extend(seg['bytecode'])
        
    payload.extend(segment_data_pool)
    
    total_size = len(payload)
    
    final_payload = bytearray(payload)
    final_payload.extend(b'RSTS')
    final_payload.extend(struct.pack('<I', total_size))
    
    # 2. Package into executable
    vm_executable = "vm/build/rsts_vm"
    if not os.path.exists(vm_executable):
        print(f"Error: VM executable not found at {vm_executable}. Please build it first.")
        return
        
    shutil.copy2(vm_executable, output_file)
    with open(output_file, "ab") as f:
        f.write(final_payload)
        
    os.chmod(output_file, 0o755)
    print(f"Successfully linked {len(segments)} segments into {output_file}")

if __name__ == '__main__':
    main()
