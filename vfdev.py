import numpy as np

data = [0, 0, 0, 0, 4, 4, 4, 4, 4, 4, 4, 8, 49, 50, 999]

# Calculate the mean
mean = np.mean(data)

# Calculate the absolute deviations from the mean
absolute_deviations = [abs(x - mean) for x in data]

# Calculate the mean absolute deviation
mad = np.mean(absolute_deviations)

mean, mad
print(mean)
print(mad)