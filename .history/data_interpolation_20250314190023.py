import os
import pandas as pd


def interpolate_csv(input_csv, output_csv, target_interval=1, visualize=False):
    """数据插值，将 3s 一次的标注转换为 1s 一次，并可视化前后对比"""
    if not os.path.exists(input_csv):
        print(f"❌ 输入文件 {input_csv} 不存在！")
        return
    
    # **读取 CSV 文件**
    df = pd.read_csv(input_csv)

    # **确保 timestamp 是整数**
    df["timestamp"] = pd.to_numeric(df["timestamp"], errors="coerce")

    # **转换为 DatetimeIndex**
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")

    # **设置索引**
    df.set_index("timestamp", inplace=True)

    # **进行插值（使用 `s` 而不是 `S`）**
    df_resampled = df.resample(f"{target_interval}s").ffill()

    # **将 DatetimeIndex 转换回秒数**
    df_resampled.reset_index(inplace=True)
    df_resampled["timestamp"] = df_resampled["timestamp"].astype(int) // 10**9  # 转换回整数秒

    # **保存结果**
    df_resampled.to_csv(output_csv, index=False)
    print(f"✅ 插值完成，已保存到 {output_csv}")

    # **可视化插值效果**
    if visualize:
        plt.figure(figsize=(10, 5))
        plt.plot(df.index, df["arousal"], 'ro-', label="原始数据 (3s)", markersize=5)
        plt.plot(df_resampled["timestamp"], df_resampled["arousal"], 'b.-', label="插值数据 (1s)", markersize=3)
        plt.xlabel("时间戳 (s)")
        plt.ylabel("Arousal 等级")
        plt.legend()
        plt.title("插值前后对比")
        plt.grid()
        plt.show()



if __name__ == "__main__":
    # 插值数据
    input_csv_file = "output/rgb_byz_baseline.csv"  # 你的原始 CSV 文件
    output_csv_file = input_csv_file.replace(".csv", "_interpolated.csv")
    interpolate_csv(input_csv_file, output_csv_file, target_interval=1)
