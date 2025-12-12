#!/usr/bin/env python3
"""
RTK Benchmark 结果分析脚本
读取所有benchmark数据集并生成性能对比报告
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json
from pathlib import Path

# 配置中文字体（如果需要）
plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

BENCHMARK_DIR = "benchmark"
FORMATIONS = ["cross", "line", "triangle", "v_formation"]
DIFFICULTIES = ["Easy", "Moderate", "Hard"]

def parse_flow_stats(csv_file):
    """解析流统计文件"""
    if not os.path.exists(csv_file):
        return None
    
    df = pd.read_csv(csv_file)
    
    stats = {
        'total_flows': len(df),
        'total_tx_packets': df['TxPackets'].sum(),
        'total_rx_packets': df['RxPackets'].sum(),
        'total_lost_packets': df['LostPackets'].sum(),
        'avg_loss_rate': df['PacketLossRate(%)'].mean(),
        'avg_throughput': df['Throughput(bps)'].mean(),
        'total_throughput': df['Throughput(bps)'].sum(),
        'avg_delay': df['DelaySum'].mean(),
        'max_delay': df['DelaySum'].max(),
        'pdr': (df['RxPackets'].sum() / df['TxPackets'].sum() * 100) if df['TxPackets'].sum() > 0 else 0
    }
    
    return stats

def parse_topology_changes(txt_file):
    """解析拓扑变化文件"""
    if not os.path.exists(txt_file):
        return None
    
    with open(txt_file, 'r') as f:
        lines = f.readlines()
    
    total_intervals = len(lines)
    active_intervals = sum(1 for line in lines if 'none' not in line.lower())
    
    stats = {
        'total_intervals': total_intervals,
        'active_intervals': active_intervals,
        'topology_stability': (active_intervals / total_intervals * 100) if total_intervals > 0 else 0
    }
    
    return stats

def parse_positions(csv_file):
    """解析位置轨迹文件"""
    if not os.path.exists(csv_file):
        return None
    
    df = pd.read_csv(csv_file)
    
    # 计算节点移动距离
    nodes = df['nodeId'].unique()
    total_distance = 0
    
    for node in nodes:
        node_data = df[df['nodeId'] == node].sort_values('time_s')
        if len(node_data) > 1:
            distances = np.sqrt(
                np.diff(node_data['x'].values)**2 + 
                np.diff(node_data['y'].values)**2 + 
                np.diff(node_data['z'].values)**2
            )
            total_distance += distances.sum()
    
    stats = {
        'num_nodes': len(nodes),
        'num_samples': len(df),
        'total_distance': total_distance,
        'avg_distance_per_node': total_distance / len(nodes) if len(nodes) > 0 else 0
    }
    
    return stats

def analyze_dataset(dataset_path, formation, difficulty):
    """分析单个数据集"""
    print(f"分析: {formation}_{difficulty}")
    
    result = {
        'formation': formation,
        'difficulty': difficulty,
        'path': dataset_path
    }
    
    # 解析流统计
    flow_stats_file = os.path.join(dataset_path, 'flow-stats.csv')
    flow_stats = parse_flow_stats(flow_stats_file)
    if flow_stats:
        result.update(flow_stats)
    
    # 解析拓扑变化
    topo_file = os.path.join(dataset_path, 'topology-changes.txt')
    topo_stats = parse_topology_changes(topo_file)
    if topo_stats:
        result.update(topo_stats)
    
    # 解析位置信息
    pos_file = os.path.join(dataset_path, 'node-positions.csv')
    pos_stats = parse_positions(pos_file)
    if pos_stats:
        result.update(pos_stats)
    
    return result

def generate_comparison_plots(results_df, output_dir):
    """生成对比图表"""
    print("\n生成对比图表...")
    
    os.makedirs(output_dir, exist_ok=True)
    
    # 图1: PDR对比
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Packet Delivery Ratio (PDR) Comparison', fontsize=16, fontweight='bold')
    
    for idx, formation in enumerate(FORMATIONS):
        ax = axes[idx // 2, idx % 2]
        formation_data = results_df[results_df['formation'] == formation]
        
        if not formation_data.empty:
            x = range(len(DIFFICULTIES))
            y = [formation_data[formation_data['difficulty'] == d]['pdr'].values[0] 
                 if not formation_data[formation_data['difficulty'] == d].empty else 0
                 for d in DIFFICULTIES]
            
            colors = ['#2ecc71', '#f39c12', '#e74c3c']
            ax.bar(x, y, color=colors, alpha=0.7, edgecolor='black')
            ax.set_xticks(x)
            ax.set_xticklabels(DIFFICULTIES)
            ax.set_ylabel('PDR (%)')
            ax.set_title(f'{formation.capitalize()} Formation')
            ax.set_ylim([0, 105])
            ax.grid(axis='y', alpha=0.3)
            
            # 添加数值标签
            for i, v in enumerate(y):
                ax.text(i, v + 2, f'{v:.1f}%', ha='center', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'pdr_comparison.png'), dpi=300, bbox_inches='tight')
    print(f"  ✓ 保存: {output_dir}/pdr_comparison.png")
    plt.close()
    
    # 图2: 吞吐量对比
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Average Throughput Comparison', fontsize=16, fontweight='bold')
    
    for idx, formation in enumerate(FORMATIONS):
        ax = axes[idx // 2, idx % 2]
        formation_data = results_df[results_df['formation'] == formation]
        
        if not formation_data.empty:
            x = range(len(DIFFICULTIES))
            y = [formation_data[formation_data['difficulty'] == d]['avg_throughput'].values[0] / 1e6
                 if not formation_data[formation_data['difficulty'] == d].empty else 0
                 for d in DIFFICULTIES]
            
            colors = ['#2ecc71', '#f39c12', '#e74c3c']
            ax.bar(x, y, color=colors, alpha=0.7, edgecolor='black')
            ax.set_xticks(x)
            ax.set_xticklabels(DIFFICULTIES)
            ax.set_ylabel('Throughput (Mbps)')
            ax.set_title(f'{formation.capitalize()} Formation')
            ax.grid(axis='y', alpha=0.3)
            
            # 添加数值标签
            for i, v in enumerate(y):
                ax.text(i, v + v*0.05, f'{v:.2f}', ha='center', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'throughput_comparison.png'), dpi=300, bbox_inches='tight')
    print(f"  ✓ 保存: {output_dir}/throughput_comparison.png")
    plt.close()
    
    # 图3: 丢包率对比
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Packet Loss Rate Comparison', fontsize=16, fontweight='bold')
    
    for idx, formation in enumerate(FORMATIONS):
        ax = axes[idx // 2, idx % 2]
        formation_data = results_df[results_df['formation'] == formation]
        
        if not formation_data.empty:
            x = range(len(DIFFICULTIES))
            y = [formation_data[formation_data['difficulty'] == d]['avg_loss_rate'].values[0]
                 if not formation_data[formation_data['difficulty'] == d].empty else 0
                 for d in DIFFICULTIES]
            
            colors = ['#2ecc71', '#f39c12', '#e74c3c']
            ax.bar(x, y, color=colors, alpha=0.7, edgecolor='black')
            ax.set_xticks(x)
            ax.set_xticklabels(DIFFICULTIES)
            ax.set_ylabel('Loss Rate (%)')
            ax.set_title(f'{formation.capitalize()} Formation')
            ax.grid(axis='y', alpha=0.3)
            
            # 添加数值标签
            for i, v in enumerate(y):
                ax.text(i, v + v*0.05 if v > 0 else 1, f'{v:.2f}%', ha='center', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'loss_rate_comparison.png'), dpi=300, bbox_inches='tight')
    print(f"  ✓ 保存: {output_dir}/loss_rate_comparison.png")
    plt.close()
    
    # 图4: 拓扑稳定性对比
    fig, ax = plt.subplots(figsize=(12, 6))
    fig.suptitle('Topology Stability Comparison', fontsize=16, fontweight='bold')
    
    x = np.arange(len(FORMATIONS))
    width = 0.25
    
    for idx, difficulty in enumerate(DIFFICULTIES):
        y = [results_df[(results_df['formation'] == f) & (results_df['difficulty'] == difficulty)]['topology_stability'].values[0]
             if not results_df[(results_df['formation'] == f) & (results_df['difficulty'] == difficulty)].empty else 0
             for f in FORMATIONS]
        
        colors = ['#2ecc71', '#f39c12', '#e74c3c']
        ax.bar(x + idx * width, y, width, label=difficulty, color=colors[idx], alpha=0.7, edgecolor='black')
    
    ax.set_xlabel('Formation Type')
    ax.set_ylabel('Stability (%)')
    ax.set_xticks(x + width)
    ax.set_xticklabels([f.capitalize() for f in FORMATIONS])
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'topology_stability_comparison.png'), dpi=300, bbox_inches='tight')
    print(f"  ✓ 保存: {output_dir}/topology_stability_comparison.png")
    plt.close()

def generate_summary_report(results_df, output_file):
    """生成汇总报告"""
    print("\n生成汇总报告...")
    
    with open(output_file, 'w') as f:
        f.write("="*80 + "\n")
        f.write("RTK Benchmark 性能评测汇总报告\n")
        f.write("="*80 + "\n\n")
        
        for formation in FORMATIONS:
            f.write(f"\n{'='*80}\n")
            f.write(f"{formation.upper()} Formation\n")
            f.write(f"{'='*80}\n\n")
            
            formation_data = results_df[results_df['formation'] == formation]
            
            for difficulty in DIFFICULTIES:
                diff_data = formation_data[formation_data['difficulty'] == difficulty]
                
                if diff_data.empty:
                    f.write(f"[{difficulty}] 数据不可用\n\n")
                    continue
                
                row = diff_data.iloc[0]
                
                f.write(f"[{difficulty} Mode]\n")
                f.write(f"{'-'*40}\n")
                f.write(f"  Packet Delivery Ratio:  {row['pdr']:.2f}%\n")
                f.write(f"  Avg Throughput:         {row['avg_throughput']/1e6:.2f} Mbps\n")
                f.write(f"  Total Throughput:       {row['total_throughput']/1e6:.2f} Mbps\n")
                f.write(f"  Avg Loss Rate:          {row['avg_loss_rate']:.2f}%\n")
                f.write(f"  Total Flows:            {int(row['total_flows'])}\n")
                f.write(f"  TX Packets:             {int(row['total_tx_packets'])}\n")
                f.write(f"  RX Packets:             {int(row['total_rx_packets'])}\n")
                f.write(f"  Lost Packets:           {int(row['total_lost_packets'])}\n")
                f.write(f"  Topology Stability:     {row['topology_stability']:.2f}%\n")
                f.write(f"  Avg Delay:              {row['avg_delay']:.4f}\n")
                f.write(f"  Max Delay:              {row['max_delay']:.4f}\n")
                f.write(f"  Avg Distance/Node:      {row['avg_distance_per_node']:.2f} m\n")
                f.write("\n")
        
        # 整体对比
        f.write(f"\n{'='*80}\n")
        f.write("难度级别整体对比\n")
        f.write(f"{'='*80}\n\n")
        
        for difficulty in DIFFICULTIES:
            diff_data = results_df[results_df['difficulty'] == difficulty]
            
            if not diff_data.empty:
                f.write(f"[{difficulty} Mode - 跨所有编队平均]\n")
                f.write(f"{'-'*40}\n")
                f.write(f"  Avg PDR:           {diff_data['pdr'].mean():.2f}%\n")
                f.write(f"  Avg Throughput:    {diff_data['avg_throughput'].mean()/1e6:.2f} Mbps\n")
                f.write(f"  Avg Loss Rate:     {diff_data['avg_loss_rate'].mean():.2f}%\n")
                f.write(f"  Avg Stability:     {diff_data['topology_stability'].mean():.2f}%\n")
                f.write("\n")
    
    print(f"  ✓ 保存: {output_file}")

def main():
    print("="*60)
    print("RTK Benchmark 结果分析工具")
    print("="*60)
    
    if not os.path.exists(BENCHMARK_DIR):
        print(f"\n错误: benchmark目录不存在: {BENCHMARK_DIR}")
        print("请先运行 ./run_benchmark.sh 生成数据")
        return
    
    results = []
    
    # 分析所有数据集
    print("\n分析数据集...")
    for formation in FORMATIONS:
        for difficulty in DIFFICULTIES:
            dataset_path = os.path.join(BENCHMARK_DIR, f"{formation}_{difficulty}")
            
            if os.path.exists(dataset_path):
                result = analyze_dataset(dataset_path, formation, difficulty)
                results.append(result)
            else:
                print(f"警告: 数据集不存在: {dataset_path}")
    
    if not results:
        print("\n错误: 没有找到任何数据集")
        return
    
    # 转换为DataFrame
    results_df = pd.DataFrame(results)
    
    # 保存原始数据
    csv_output = os.path.join(BENCHMARK_DIR, 'benchmark_results.csv')
    results_df.to_csv(csv_output, index=False)
    print(f"\n✓ 保存原始数据: {csv_output}")
    
    # 生成图表
    plots_dir = os.path.join(BENCHMARK_DIR, 'analysis_plots')
    generate_comparison_plots(results_df, plots_dir)
    
    # 生成汇总报告
    report_file = os.path.join(BENCHMARK_DIR, 'performance_report.txt')
    generate_summary_report(results_df, report_file)
    
    print("\n" + "="*60)
    print("分析完成！")
    print("="*60)
    print(f"\n生成的文件:")
    print(f"  - {csv_output}")
    print(f"  - {report_file}")
    print(f"  - {plots_dir}/")
    print(f"    ├── pdr_comparison.png")
    print(f"    ├── throughput_comparison.png")
    print(f"    ├── loss_rate_comparison.png")
    print(f"    └── topology_stability_comparison.png")
    print()

if __name__ == "__main__":
    main()

