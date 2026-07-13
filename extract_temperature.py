#!/usr/bin/env python3

import glob
import re
import numpy as np
import matplotlib.pyplot as plt


# -----------------------------
# Settings
# -----------------------------

outcar_files = sorted(
    glob.glob("/home/nico/MD_trajectories/520/outcar_*")
)

temperature = []


# -----------------------------
# Parse OUTCAR files
# -----------------------------

print("Files:")
for f in outcar_files:
    print(" ", f)


# -----------------------------
# Extract temperatures
# -----------------------------

temperature = []
segment = []

for i, filename in enumerate(outcar_files):

    print("Reading", filename)

    with open(filename, "r") as f:

        for line in f:

            if "temperature" in line:

                match = re.search(
                    r"temperature\s+([0-9.]+)",
                    line
                )

                if match:
                    temperature.append(
                        float(match.group(1))
                    )

                    # keep track of which OUTCAR segment
                    segment.append(i+1)


temperature = np.array(temperature)
segment = np.array(segment)


print()
print("Number of MD steps:", len(temperature))
print("Average temperature: %.2f K" %
      np.mean(temperature))

print("Temperature standard deviation: %.2f K" %
      np.std(temperature))


# -----------------------------
# Plot temperature
# -----------------------------

plt.figure(figsize=(9,4))

plt.plot(
    temperature,
    linewidth=1
)

plt.xlabel("MD step")
plt.ylabel("Temperature (K)")

plt.tight_layout()
plt.savefig(
    "temperature_vs_time.png",
    dpi=300
)

plt.show()


# -----------------------------
# Plot with segment boundaries
# -----------------------------

plt.figure(figsize=(9,4))

plt.plot(
    temperature
)

for s in np.unique(segment):

    idx = np.where(segment == s)[0][0]

    plt.axvline(
        idx,
        linestyle="--"
    )

plt.xlabel("MD step")
plt.ylabel("Temperature (K)")
plt.title("Temperature with OUTCAR segment boundaries")

plt.tight_layout()
plt.savefig(
    "temperature_segments.png",
    dpi=300
)

plt.show()