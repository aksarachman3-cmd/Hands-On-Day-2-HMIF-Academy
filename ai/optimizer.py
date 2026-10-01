from collections import defaultdict, Counter

def compute_velocity(orders):
    """Hitung frekuensi setiap SKU (SKU velocity)."""
    counter = Counter(o['sku'] for o in orders)
    return dict(counter)

def compute_affinity(orders):
    """Hitung pasangan SKU yang sering muncul bersama (SKU affinity)."""
    affinity = defaultdict(int)
    order_groups = defaultdict(set)
    for o in orders:
        order_groups[o['order_id']].add(o['sku'])
    for skus in order_groups.values():
        skus = list(skus)
        for i in range(len(skus)):
            for j in range(i + 1, len(skus)):
                pair = tuple(sorted([skus[i], skus[j]]))
                affinity[pair] += 1
    return dict(affinity)

def optimize_routes(orders, pickers):
    if not orders:
        raise ValueError("Tidak ada order untuk dioptimasi")
    if any(not o.get('bin_location') for o in orders):
        raise ValueError("Digitasi bin diperlukan: ada order tanpa bin_location")

    # 1. Hitung velocity & affinity
    velocity = compute_velocity(orders)
    affinity = compute_affinity(orders)

    # 2. Group orders by bin
    bins = defaultdict(list)
    for o in orders:
        bins[o['bin_location']].append(o)

    # 3. Sort bin berdasarkan total velocity
    def bin_velocity(bin_loc):
        return sum(velocity.get(o['sku'], 0) for o in bins[bin_loc])
    sorted_bins = sorted(bins.keys(), key=bin_velocity, reverse=True)

    # 4. Assign ke picker (round-robin)
    tasks = []
    task_id = 1
    for i, picker in enumerate(pickers):
        for bin_loc in sorted_bins[i::len(pickers)]:
            for order in bins[bin_loc]:
                tasks.append({
                    "task_id": task_id,
                    "picker_id": picker["picker_id"],
                    "order_id": order["order_id"],
                    "sku": order["sku"],
                    "bin_location": bin_loc,
                    "qty": order.get("qty", 1),
                    "sequence": task_id,
                    "status": "pending"
                })
                task_id += 1

    # 5. Confidence dinamis
    batched = sum(1 for b in bins.values() if len(b) > 1)
    total_bins = len(bins)
    confidence = round(batched / total_bins, 2) if total_bins else 0.5

    return {
        "tasks": tasks,
        "confidence": confidence,
        "velocity": velocity,
        "affinity_pairs": len(affinity)
    }