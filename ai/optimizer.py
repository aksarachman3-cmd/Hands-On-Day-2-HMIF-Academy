import math
from collections import defaultdict, Counter


def compute_velocity(orders):
    """Hitung frekuensi setiap SKU."""
    return dict(Counter(o['sku'] for o in orders))


def compute_affinity(orders):
    """Hitung pasangan SKU yang sering muncul bersama."""
    affinity = defaultdict(int)
    groups = defaultdict(set)
    for o in orders:
        groups[o['order_id']].add(o['sku'])
    for skus in groups.values():
        skus = list(skus)
        for i in range(len(skus)):
            for j in range(i + 1, len(skus)):
                affinity[tuple(sorted([skus[i], skus[j]]))] += 1
    return dict(affinity)


def parse_bin_to_coord(bin_loc):
    """
    Parse bin format 'Zona-Rak-Level' menjadi koordinat 3D.
    Contoh: 'A-01-02' -> (1, 1, 2)
    Return None jika format tidak valid.
    """
    if not bin_loc or '-' not in bin_loc:
        return None
    parts = bin_loc.split('-')
    if len(parts) != 3:
        return None
    try:
        zone = ord(parts[0].upper()) - ord('A') + 1
        rack = int(parts[1])
        level = int(parts[2])
        return (zone, rack, level)
    except (ValueError, IndexError):
        return None


def euclidean(a, b):
    return math.sqrt(sum((a[i] - b[i]) ** 2 for i in range(3)))


def greedy_nearest_neighbor(start, bins):
    """Urutkan bin dengan Greedy Nearest Neighbor. Return (route, total_distance)."""
    remaining = list(bins.keys())
    current = start
    route = []
    total_distance = 0.0

    while remaining:
        nearest = min(remaining, key=lambda b: euclidean(current, bins[b]['coord']))
        total_distance += euclidean(current, bins[nearest]['coord'])
        route.append(nearest)
        current = bins[nearest]['coord']
        remaining.remove(nearest)

    return route, total_distance


def optimize_routes(orders, pickers):
    if not orders:
        raise ValueError("Tidak ada order untuk dioptimasi")

    velocity = compute_velocity(orders)
    affinity = compute_affinity(orders)

    # --- Preprocessing: validasi & parse bin ---
    valid_orders = []
    warnings = []
    for o in orders:
        coord = parse_bin_to_coord(o.get('bin_location', ''))
        if coord is None:
            warnings.append(
                f"Bin '{o.get('bin_location')}' tidak valid (harus Zona-Rak-Level, mis. A-01-02). Baris dilewati."
            )
            continue
        o['_coord'] = coord
        valid_orders.append(o)

    if not valid_orders:
        raise ValueError(
            "Digitasi lokasi bin diperlukan: tidak ada bin dengan format Zona-Rak-Level yang valid."
        )

    # --- Fallback jika order < 2 ---
    if len(valid_orders) < 2:
        valid_orders.sort(key=lambda o: o['order_id'])
        tasks = []
        for i, o in enumerate(valid_orders, 1):
            tasks.append({
                "task_id": i,
                "picker_id": pickers[0]["picker_id"],
                "order_id": o["order_id"],
                "sku": o["sku"],
                "bin_location": o["bin_location"],
                "qty": o.get("qty", 1),
                "sequence": i,
                "batch": 1,
                "status": "pending"
            })
        return {
            "tasks": tasks,
            "confidence": 0.75,
            "velocity": velocity,
            "affinity_pairs": len(affinity),
            "total_distance": 0.0,
            "warnings": warnings,
            "fallback": True
        }

    # --- Group by bin ---
    bins = defaultdict(list)
    for o in valid_orders:
        bins[o['bin_location']].append(o)

    bins_with_coord = {
        b: {"coord": items[0]['_coord'], "orders": items}
        for b, items in bins.items()
    }

    # --- Assign bins ke picker (round-robin) ---
    bin_list = list(bins_with_coord.keys())
    bins_per_picker = defaultdict(list)
    for i, bin_loc in enumerate(bin_list):
        picker_idx = i % len(pickers)
        bins_per_picker[pickers[picker_idx]["picker_id"]].append(bin_loc)

    # --- Routing + Batching ---
    tasks = []
    task_id = 1
    total_all_distance = 0.0

    for picker in pickers:
        picker_id = picker["picker_id"]
        picker_bins = bins_per_picker.get(picker_id, [])
        if not picker_bins:
            continue

        sub_bins = {b: bins_with_coord[b] for b in picker_bins}
        route, total_distance = greedy_nearest_neighbor((0, 0, 0), sub_bins)

        batch_items = []
        for bin_loc in route:
            for order in sub_bins[bin_loc]["orders"]:
                batch_items.append((bin_loc, order))

        batches = [batch_items[i:i + 5] for i in range(0, len(batch_items), 5)]

        for b_idx, b in enumerate(batches, 1):
            for bin_loc, order in b:
                tasks.append({
                    "task_id": task_id,
                    "picker_id": picker_id,
                    "order_id": order["order_id"],
                    "sku": order["sku"],
                    "bin_location": bin_loc,
                    "qty": order.get("qty", 1),
                    "sequence": task_id,
                    "batch": b_idx,
                    "status": "pending"
                })
                task_id += 1

        total_all_distance += total_distance

    # --- Confidence Score ---
    max_route_len = max(
        (len(bins_per_picker[p["picker_id"]])
         for p in pickers
         if bins_per_picker.get(p["picker_id"])),
        default=1
    )
    confidence = round(min(0.75 + 0.05 * min(max_route_len, 5), 1.0), 2)

    return {
        "tasks": tasks,
        "confidence": confidence,
        "velocity": velocity,
        "affinity_pairs": len(affinity),
        "total_distance": round(total_all_distance, 2),
        "warnings": warnings,
        "fallback": False
    }