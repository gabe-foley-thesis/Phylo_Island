import glob
from Bio import SearchIO
import re
import models
from bson.objectid import ObjectId


def expandStartPostion(record, hit_start, strand):
    """
    Extend a HMMER hit until we get to a full open reading frame

    Expanding leftwards on a genome, so at the start of something on the forward strand, but at the end of
    something on the backwards strand.

    So we want to return the start position if we're on the forward strand, otherwise we want to return the
    position just before the stop codon

    :param record: The genome record
    :param hit_start: Where the hit starts
    :param strand: The strand we are on
    :return:
    """

    if strand == "forward":
        codon_list = ["TGA", "TAA", "TAG"]
    elif strand == "backward":
        codon_list = ["TCA", "TTA", "CTA"]
    start_codons = ["ATG", "TTG", "GTG"]

    first_pos = hit_start
    second_pos = hit_start + 3

    start_pos = (
        first_pos
    )  # variable to keep track of all the potential start positions (methionines) we run into

    while first_pos - 3 > 0:
        codon = record.sequence[first_pos:second_pos]

        if codon in start_codons:
            start_pos = first_pos

        if codon in codon_list:
            break

        second_pos = first_pos
        first_pos = first_pos - 3

    if strand == "forward":
        if record.sequence[start_pos : start_pos + 3] in start_codons:
            return start_pos
        else:
            # Start of hmmer hit was not a start codon, so go forwards to find it

            first_pos = hit_start
            second_pos = hit_start + 3

            while first_pos + 3 < len(record.sequence):
                codon = record.sequence[first_pos:second_pos]

                if codon in start_codons:
                    return first_pos

                first_pos = second_pos
                second_pos = first_pos + 3

    else:

        return first_pos


def expandEndPosition(record, hit_end, strand):

    """
    Expanding rightwards on a genome, so at the end of something on the forward strand, but at the start of something on
     the backwards strand
    :param record: The genome record
    :param hit_end: Where the hit ended
    :param strand: The direction of the strand
    :return:
    """

    if strand == "forward":
        codon_list = ["TGA", "TAA", "TAG"]
    elif strand == "backward":
        codon_list = ["TCA", "TTA", "CTA"]

    start_codons = ["CAT", "CAA", "CAC"]

    first_pos = hit_end - 3
    second_pos = hit_end

    start_pos = (
        second_pos
    )  # Variable to keep track of all the potential start positions (methionines) we run into

    while first_pos + 3 < len(record.sequence):
        codon = record.sequence[first_pos:second_pos]
        if codon in start_codons:
            start_pos = second_pos
        if codon in codon_list:
            break
        first_pos = second_pos
        second_pos = first_pos + 3

    if strand == "forward":
        return second_pos
    else:
        if record.sequence[start_pos : start_pos + 3] in start_codons:
            return start_pos + 3
        else:

            first_pos = hit_end - 3
            second_pos = hit_end

        while first_pos - 3 > 0:
            codon = record.sequence[first_pos:second_pos]

            if codon in start_codons:
                return start_pos

            second_pos = first_pos
            first_pos = first_pos - 3


def HMMread(path, record=None, expand=False):
    """
    Read a HMMER result file and associate the hits with a genome record
    :param path: Filepath to HMMER output file
    :param record: The genome record
    :param expand: Boolean indicating whether we want to pull just the original hit or expand to open reading frame
    """
    hmm_dict = {}
    record.id

    for infile in glob.glob(path + "/*.fasta"):

        try:
            qresult = SearchIO.read(infile, "hmmer3-text")
            strand_regex = re.search(r"_.{3,4}ward_\d", infile)

            if strand_regex:
                frame = strand_regex.group()[-1]
                strand = strand_regex.group().split("_")[1]

                correction = 0
                if strand == "forward":
                    if frame == "0":
                        correction = 2
                    elif frame == "1":
                        correction = 1
                elif strand == "backward":
                    if frame == "0":
                        correction = 1
                    elif frame == "2":
                        correction = -1

            for i in range(len(qresult.hsps)):
                try:
                    hsp = qresult[0][i]

                    if strand == "forward":
                        start = ((hsp.hit_start + 1) * 3) - correction - 1
                        end = ((hsp.hit_end + 1) * 3) - correction - 1

                    # If on the backwards strand we need to update the positions to have them in correct 5' to 3'
                    elif strand == "backward":
                        start = (
                            len(record.sequence) + correction - (hsp.hit_end * 3) - 1
                        )
                        end = (
                            len(record.sequence) + correction - (hsp.hit_start * 3) - 1
                        )

                    # If we have a genome record, it means we want to pull to the start and stop codons
                    if expand:

                        # Don't want to expand region1 (the Ig-fold, so don't allow it to do so
                        if path.split("/")[-1] == "region1":
                            print("Override region1 expanding")
                            pass

                        else:

                            start = expandStartPostion(record, start, strand)
                            end = expandEndPosition(record, end, strand)

                    # After expanding, we might have the exact region already identified - don't add multiple regions in
                    if str(start) + ":" + str(end) in hmm_dict.values():
                        print(
                            "Found two identical regions, skipping adding this record %s at position %s : %s"
                            % (infile + "_" + str(i), str(start), str(end))
                        )

                    else:
                        hmm_dict[infile + "_" + str(i)] = str(start) + ":" + str(end)

                        curr = models.GenomeRecords.objects().get(id=record.id)

                        new_reg = path.split("/")[-1]
                        if expand:
                            new_reg += "_expanded"
                        new_score = str(hsp.bitscore)
                        new_start = str(start)
                        new_end = str(end)
                        object_id = ObjectId()

                        hit = models.Hits(
                            id=object_id,
                            name=record.name,
                            region=new_reg,
                            score=new_score,
                            start=new_start,
                            end=new_end,
                            expand=expand,
                        )

                        # TODO Make the hit check query better here
                        add = True
                        for hit_check in record.hits:
                            if (
                                hit_check.region == new_reg
                                and hit.start == new_start
                                and hit.end == new_end
                            ):
                                add = False

                        if add:

                            # Extract the genomic region to add to the Hit record
                            sequence = record.sequence[int(new_start) : int(new_end)]

                            hit = models.Hits(
                                id=object_id,
                                name=record.name,
                                region=new_reg,
                                score=new_score,
                                start=new_start,
                                end=new_end,
                                expand=expand,
                                strand=strand,
                                sequence=sequence,
                            )
                            curr.hits.append(hit)
                            curr.save()
                    i += 1
                except ValueError:
                    continue
        except ValueError:
            continue

    return hmm_dict
