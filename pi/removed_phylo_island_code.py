## REMOVED FROM getGenomes.py
def read_genome(outpath, species_name):

    # Collate all of the nucleotide records together to make the genome
    concatenated_genome = ""

    my_dict = SeqIO.to_dict(SeqIO.parse(outpath, "fasta"))
    for r in sorted(my_dict.values(), key=operator.attrgetter("id")):

        concatenated_genome += str(r.seq)
        description = r.description
        genome_id = r.id

        # if r.id == "NZ_NIBS01000003.1":
        #     print (concatenated_genome)

        # if "plasmid" not in r.description:
        #     print ('Was not a plasmid')
        #     print (r.description)
        #     # concatenated_genome += str(r.seq)
        #     # description = r.description
        #     # genome_id = r.id
        #
        # else:
        #     # print ('Was a plasmid')
        #     # print (r.description)

        # Temporary measure to reduce the name so it can fit in the database. Edge case but occurs with
        # 'bacterium endosymbiont of Mortierella elongata FMR23-6', for example

        if len(species_name) > 40:
            species_name = species_name[0:40]

    return SeqRecord(
        Seq(concatenated_genome),
        id=genome_id,
        name=species_name,
        description=description,
        annotations={
            "organism": species_name,
            "source": "",
            "plasmid": True if "plasmid" in description else False,
        },
    )

## REMOVED FROM genome_overview.py
def write_hits_to_gb(hmm_dict, reference, seqrecord, query_id, species, expand=False):

    print("writing to genbank")
    print("and reference is ")
    print(reference)
    name = species + "_sequence"
    name += "_expanded" if expand else ""
    output_path = reference + "/" + name + ".gb"

    output_path = output_path.replace(" ", "_")
    print(name)
    print(reference)
    print("and species name is", species)
    seqrecord.name = species[0:9].zfill(9).replace(" ", "_")

    print(seqrecord.name)

    # Write Annotated Sequences to Genbank files to allow easy movement to Artemis
    print("Writing sequences to GenBank File")
    """ Create a dictionary for key = feature type -> value = location """
    locs = {}
    strand_dict = {}
    colour_dict = {
        "A1": "255 165 0",
        "A2": "255 0 0",
        "TcdA1": "255 255 0",
        "TcB": "0 0 255",
        "TcC": "255 0 255",
        "Chitinase": "0 255 0",
        "region1": "0 255 255",
        "region2": "255 153 255",
        "region3": "204 0 102",
        "region4": "0 0 0",
    }
    for result in hmm_dict:
        print(result)
        i = 0
        for reg in result:
            """ Create a dictionary for key = feature type -> value = location """
            if "forward" in reg:
                location = reg.split("/")[3] + utilities.randstring(5)
                locs[location] = result[reg].split(":")
                strandd = 1
                strand_dict[location] = strandd

            elif "backward" in reg:

                strandd = -1

                location = reg.split("/")[3] + utilities.randstring(5)
                locs[location] = result[reg].split(":")
                strand_dict[location] = strandd

            i += 1

    print("Adding %s genome to diagram" % (seqrecord.name))

    seqrecord.features = []
    for location in locs:
        """ create and add features based on locations """
        color = {"color": colour_dict[location[0:-5]]}
        feature = SeqFeature(
            location=FeatureLocation(
                int(locs[location][0]),
                int(locs[location][1]),
                strand=strand_dict[location],
            ),
            type=location[0:-5],
            qualifiers=color,
        )
        seqrecord.features.append(feature)

        # add_hit_to_database(query_id = query_id, species=species, region=location[0:-5], start=int(locs[location][0]), \
        #                                                                             end=int(locs[
        #                                                                                                       location][
        #                                                                                                       1]),
        #                     expand=expand)

    # sequence = str(seqrecord)[2:-1]
    # seqrecord.seq = Seq(sequence, generic_dna)
    SeqIO.write(seqrecord, output_path, "genbank")