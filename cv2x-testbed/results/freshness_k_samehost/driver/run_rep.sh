#!/bin/bash
# usage: run_rep.sh <rep> <mode> <order_index>
set -u
REP=$1; MODE=$2; ORD=$3
WT=/home/user/CVIN-SC-Implementation-SSI-DID/.claude/worktrees/agent-a04761ffa1dab2915
BI=/home/user/CVIN-SC-Implementation-SSI-DID/1_blockchain-identity
PORT=8562
OUTDIR=$WT/cv2x-testbed/results/freshness_k_samehost
NAME=r${REP}_${MODE}
S=/tmp/hk_scratch/$NAME
mkdir -p $S $OUTDIR
RPC='{"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]}'
if curl -s -m 2 -X POST -H 'content-type: application/json' --data "$RPC" http://127.0.0.1:$PORT >/dev/null; then
  echo "port $PORT busy"; exit 1
fi
python3 /tmp/hk_scratch/gate.py | tee $S/gate.txt
cd $BI
setsid ./node_modules/.bin/hardhat node --port $PORT > $S/node.log 2>&1 &
NODE_PID=$!
echo "node pid $NODE_PID"
for i in $(seq 1 60); do
  if curl -s -m 2 -X POST -H 'content-type: application/json' --data "$RPC" http://127.0.0.1:$PORT | grep -q '"result":"0x0"'; then break; fi
  sleep 1
done
echo "block: $(curl -s -X POST -H 'content-type: application/json' --data "$RPC" http://127.0.0.1:$PORT)"
L0=$(cat /proc/loadavg); T0=$(date -u +%FT%TZ)
python3 /tmp/hk_scratch/sampler.py $S/load_samples.txt &
SAMP=$!
cd $WT/cv2x-testbed
python3 scripts/experiment_freshness_k.py --rpc-url http://127.0.0.1:$PORT --deploy --rotation \
   --refresh-mode $MODE --n 250 --warmup 3 --ks 1,5,25,inf --out-dir $OUTDIR --out-name $NAME > $S/run.log 2>&1
RC=$?
L1=$(cat /proc/loadavg); T1=$(date -u +%FT%TZ)
kill $SAMP
kill -- -$NODE_PID 2>/dev/null || kill $NODE_PID
sleep 2
if curl -s -m 2 -X POST -H 'content-type: application/json' --data "$RPC" http://127.0.0.1:$PORT >/dev/null; then
  echo "WARNING node still on $PORT"
fi
python3 /tmp/hk_scratch/write_load.py "$OUTDIR/$NAME.load.json" "$REP" "$MODE" "$ORD" "$T0" "$L0" "$T1" "$L1" "$S/load_samples.txt" "$RC"
tail -30 $S/run.log
exit $RC
