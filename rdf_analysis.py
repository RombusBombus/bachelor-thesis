import pandas as pd
import matplotlib.pyplot as plt

species_pairs = [
    ("Ta", "N"),
    ("Cu", "N")
]

for species1, species2 in species_pairs:

    # ----------------------------------
    # Parsing the RDF data from the text file for our own trajectory
    # ----------------------------------

    with open(f"/home/nico/MD_trajectories/own/temp_300.0/rdf/rdf_{species1}-{species2}.txt", "r") as f:
        lines = f.readlines()

        data = {
            "bin": [],
            "r": [],
            "g(r)": [],
            "coordination_number": [],
        }
        
        for line in lines[4:]:
            columns = line.split(" ")
            data["bin"].append(float(columns[0]))
            data["r"].append(float(columns[1]))
            data["g(r)"].append(float(columns[2]))
            data["coordination_number"].append(float(columns[3]))
        
    df = pd.DataFrame(data)

    df.plot(x="r", y="g(r)", kind="line", title="Radial Distribution Function", xlabel="Distance (r)", ylabel="g(r)")

    plt.show()

    print(df.head())

    # ----------------------------------
    # Parsing the RDF data from the AIMD trajectory
    # (contains r and g(r) values for each frame as columns)
    # ----------------------------------

    path = f"/home/nico/bachelor-thesis/rdf_results/XDATCAR_300_{species1}-{species2}_RDF.dat"

    with open(path, "r") as f:
        lines = f.readlines()

        data = {
            "r": [],
            "g(r)": [],
        }
        
        for line in lines[1:]:
            columns = line.split(" ")
            data["r"].append(float(columns[0]))
            data["g(r)"].append(float(columns[1]))

    df_aimd = pd.DataFrame(data)

    df_aimd.plot(x="r", y="g(r)", kind="line", title="Radial Distribution Function (AIMD)", xlabel="Distance (r)", ylabel="g(r)")


    # ----------------------------------
    # Plot the two RDFs together for comparison
    # ----------------------------------

    plt.figure(figsize=(8, 6))
    plt.plot(df["r"], df["g(r)"], label="Own Trajectory RDF", lw=2)
    plt.plot(df_aimd["r"], df_aimd["g(r)"], label="AIMD RDF", lw=2)
    plt.title("Comparison of Radial Distribution Functions")
    plt.xlabel("Distance (r)")
    plt.ylabel("g(r)")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.show()