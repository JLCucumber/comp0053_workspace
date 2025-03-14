import os
import pandas as pd


def interpolate_csv(input_csv, output_csv, target_interval=1):
    """数据插值，将 3s 一次的标注转换为 1s 一次"""
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
