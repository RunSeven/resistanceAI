

mission = [3, 6, 1]
confirmed_spies = [2, 4]
spy_in_group = any([player in mission for player in confirmed_spies])

print(spy_in_group)