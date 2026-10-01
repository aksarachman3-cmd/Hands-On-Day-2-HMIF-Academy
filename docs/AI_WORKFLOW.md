# AI Workflow

## Approach
Heuristic batching + routing based on SKU velocity and affinity.

## Pipeline
1. **Input**: orders list + pickers list
2. **Preprocessing**: validate bin_location, build velocity & affinity maps
3. **Inference**:
   - Group orders by bin
   - Sort bins by total SKU velocity
   - Assign bins to pickers round-robin
4. **Postprocessing**: format tasks, compute confidence
5. **Confidence Score**: ratio of bins with >1 order (batched) / total bins
6. **Failure Conditions**:
   - Empty orders → error
   - Missing bin_location → error
   - Single order only → confidence 0.5 (low)

## Why Heuristic, Not ML
Given a 4-hour build constraint and demo-only scope, a deterministic heuristic provides:
- Predictable output
- No training data required
- Explainable decisions
- Fast inference (< 100ms)

Future improvement: replace with OR-Tools VRP or reinforcement learning.