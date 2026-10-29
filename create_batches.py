import os
import csv
import shutil

def split_and_distribute():
    base_dir = r"c:\Users\BIT\Downloads\minor_proj\fire-and-smoke-main"
    fire_csv_path = os.path.join(base_dir, "fire.csv")
    smoke_csv_path = os.path.join(base_dir, "smoke.csv")
    script_path = os.path.join(base_dir, "scripts", "extract_youtube_frames.py")
    output_dir = os.path.join(base_dir, "youtube_frames")
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Read data
    def read_csv(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader)
            rows = list(reader)
        return header, rows

    fire_header, fire_rows = read_csv(fire_csv_path)
    smoke_header, smoke_rows = read_csv(smoke_csv_path)
    
    # All rows, 90 from fire, 15 from smoke
    all_rows = fire_rows + smoke_rows
    # We'll use the fire header since they are the same format
    header = fire_header
    
    batch_size = 10
    total_batches = (len(all_rows) + batch_size - 1) // batch_size
    
    requirements_content = "yt-dlp\nopencv-python\nnumpy\n"
    
    for i in range(total_batches):
        batch_num = i + 1
        batch_folder = os.path.join(output_dir, f"batch_{batch_num}")
        os.makedirs(batch_folder, exist_ok=True)
        
        # 1. Write the chunked CSV
        chunk = all_rows[i * batch_size : (i + 1) * batch_size]
        csv_out_path = os.path.join(batch_folder, "videos.csv")
        with open(csv_out_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(chunk)
            
        # 2. Copy the Python script
        shutil.copy2(script_path, os.path.join(batch_folder, "extract_youtube_frames.py"))
        
        # 3. Create requirements.txt
        with open(os.path.join(batch_folder, "requirements.txt"), "w") as f:
            f.write(requirements_content)
            
        # 4. Optional: create a small README or bat file to make it click-and-run
        bat_content = "@echo off\npip install -r requirements.txt\npython extract_youtube_frames.py --csv videos.csv --skip 0 --limit 10 --out-dir extracted_frames\npause\n"
        with open(os.path.join(batch_folder, "run_extraction.bat"), "w") as f:
            f.write(bat_content)

        print(f"Created {batch_folder} with {len(chunk)} videos.")

if __name__ == '__main__':
    split_and_distribute()
