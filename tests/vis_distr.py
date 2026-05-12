import numpy as np
import matplotlib.pyplot as plt

# 1. Load your .npy file
# Replace 'your_file.npy' with your actual filename
data = np.load('src/tests/avg_pixel_distribution.npy')

# 2. Count occurrences of each value from 0 to 100
# np.bincount works perfectly for counting non-negative integers
counts = np.bincount(data, minlength=101)

# 3. Define the x-axis range (0 to 100)
x_axis = np.arange(0, 101)

# Ensure we only plot up to index 100 if the array has larger values
y_axis = counts[:101]

# 4. Create the plot
plt.figure(figsize=(12, 6))
plt.bar(x_axis, y_axis, color='royalblue', edgecolor='black', alpha=0.8)

# Formatting the visual
plt.title('Categorical Distribution (0 - 100)', fontsize=14)
plt.xlabel('Category Value', fontsize=12)
plt.ylabel('Frequency (Count)', fontsize=12)
plt.xticks(np.arange(0, 101, 10))  # Set ticks every 10 units for readability
plt.grid(axis='y', linestyle='--', alpha=0.6)

# 5. Show the plot
plt.show()