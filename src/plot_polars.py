import csv
import matplotlib.pyplot as plt

# Read the list of CSV files to compare
polars_list = "polars_list.txt"
with open(polars_list, 'r') as file:
        lines = file.readlines()
csv_files = []
cases_names = []
name = False
for line in lines:
    line=line.strip()
    if line.startswith("###") and not name:
        name = True
        continue
    if line.startswith("###") and name:
        name = False
        continue
    if name:
        csv_files.append(line)
        cases_names.append(line.removesuffix(".csv"))
print(csv_files)

labels = cases_names
colors = ['b', 'r', 'g','c']  # Colors for each CSV file
markers = ['o', 's', '^','o']  # Markers for each CSV file

plt.figure(figsize=(12, 10))

# Initialize subplots
plt.subplot(2, 2, 1)
plt.xlabel('Alpha (degrees)')
plt.ylabel('Cl')
plt.title('Cl vs Alpha')
plt.grid(True)

plt.subplot(2, 2, 2)
plt.xlabel('Alpha (degrees)')
plt.ylabel('Cd')
plt.title('Cd vs Alpha')
plt.grid(True)

plt.subplot(2, 2, 3)
plt.xlabel('Alpha (degrees)')
plt.ylabel('Cm')
plt.title('Cm vs Alpha')
plt.grid(True)

plt.subplot(2, 2, 4)
plt.xlabel('Cd')
plt.ylabel('Cl')
plt.title('Cl vs Cd')
plt.grid(True)

# Plotting the polars from each csv file
for i, csv_file in enumerate(csv_files):
    alpha_values = []
    Cl_values = []
    Cd_values = []
    Cm_values = []

    with open(csv_file, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            alpha_values.append(float(row['Alpha']))  # Assuming 'Alpha' column exists
            Cl_values.append(float(row['Cl']))
            Cd_values.append(float(row['Cd']))
            Cm_values.append(float(row['Cm']))

    # Plot each CSV file with different color and marker
    plt.subplot(2, 2, 1)
    plt.plot(alpha_values, Cl_values, color=colors[i], marker=markers[i], linestyle='-', label=labels[i])

    plt.subplot(2, 2, 2)
    plt.plot(alpha_values, Cd_values, color=colors[i], marker=markers[i], linestyle='-', label=labels[i])

    plt.subplot(2, 2, 3)
    plt.plot(alpha_values, Cm_values, color=colors[i], marker=markers[i], linestyle='-', label=labels[i])

    plt.subplot(2, 2, 4)
    plt.plot(Cd_values, Cl_values, color=colors[i], marker=markers[i], linestyle='-', label=labels[i])

# Adding legends
plt.subplot(2, 2, 1)
plt.legend()

plt.subplot(2, 2, 2)
plt.legend()

plt.subplot(2, 2, 3)
plt.legend()

plt.subplot(2, 2, 4)
plt.legend()

plt.tight_layout()
plt.show()
