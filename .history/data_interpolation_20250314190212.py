import os
import pandas as pd
import matplotlib.pyplot as plt

def interpolate_csv(input_csv, output_csv, target_interval=1, visualize=False):
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

    # **Perform interpolation (using `s` instead of `S`)**
    # df_resampled = df.resample(f"{target_interval}s").ffill()
    df_resampled = df.resample(f"{target_interval}s").interpolate(method="linear")


    # **Convert DatetimeIndex back to seconds**
    df_resampled.reset_index(inplace=True)
    df_resampled["timestamp"] = df_resampled["timestamp"].astype(int) // 10**9  # Convert back to integer seconds

    # **Save results**
    df_resampled.to_csv(output_csv, index=False)
    print(f"✅ Interpolation completed, saved to {output_csv}")

    # **Visualize interpolation effect**
    if visualize:
        plt.figure(figsize=(10, 5))
        plt.plot(df.index, df["arousal"], 'ro-', label="Original Data (3s)", markersize=5)
        plt.plot(df_resampled["timestamp"], df_resampled["arousal"], 'b.-', label="Interpolated Data (1s)", markersize=3)
        plt.xlabel("Timestamp (s)")
        plt.ylabel("Arousal Level")
        plt.legend()
        plt.title("Interpolation Before and After Comparison")
        plt.grid()
        plt.show()



if __name__ == "__main__":
    # 插值数据
    input_csv_file = "output/rgb_byz_baseline.csv"  # 你的原始 CSV 文件
    output_csv_file = input_csv_file.replace(".csv", "_interpolated.csv")
    interpolate_csv(input_csv_file, output_csv_file, target_interval=1, visualize=True)
