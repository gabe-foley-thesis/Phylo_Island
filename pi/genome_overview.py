import models

def classify_genomes_original(queries):
    for query in queries:
        region_names = set([hit.region for hit in query.hits])
        print(f"\nClassifying {query.description}")
        print(f"It has the following regions {region_names}")
        if set(["TcB", "TcC"]).issubset(region_names):
            if set(["A1", "A2"]).issubset(region_names):
                if set(["Chitinase"]).issubset(region_names):
                    print(
                        "It had A1 / A2 and chitinases, so we're tagging it as Type 2A"
                    )
                    update_tag(query, "Auto_Type2A")
                else:
                    print(
                        "It had A1 / A2 but no chitinases, so we're tagging it as Type 2B"
                    )
                    update_tag(query, "Auto_Type2B")

            elif set(["TcdA1"]).issubset(region_names):
                if set("Chitinase").issubset(region_names):
                    print(
                        "It had TcdA1 but also chitinase, so we're tagging it for further investigation"
                    )
                    update_tag(query, "Auto_Unsure")

                else:
                    print("It had TcdA1 so we're classifying it as Type 1")
                    update_tag(query, "Auto_Type1")

            else:
                print(
                    "It had a TcB and TcC, but was missing either A1 or TcdA1, so we're classifying it as incomplete"
                )
                update_tag(query, "Auto_Incomplete")

        else:
            print("It was lacking a TcB and TcC, so we're classifying it as incomplete")
            update_tag(query, "Auto_Incomplete")


def classify_genomes(queries):

    for query in queries:
        region_names = set(
            [
                hit.region
                for hit in query.hits
                if "expanded" in hit.region
                if "hidden" not in hit.tags
            ]
        )

        print(f"\nClassifying {query.description}")
        print(f"It has the following regions {region_names}")

        print("Check if it should be Single or Multiple")

        allow_multi = ["Chitinase_expanded", "TcB_expanded", "TcC_expanded"]
        multi_check = [
            hit.region
            for hit in query.hits
            if "expanded" in hit.region and hit.region not in allow_multi
        ]

        print(multi_check)

        if len(multi_check) != len(set(multi_check)):
            count_check = "Multiple"
        else:
            count_check = "Single"

        # Count the number of chitinases
        chitinase_count = 0
        for hit in query.hits:
            if hit.region == "Chitinase_expanded":
                chitinase_count += 1

        # Check if there is at least one A1 and A2 that don't overlap

        a1_starts = []
        a1_ends = []
        a2_starts = []
        a2_ends = []

        if set(["A1_expanded", "A2_expanded"]).issubset(region_names):
            for hit in query.hits:
                if hit.region == "A1_expanded":
                    a1_starts.append(hit.start)
                    a1_ends.append(hit.end)

                if hit.region == "A2_expanded":
                    a2_starts.append(hit.start)
                    a2_ends.append(hit.end)

            print("Here are the A1 start positions ")
            print(a1_starts)

            print("Here are the A1 end positions")
            print(a1_ends)

            print("Here are the A2 start positions ")
            print(a2_starts)

            print("Here are the A2 end positions")
            print(a2_ends)

            start_unique = False
            end_unique = False

            for a1_start in a1_starts:
                if a1_start not in a2_starts:
                    start_unique = True

            for a2_start in a2_starts:
                if a2_start not in a1_starts:
                    start_unique = True

            for a1_end in a1_ends:
                if a1_end not in a2_ends:
                    end_unique = True

            for a2_end in a2_ends:
                if a2_end not in a1_ends:
                    end_unique = True

            if start_unique and end_unique:
                print("There is a non-overlapping A1 and A2 region")

        if set(["TcB_expanded", "TcC_expanded"]).issubset(region_names):
            if (
                set(["A1_expanded", "A2_expanded"]).issubset(region_names)
                and start_unique
                and end_unique
            ):

                # Needs to have more than one chitinase
                if (
                    set(["Chitinase_expanded"]).issubset(region_names)
                    and chitinase_count > 1
                ):
                    print(
                        "It had A1 / A2 and chitinases, so we're tagging it as Type 2A"
                    )
                    update_tag(query, count_check, "Type2a")

                    genome_tag = models.GenomeTags(
                        tag_id=query.name, tags=[count_check, "Type2a"]
                    )
                    genome_tag.save()
                else:
                    print(
                        "It had A1 / A2 but no chitinases, so we're tagging it as Type 2B"
                    )
                    update_tag(query, count_check, "Type2b")
                    genome_tag = models.GenomeTags(
                        tag_id=query.name, tags=[count_check, "Type2b"]
                    )
                    genome_tag.save()

            elif set(["TcdA1_expanded"]).issubset(region_names) or set(
                ["A2_expanded"]
            ).issubset(region_names):
                if set("Chitinase_expanded").issubset(region_names):
                    print(
                        "It had TcdA1 or A2 but also chitinase, so we're tagging it for further investigation"
                    )
                    update_tag(query, count_check, "TcdA1_w_Chitinase")
                    genome_tag = models.GenomeTags(
                        tag_id=query.name, tags=[count_check, "TcdA1_w_Chitinase"]
                    )
                    genome_tag.save()

                else:

                    for hit in query.hits:
                        if hit.region == "TcB_expanded":
                            tcB_start = hit.start
                        elif hit.region == "TcC_expanded":
                            tcC_start = hit.start

                    if tcB_start == tcC_start:
                        print(
                            "It had TcdA1 or A2 and a fused TcB / TcC so we're classifying it as "
                            "Type 3"
                        )
                        update_tag(query, count_check, "Type3")
                        genome_tag = models.GenomeTags(
                            tag_id=query.name, tags=[count_check, "Type3"]
                        )
                        genome_tag.save()
                    else:

                        print(
                            "It had TcdA1 or A2 and a split TcB / TcC so we're classifying it as Type 1"
                        )
                        update_tag(query, count_check, "Type1")
                        genome_tag = models.GenomeTags(
                            tag_id=query.name, tags=[count_check, "Type1"]
                        )
                        genome_tag.save()

            else:
                print(
                    "It had a TcB and TcC, but was missing either A1 or TcdA1, so we're classifying it as incomplete"
                )
                update_tag(query, count_check, "Incomplete")
                genome_tag = models.GenomeTags(
                    tag_id=query.name, tags=[count_check, "Incomplete"]
                )
                genome_tag.save()

        else:
            print("It was lacking a TcB or TcC, so we're classifying it as incomplete")
            update_tag(query, count_check, "Incomplete")
            genome_tag = models.GenomeTags(
                tag_id=query.name, tags=[count_check, "Incomplete"]
            )
            genome_tag.save()

        region_names = [hit.region for hit in query.hits if "expanded" in hit.region]


def delete_genome_tags(queries):
    for query in queries:
        query.update(tags=[])


def update_tag(query, *args):
    for tag in args:
        if tag not in query.tags:
            query.update(push__tags=tag)
