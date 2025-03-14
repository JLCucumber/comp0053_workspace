import os
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from scipy.interpolate import CubicSpline

matplotlib.rcParams["font.family"] = "DejaVu Sans"  # 


def interpolate_csv(input_csv, output_csv, target_interval=1, visualize=False, method="linear"):
    """Data interpolation: Convert annotations from 3s intervals to 1s intervals and visualize the difference"""
    if not os.path.exists(input_csv):
        print(f"❌ Input file {input_csv} does not exist!")
        return
    
    # **Read CSV file**
    df = pd.read_csv(input_csv)

    # **Ensure timestamp is an integer**
    df["timestamp"] = pd.to_numeric(df["timestamp"], errors="coerce")

    # **Convert to DatetimeIndex**
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")

    # **Set index**
    df.set_index("timestamp", inplace=True)

    if method == "spline":
        # **Perform cubic spline interpolation**
        timestamps = df.index.astype(int) // 10**9  # Convert timestamps to integer seconds
        arousal_values = df["arousal"].values
        cs = CubicSpline(timestamps, arousal_values)
        new_timestamps = range(timestamps[0], timestamps[-1] + 1, target_interval)
        new_arousal = cs(new_timestamps)
        df_resampled = pd.DataFrame({"timestamp": new_timestamps, "arousal": new_arousal})
    else:
        # **Perform linear interpolation (default)**
        df_resampled = df.resample(f"{target_interval}s").interpolate(method=method)
        df_resampled.reset_index(inplace=True)
        df_resampled["timestamp"] = df_resampled["timestamp"].astype(int) // 10**9  # Convert back to integer seconds

    # **Save results**
    df_resampled.to_csv(output_csv, index=False)
    print(f"✅ Interpolation completed, saved to {output_csv}")


def visualize_interpolation(original_csv, interpolated_csv):
    """Function to visualize interpolation effect separately"""
    if not os.path.exists(original_csv) or not os.path.exists(interpolated_csv):
        print("❌ One or both files do not exist!")
        return
    
    # **Read files**
    df_original = pd.read_csv(original_csv)
    df_interpolated = pd.read_csv(interpolated_csv)

    # **Ensure timestamps are numeric and sorted**
    df_original["timestamp"] = pd.to_numeric(df_original["timestamp"], errors="coerce")
    print(df_original["timestamp"])
    df_interpolated["timestamp"] = pd.to_numeric(df_interpolated["timestamp"], errors="coerce")
    df_original = df_original.sort_values("timestamp")
    df_interpolated = df_interpolated.sort_values("timestamp")

    plt.figure(figsize=(10, 5))

    # **Fix: Use correct timestamps for original data**
    plt.plot(df_original["timestamp"], df_original["arousal"], 'ro-', label="Original Data (3s)", markersize=5, linestyle="None")

    # **Plot interpolated data**
    plt.plot(df_interpolated["timestamp"], df_interpolated["arousal"], 'bo-', label="Interpolated Data (1s, spline)", markersize=3, linestyle="None")

    # **Fix X-axis labels to avoid overlap**
    plt.xticks(df_interpolated["timestamp"][::5], labels=df_interpolated["timestamp"][::5].astype(str), rotation=45)

    plt.xlabel("Timestamp (from CSV labels)")
    plt.ylabel("Arousal Level")
    plt.legend()
    plt.title("Interpolation Before and After Comparison")
    plt.grid()
    plt.show()





# if __name__ == "__main__":
#     # 插值数据
#     input_csv_file = "output/rgb_byz_game_session.csv"  # 你的原始 CSV 文件
#     output_csv_file = input_csv_file.replace(".csv", "_interpolated.csv")
#     interpolate_csv(input_csv_file, output_csv_file, target_interval=1, visualize=True, method="spline")
#     visualize_interpolation(input_csv_file, output_csv_file)