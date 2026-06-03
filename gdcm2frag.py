import os
import subprocess
import sys
import tempfile
import argparse

def fragment_dicom_directory(input_base, output_base, transfer_syntax, chunk_size_bytes=16000):
    """
    Recursively scans input_base for DICOM files, compresses them using gdcmconv
    with the selected transfer syntax, and forces fragmentation at the specified
    byte boundary using a two-pass approach.
    """
    # Ensure gdcmconv is available in the system PATH
    if subprocess.call(["which", "gdcmconv"], stdout=subprocess.PIPE, stderr=subprocess.PIPE) != 0:
        print("Error: gdcmconv is not installed or not in your PATH.")
        sys.exit(1)

    # Map the user selection to the exact gdcmconv flag
    syntax_flag = "--jpeg" if transfer_syntax == "jpeg" else "--j2k"

    for root, _, files in os.walk(input_base):
        for file in files:
            if file.startswith('.'):
                continue
                
            input_path = os.path.join(root, file)
            
            # Replicate the directory structure in the output folder
            rel_path = os.path.relpath(root, input_base)
            target_dir = os.path.join(output_base, rel_path)
            os.makedirs(target_dir, exist_ok=True)
            output_path = os.path.join(target_dir, file)
            
            # Create a temporary file for the intermediate compressed step
            with tempfile.NamedTemporaryFile(suffix=".dcm", delete=False) as tmp:
                tmp_path = tmp.name
            
            try:
                # Pass 1: Compress uncompressed to single-fragment using chosen syntax
                cmd_compress = ["gdcmconv", syntax_flag, input_path, tmp_path]
                subprocess.run(cmd_compress, capture_output=True, text=True, check=True)
                
                # Pass 2: Fragment the newly compressed file
                cmd_fragment = ["gdcmconv", "-S", str(chunk_size_bytes), tmp_path, output_path]
                subprocess.run(cmd_fragment, capture_output=True, text=True, check=True)
                
            except subprocess.CalledProcessError as e:
                print(f"Skipping or Failed: {input_path}")
                if e.stderr:
                    print(f" Reason: {e.stderr.strip()}")
                # Clean up output file if it was partially created on failure
                if os.path.exists(output_path):
                    os.remove(output_path)
            finally:
                # Always clean up the intermediate temp file
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Recursively compress and fragment DICOM files in a directory using gdcmconv."
    )
    
    # Positional Arguments
    parser.add_argument("input_dir", help="Path to the input directory containing DICOM files")
    parser.add_argument("output_dir", help="Path to the output directory for processed files")
    
    # Optional Arguments
    parser.add_argument(
        "-s", "--syntax", 
        choices=["jpeg", "j2k"], 
        default="jpeg", 
        help="Compression transfer syntax: 'jpeg' (Classic JPEG Lossless, default) or 'j2k' (JPEG 2000)"
    )
    parser.add_argument(
        "-b", "--bytes", 
        type=int, 
        default=16000, 
        help="Fragment chunk size in bytes (default: 16000)"
    )

    args = parser.parse_args()
    
    fragment_dicom_directory(
        input_base=args.input_dir, 
        output_base=args.output_dir, 
        transfer_syntax=args.syntax, 
        chunk_size_bytes=args.bytes
    )