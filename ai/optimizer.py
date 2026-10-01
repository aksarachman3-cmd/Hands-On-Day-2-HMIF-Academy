from collections import defaultdict

def optimize_routes(orders, pickers):
    if any(not o.get('bin_location') for o in orders):
        raise ValueError("Digitasi bin diperlukan")

    bins = defaultdict(list)
    for o in orders:
        bins[o['bin_location']].append(o)

    sorted_bins = sorted(bins.keys())

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
                    "sequence": task_id,
                    "status": "pending"
                })
                task_id += 1

    confidence = 0.75
    return {"tasks": tasks, "confidence": confidence}