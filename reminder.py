import sys
import random

#[date, id]
# times = {
#     7: 0,
#     8: 0,
#     9: 0
# }

list = (7, 8, 9)
data = [[10, 7], [13, 7], [14, 8], [20, 9], [50, 7], [100, 7], [110, 8]]
const_time_weight = 100

def get_data_by_id(inp, id):
    time_intervals = []
    weights = []
    initial_time = 0
    for item in inp:
        if item[1] == id:
            time_past = item[0] - initial_time
            weights.append(time_past / const_time_weight)
            time_intervals.append(time_past)
            initial_time = item[0]

    return {
        "time_intervals": time_intervals,
        "weights": weights
        }


def calc_arr(data):
    result = []
    idx = 0
    for time in data["time_intervals"]:
        weight = int(data["weights"][idx] * 100)
        for i in range(0, weight):
          result.append(time)
        idx += 1
    
    sum = 0
    for i in result:
        sum += i

    return sum / len(result)

seven_data = get_data_by_id(data, 7)
seven_time = calc_arr(seven_data)
print(seven_time)
