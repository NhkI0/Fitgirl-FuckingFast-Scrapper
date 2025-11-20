import subprocess
import os
import glob
from datetime import datetime
from tqdm import tqdm


def find_7zip():
    """Find 7-Zip installation"""
    possible_paths = [
        r"C:\Program Files\7-Zip\7z.exe",
        r"C:\Program Files (x86)\7-Zip\7z.exe",
    ]

    for path in possible_paths:
        if os.path.exists(path):
            return path

    raise FileNotFoundError("7-Zip not found! Install from https://www.7-zip.org/")


def get_volumes_count(seven_zip, rar_file):
    """Get number of volumes to extract"""
    result = subprocess.run([
        seven_zip, 'l', '-slt', rar_file
    ], capture_output=True, text=True)

    for line in result.stdout.split('\n'):
        if line.startswith('Volumes = '):
            return int(line.split('=')[1].strip())

    return 1  # Single archive if not found


def format_size(nb_bytes):
    """Format bytes to human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if nb_bytes < 1024.0:
            return f"{nb_bytes:.1f}{unit}"
        nb_bytes /= 1024.0
    return f"{nb_bytes:.1f}TB"


def get_archive_info(seven_zip, rar_file):
    """Get information about the archive"""
    result = subprocess.run([
        seven_zip, 'l', '-slt', rar_file
    ], capture_output=True, text=True)

    # Count files and calculate size
    lines = result.stdout.split('\n')
    file_count = 0
    total_size = 0

    for line in lines:
        if line.startswith('Path = ') and not line.endswith('.rar'):
            file_count += 1
        if line.startswith('Size = '):
            # noinspection PyBroadException
            try:
                size = int(line.split('=')[1].strip())
                total_size += size
            except:
                pass

    return file_count, total_size


def extract_rar_with_tqdm(rar_file, output_dir):
    """Extract RAR archive with tqdm progress bar"""

    # Find 7-Zip
    try:
        seven_zip = find_7zip()
    except FileNotFoundError as e:
        print(f"✗ Error: {e}")
        return 1

    # Get archive info
    print("═" * 80)
    print("🔍 Analyzing archive...")
    file_count, total_size = get_archive_info(seven_zip, rar_file)

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Print header
    print("─" * 80)
    print(f"📦 Extracting Archive...")
    print(f"File: {os.path.basename(rar_file)}")
    print(f"Number of volumes: {get_volumes_count(seven_zip, rar_file)}")
    print(f"Files to extract: {file_count}")
    print(f"Total size: {format_size(total_size)}")
    print(f"Destination: {output_dir}")
    print("─" * 80)

    # Run extraction with tqdm
    start_time = datetime.now()

    process = subprocess.Popen([
        seven_zip, 'x',
        rar_file,
        f'-o{output_dir}',
        '-y',
        '-bsp1'  # Show progress as percentage
    ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)

    # Create progress bar
    pbar = tqdm(
        total=100,
        desc="Extracting",
        unit="%",
        bar_format="{desc}: {percentage:3.0f}%|{bar}| {n:.0f}/{total:.0f} [{elapsed}<{remaining}]",
        ncols=80
    )

    last_percent = 0

    for line in process.stdout:
        line = line.strip()

        # Track current file
        if line.startswith('- '):
            current_file = line[2:]
            if len(current_file) > 50:
                current_file = current_file[:47] + "..."
            pbar.set_postfix_str(current_file)

        # Track progress percentage
        elif '%' in line and line[0].isdigit():
            # noinspection PyBroadException
            try:
                percent = int(line.split('%')[0].strip())
                if percent > last_percent:
                    pbar.update(percent - last_percent)
                    last_percent = percent
            except:
                pass

    pbar.close()
    process.wait()

    # Calculate elapsed time
    elapsed = (datetime.now() - start_time).total_seconds()
    minutes = int(elapsed // 60)
    seconds = elapsed % 60

    # Print footer
    if process.returncode == 0:
        print("✓ Extraction completed!")
        print(f"✓ Files extracted to: {output_dir}")
        print(f"✓ Time elapsed: {minutes}m {seconds:.1f}s")
        print("=" * 80)
        print(" " * 25 + "EXTRACTION COMPLETE")
        print("=" * 80)
        print(f"✓ Successfully extracted: {file_count} files")
        print(f"✓ Total size: {format_size(total_size)}")
        print("=" * 80)
        return 0
    else:
        print("✗ Extraction failed!")
        print(f"✗ Error code: {process.returncode}")
        print("=" * 80)
        return process.returncode


def extract(folder):
    try:
        first_rar = glob.glob(f"{folder}/*.part01.rar")[0]
    except IndexError:
        first_rar = glob.glob(f"{folder}/*.part1.rar")[0]

    extract_path = f"{folder}/Extracted"
    extract_rar_with_tqdm(first_rar, extract_path)
