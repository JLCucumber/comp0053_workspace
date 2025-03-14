import os
import pandas as pd


def check_and_extend_csv(csv_file, segment_duration=3):
    """Check CSV file length and extend if necessary"""
    
    if not os.path.exists(csv_file):
        print(f"❌ File {csv_file} does not exist!")
        return
    
    # **Determine the target end time based on filename**
    if "_game_session.csv" in csv_file:
        target_time = 900
    elif "_baseline.csv" in csv_file:
        target_time = 60
    else:
        print(f"⚠️ File {csv_file} does not match naming convention, skipping extension.")
        return
    
    # **Read CSV file**
    df = pd.read_csv(csv_file)

    # **Ensure timestamps are numeric and sorted**
    df["timestamp"] = pd.to_numeric(df["timestamp"], errors="coerce")
    df = df.sort_values("timestamp")

    # **Get last row values**
    last_timestamp = df["timestamp"].iloc[-1]
    last_arousal = df["arousal"].iloc[-1]

    # **Extend timestamps if needed**
    if last_timestamp < target_time:
        new_rows = []
        while last_timestamp + segment_duration <= target_time:
            last_timestamp += segment_duration
            new_rows.append({"timestamp": last_timestamp, "arousal": last_arousal})

        # **Append new rows to DataFrame**
        df = pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True)

        # **Save extended CSV**
        df.to_csv(csv_file, index=False)
        print(f"✅ Extended {csv_file} to {target_time}s.")
    else:
        print(f"✅ {csv_file} already meets the required duration.")


if __name__ == "__main__":
    # check_and_extend_csv("output/rgb_byz_game_session.csv", segment_duration=3)
    check_and_extend_csv("output/rgb_byz_baseline.csv", segment_duration=3)