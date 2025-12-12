#!/bin/bash

# RTK Benchmark 批量仿真脚本
# 运行所有飞行形态和难度级别的组合

echo "========================================"
echo "RTK Benchmark 批量仿真"
echo "========================================"
echo ""

# 定义飞行形态和难度级别
FORMATIONS=("cross" "line" "triangle" "v_formation")
DIFFICULTIES=("easy" "moderate" "hard")

# 输出目录
OUTPUT_BASE="benchmark"

# 创建输出目录
mkdir -p ${OUTPUT_BASE}

# 记录开始时间
START_TIME=$(date +%s)

# 计数器
TOTAL_SIMS=$((${#FORMATIONS[@]} * ${#DIFFICULTIES[@]}))
CURRENT=0

echo "总共需要运行 ${TOTAL_SIMS} 个仿真场景"
echo ""

# 遍历所有组合
for formation in "${FORMATIONS[@]}"; do
    for difficulty in "${DIFFICULTIES[@]}"; do
        CURRENT=$((CURRENT + 1))
        
        echo "----------------------------------------"
        echo "[${CURRENT}/${TOTAL_SIMS}] 运行: ${formation} - ${difficulty}"
        echo "----------------------------------------"
        
        # 构建轨迹文件路径
        TRAJECTORY_FILE="data_rtk/mobility_trace_${formation}.txt"
        
        # 检查轨迹文件是否存在
        if [ ! -f "${TRAJECTORY_FILE}" ]; then
            echo "警告: 轨迹文件不存在: ${TRAJECTORY_FILE}"
            echo "尝试使用默认文件: data_rtk/mobility_trace.txt"
            TRAJECTORY_FILE="data_rtk/mobility_trace.txt"
        fi
        
        if [ ! -f "${TRAJECTORY_FILE}" ]; then
            echo "错误: 找不到轨迹文件，跳过此仿真"
            continue
        fi
        
        # 运行仿真
        ./ns3 run "rtk_benchmark --trajectory=${TRAJECTORY_FILE} --outputDir=${OUTPUT_BASE} --formation=${formation} --difficulty=${difficulty}"
        
        if [ $? -eq 0 ]; then
            echo "✓ 完成: ${formation} - ${difficulty}"
        else
            echo "✗ 失败: ${formation} - ${difficulty}"
        fi
        
        echo ""
    done
done

# 计算总耗时
END_TIME=$(date +%s)
ELAPSED=$((END_TIME - START_TIME))
MINUTES=$((ELAPSED / 60))
SECONDS=$((ELAPSED % 60))

echo "========================================"
echo "所有仿真完成！"
echo "总耗时: ${MINUTES} 分 ${SECONDS} 秒"
echo "输出目录: ${OUTPUT_BASE}/"
echo "========================================"
echo ""

# 列出生成的目录
echo "生成的数据集:"
ls -lh ${OUTPUT_BASE}/

# 生成汇总报告
echo ""
echo "生成汇总报告..."
SUMMARY_FILE="${OUTPUT_BASE}/benchmark_summary.txt"

cat > ${SUMMARY_FILE} << 'EOF'
RTK Benchmark 数据集汇总
====================================

数据集结构:
benchmark/
├── cross_Easy/          # Cross 编队 - 简单模式
├── cross_Moderate/      # Cross 编队 - 中等模式
├── cross_Hard/          # Cross 编队 - 困难模式
├── line_Easy/           # Line 编队 - 简单模式
├── line_Moderate/       # Line 编队 - 中等模式
├── line_Hard/           # Line 编队 - 困难模式
├── triangle_Easy/       # Triangle 编队 - 简单模式
├── triangle_Moderate/   # Triangle 编队 - 中等模式
├── triangle_Hard/       # Triangle 编队 - 困难模式
├── v_formation_Easy/    # V-Formation 编队 - 简单模式
├── v_formation_Moderate/# V-Formation 编队 - 中等模式
└── v_formation_Hard/    # V-Formation 编队 - 困难模式

每个数据集包含:
- benchmark-config.txt     配置参数
- node-transmissions.csv   节点传输事件
- topology-changes.txt     网络拓扑变化
- node-positions.csv       节点位置轨迹
- flowmon.xml             FlowMonitor详细数据
- flow-stats.csv          流统计汇总

难度级别说明:
------------------------------------
Easy (简单):
- 理想信道条件
- 无RTK漂移
- 低业务负载
- 适合算法基础验证

Moderate (中等):
- 城市环境信道
- 周期性RTK漂移
- 中等视频流负载
- 适合鲁棒性测试

Hard (困难):
- 复杂多径衰落
- 频繁RTK漂移
- 高负载 + 共信道干扰
- 适合极端场景测试

飞行形态说明:
------------------------------------
cross:        交叉编队
line:         直线编队
triangle:     三角编队
v_formation:  V字编队

评测指标建议:
------------------------------------
- Packet Delivery Ratio (PDR)
- Average Throughput
- 95th Percentile Latency
- Jitter
- Topology Stability
- Position Tracking Accuracy

EOF

echo "生成时间: $(date)" >> ${SUMMARY_FILE}
echo ""

cat ${SUMMARY_FILE}

echo ""
echo "汇总报告已保存到: ${SUMMARY_FILE}"

