# Compare across all formations and difficulties
./ns3 run "rtk_benchmark --formation=line --difficulty=moderate --maxTime=30"
./ns3 run "rtk_benchmark --formation=v_formation --difficulty=hard --maxTime=30"

# Or use the batch script for full benchmark suite
bash run_benchmark.sh