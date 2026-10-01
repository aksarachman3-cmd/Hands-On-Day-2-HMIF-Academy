# Testing

## Scenarios Tested
| # | Skenario | Input | Expected | Result |
|---|----------|-------|----------|--------|
| 1 | Import CSV valid | input_orders.csv | 4 orders imported | ✅ |
| 2 | Optimize dengan data valid | 4 orders | Tasks + confidence > 0 | ✅ |
| 3 | Picker view tasks | picker_id=1 | Task list tampil | ✅ |
| 4 | Complete task | POST /tasks/1/complete | Status berubah | ✅ |
| 5 | Import CSV kosong | empty.csv | Error 400 | ✅ |
| 6 | Optimize tanpa data | - | Error 400 | ✅ |
| 7 | Bin location kosong | CSV tanpa bin | Error "Digitasi bin diperlukan" | ✅ |

## Edge Cases
- Single order → confidence 0.5
- All bins unique → confidence 0.0
- Duplicate SKU across orders → velocity tinggi