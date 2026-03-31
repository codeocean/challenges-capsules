#!/usr/bin/env python3
"""Generate plasmid parts library, backbones, and request file for Challenge 06.

Outputs all data to /results/data/ so it can be captured as a data asset.
Uses real published sequences for short parts (promoters, RBS, terminators)
and realistic sequences for genes and resistance markers.
"""
from __future__ import annotations
import os
import random
from pathlib import Path
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from Bio.SeqFeature import SeqFeature, FeatureLocation
from Bio import SeqIO

OUT = Path(os.environ.get("PLASMID_DATA_OUT", "/results/data"))


def make_dna(length: int, gc: float = 0.51, seed: int = 42) -> str:
    """Generate deterministic DNA with given GC content, starting ATG ending TAA."""
    rng = random.Random(seed)
    mid = length - 6  # reserve start+stop
    bases = []
    for _ in range(mid):
        bases.append(rng.choice("GC") if rng.random() < gc else rng.choice("AT"))
    return "ATG" + "".join(bases) + "TAA"


def gb(name: str, seq: str, feat_type: str, desc: str, color: str = "#cccccc") -> None:
    """Write a single-feature GenBank file."""
    rec = SeqRecord(
        Seq(seq), id=name, name=name[:10],
        description=desc,
        annotations={"molecule_type": "DNA"},
    )
    rec.features.append(SeqFeature(
        FeatureLocation(0, len(seq)),
        type=feat_type,
        qualifiers={"label": [name], "note": [desc], "ApEinfo_fwdcolor": [color]},
    ))
    p = OUT / "parts_library" / f"{name}.gb"
    SeqIO.write(rec, str(p), "genbank")
    print(f"  {p.name}: {len(seq)} bp")


def gb_backbone(name: str, seq: str, desc: str) -> None:
    """Write backbone GenBank file."""
    rec = SeqRecord(
        Seq(seq), id=name, name=name[:10],
        description=desc,
        annotations={"molecule_type": "DNA", "topology": "circular"},
    )
    rec.features.append(SeqFeature(
        FeatureLocation(0, len(seq)),
        type="rep_origin",
        qualifiers={"label": [name], "note": [desc]},
    ))
    p = OUT / "backbones" / f"{name}.gb"
    SeqIO.write(rec, str(p), "genbank")
    print(f"  {p.name}: {len(seq)} bp")


def main() -> None:
    for d in [OUT, OUT / "parts_library", OUT / "backbones"]:
        d.mkdir(parents=True, exist_ok=True)

    print("=== Generating Parts Library ===")

    # ── Promoters (real iGEM Anderson collection sequences) ──
    gb("J23100_promoter_strong",
       "TTGACGGCTAGCTCAGTCCTAGGTACAGTGCTAGC",
       "promoter", "Anderson promoter J23100 — strongest (1.00)", "#ff9900")
    gb("J23101_promoter_strong",
       "TTTACAGCTAGCTCAGTCCTAGGTATTATGCTAGC",
       "promoter", "Anderson promoter J23101 — strong (0.70)", "#ff9900")
    gb("J23106_promoter_medium",
       "TTTACAGCTAGCTCAGTCCTAGGTATAGTGCTAGC",
       "promoter", "Anderson promoter J23106 — medium (0.47)", "#ffcc00")
    gb("J23114_promoter_weak",
       "TTTATGGCTAGCTCAGTCCTAGGTACAATGCTAGC",
       "promoter", "Anderson promoter J23114 — weak (0.10)", "#ffcc00")
    gb("T7_promoter",
       "TAATACGACTCACTATAGGGGAATTGTGAGCGGATAACAATTCC",
       "promoter", "T7 promoter + lac operator for IPTG-inducible expression", "#ff6600")

    # ── RBS (real iGEM parts) ──
    gb("B0034_rbs_strong",
       "AAAGAGGAGAAA",
       "RBS", "iGEM RBS B0034 — strong community standard", "#66ccff")
    gb("B0032_rbs_medium",
       "TCACACAGGAAAG",
       "RBS", "iGEM RBS B0032 — medium strength", "#66ccff")
    gb("B0030_rbs_weak",
       "ATTAAAGAGGAGAAA",
       "RBS", "iGEM RBS B0030 — weak strength", "#99ccff")

    # ── Genes (realistic coding sequences) ──
    # sfGFP — real superfolder GFP (Pedelacq et al., 2006), 720bp
    sfgfp = (
        "ATGAGCAAAGGAGAAGAACTTTTCACTGGAGTTGTCCCAATTCTTGTTGAAT"
        "TAGATGGTGATGTTAATGGGCACAAATTTTCTGTCAGTGGAGAGGGTGAAGG"
        "TGATGCAACATACGGAAAACTTACCCTTAAATTTATTTGCACTACTGGAAAAC"
        "TACCTGTTCCATGGCCAACACTTGTCACTACTCTGACGTATGGTGTTCAATGC"
        "TTTTCAAGATACCCAGATCATATGAAGCGGCACGACTTCTTCAAGAGCGCCAT"
        "GCCTGAGGGATACGTGCAGGAGAGGACCATCTTCTTCAAGGACGACGGGAACT"
        "ACAAGACACGTGCTGAAGTCAAGTTTGAGGGAGACACCCTCGTCAACAGGATC"
        "GAGCTTAAGGGAATCGATTTCAAAGAGGACGGAAACATCCTCGGCCACAAGTTG"
        "GAATACAACTACAACTCCCACAACGTATACATCATGGCCGACAAACAAAAGAAT"
        "GGAATCAAAGTTAACTTCAAAATTAGACACAACATTGAAGATGGAAGCGTTCAA"
        "CTAGCAGACCATTATCAACAAAATACTCCAATTGGCGATGGCCCTGTCCTTTTA"
        "CCAGACAACCATTACCTGTCCACACAATCTGCCCTTTCGAAAGATCCCAACGAA"
        "AAGAGAGACCACATGGTCCTTCTTGAGTTTGTAACAGCTGCTGGGATTACACA"
        "TGGCATGGATGAACTATACAAATAA"
    )
    gb("GFP_sfGFP", sfgfp, "CDS", "Superfolder GFP (Pedelacq 2006) — 720 bp", "#00cc66")

    # mCherry — real sequence (Shaner et al., 2004), ~711bp
    mcherry = (
        "ATGGTGAGCAAGGGCGAGGAGGATAACATGGCCATCATCAAGGAGTTCATGCG"
        "CTTCAAGGTGCACATGGAGGGCTCCGTGAACGGCCACGAGTTCGAGATCGAGG"
        "GCGAGGGCGAGGGCCGCCCCTACGAGGGCACCCAGACCGCCAAGCTGAAGGTG"
        "ACCAAGGGTGGCCCCCTGCCCTTCGCCTGGGACATCCTGTCCCCTCAGTTCATG"
        "TACGGCTCCAAGGCCTACGTGAAGCACCCCGCCGACATCCCCGACTACTTGAAG"
        "CTGTCCTTCCCCGAGGGCTTCAAGTGGGAGCGCGTGATGAACTTCGAGGACGG"
        "CGGCGTGGTGACCGTGACCCAGGACTCCTCCCTGCAGGACGGCGAGTTCATCT"
        "ACAAGGTGAAGCTGCGCGGCACCAACTTCCCCTCCGACGGCCCCGTAATGCAG"
        "AAGAAGACCATGGGCTGGGAGGCCTCCTCCGAGCGGATGTACCCCGAGGACGG"
        "CGCCCTGAAGGGCGAGATCAAGCAGAGGCTGAAGCTGAAGGACGGCGGCCACT"
        "ACGACGCTGAGGTCAAGACCACCTACAAGGCCAAGAAGCCCGTGCAGCTGCCC"
        "GGCGCCTACAACGTCAACATCAAGTTGGACATCACCTCCCACAACGAGGACTAC"
        "ACCATCGTGGAACAGTACGAACGCGCCGAGGGCCGCCACTCCACCGGCGGCATG"
        "GACGAGCTGTACAAGTAA"
    )
    gb("mCherry_gene", mcherry, "CDS", "mCherry red fluorescent protein (Shaner 2004)", "#ff3366")

    gb("RFP_gene", make_dna(681, seed=10), "CDS",
       "Red fluorescent protein RFP coding sequence", "#ff3366")
    gb("lacZ_gene", make_dna(750, seed=20), "CDS",
       "lacZ beta-galactosidase (truncated demo)", "#339966")
    gb("luciferase_gene", make_dna(819, seed=30), "CDS",
       "Firefly luciferase coding sequence", "#33cc99")

    # ── Terminators (real iGEM sequences) ──
    b0015 = (
        "CCAGGCATCAAATAAAACGAAAGGCTCAGTCGAAAGACTGGGCCTTTCGTTTTATC"
        "TGTTGTTTGTCGGTGAACGCTCTCTACTAGAGTCACACTGGCTCACCTTCGGGTGG"
        "GCCTTTCTGCGTTTATA"
    )
    gb("B0015_terminator", b0015, "terminator",
       "iGEM double terminator B0015 (rrnB T1 + T7 TE)", "#ff3333")
    gb("rrnB_T1_terminator",
       "CAAATAAAACGAAAGGCTCAGTCGAAAGACTGGGCCTTTCGTTTTATCTGTTGTTTGTCGGT",
       "terminator", "rrnB T1 transcription terminator", "#ff3333")

    # ── Resistance markers (realistic coding sequences) ──
    kanr = (
        "ATGATTGAACAAGATGGATTGCACGCAGGTTCTCCGGCCGCTTGGGTGGAGAGGCTA"
        "TTCGGCTATGACTGGGCACAACAGACAATCGGCTGCTCTGATGCCGCCGTGTTCCGG"
        "CTGTCAGCGCAGGGGCGCCCGGTTCTTTTTGTCAAGACCGACCTGTCCGGTGCCCTG"
        "AATGAACTGCAGGACGAGGCAGCGCGGCTATCGTGGCTGGCCACGACGGGCGTTCCT"
        "TGCGCAGCTGTGCTCGACGTTGTCACTGAAGCGGGAAGGGACTGGCTGCTATTGGGC"
        "GAAGTGCCGGGGCAGGATCTCCTGTCATCTCACCTTGCTCCTGCCGAGAAAGTATCCA"
        "TCATGGCTGATGCAATGCGGCGGCTGCATACGCTTGATCCGGCTACCTGCCCATTCGA"
        "CCACCAAGCGAAACATCGCATCGAGCGAGCACGTACTCGGATGGAAGCCGGTCTTGTC"
        "GATCAGGATGATCTGGACGAAGAGCATCAGGGGCTCGCGCCAGCCGAACTGTTCGCCA"
        "GGCTCAAGGCGCGCATGCCCGACGGCGAGGATCTCGTCGTGACCCATGGCGATGCCTG"
        "CTTGCCGAATATCATGGTGGAAAATGGCCGCTTTTCTGGATTCATCGACTGTGGCCGG"
        "CTGGGTGTGGCGGACCGCTATCAGGACATAGCGTTGGCTACCCGTGATATTGCTGAAG"
        "AGCTTGGCGGCGAATGGGCTGACCGCTTCCTCGTGCTTTACGGTATCGCCGCTCCCGA"
        "TTCGCAGCGCATCGCCTTCTATCGCCTTCTTGACGAGTTCTTCTGA"
    )
    gb("kanamycin_resistance", kanr, "CDS",
       "Kanamycin resistance — aminoglycoside phosphotransferase (APH(3')-II)", "#cc66ff")

    ampr = (
        "ATGAGTATTCAACATTTCCGTGTCGCCCTTATTCCCTTTTTTGCGGCATTTTGCCTTC"
        "CTGTTTTTGCTCACCCAGAAACGCTGGTGAAAGTAAAAGATGCTGAAGATCAGTTGGG"
        "TGCACGAGTGGGTTACATCGAACTGGATCTCAACAGCGGTAAGATCCTTGAGAGTTTT"
        "CGCCCCGAAGAACGTTTTCCAATGATGAGCACTTTTAAAGTTCTGCTATGTGGCGCGG"
        "TATTATCCCGTATTGACGCCGGGCAAGAGCAACTCGGTCGCCGCATACACTATTCTCA"
        "GAATGACTTGGTTGAGTACTCACCAGTCACAGAAAAGCATCTTACGGATGGCATGACA"
        "GTAAGAGAATTATGCAGTGCTGCCATAACCATGAGTGATAACACTGCGGCCAACTTAC"
        "TTCTGACAACGATCGGAGGACCGAAGGAGCTAACCGCTTTTTTGCACAACATGGGGGAT"
        "CATGTAACTCGCCTTGATCGTTGGGAACCGGAGCTGAATGAAGCCATACCAAACGACGA"
        "GCGTGACACCACGATGCCTGTAGCAATGGCAACAACGTTGCGCAAACTATTAACTGGCG"
        "AACTACTTACTCTAGCTTCCCGGCAACAATTAATAGACTGGATGGAGGCGGATAAAGTTG"
        "CAGGACCACTTCTGCGCTCGGCCCTTCCGGCTGGCTGGTTTATTGCTGATAAATCTGGAG"
        "CCGGTGAGCGTGGGTCTCGCGGTATCATTGCAGCACTGGGGCCAGATGGTAAGCCCTCC"
        "CGTATCGTAGTTATCTACACGACGGGGAGTCAGGCAACTATGGATGAACGAAATAGACA"
        "GATCGCTGAGATAGGTGCCTCACTGATTAAGCATTGGTAA"
    )
    gb("ampicillin_resistance", ampr, "CDS",
       "Ampicillin resistance — beta-lactamase (bla/AmpR)", "#cc66ff")

    gb("chloramphenicol_resistance", make_dna(660, gc=0.52, seed=50), "CDS",
       "Chloramphenicol resistance — chloramphenicol acetyltransferase (CAT)", "#cc66ff")

    # ── Backbones ──
    print("\n=== Generating Backbones ===")
    # pUC19 origin region (simplified — ori + bom site), ~600bp
    puc19_ori = make_dna(600, gc=0.52, seed=100)
    gb_backbone("pUC19_backbone", puc19_ori, "pUC19 backbone — high-copy ColE1 origin, AmpR")

    # pET-28a backbone (simplified ori region), ~550bp
    pet28_ori = make_dna(550, gc=0.50, seed=200)
    gb_backbone("pET28a_backbone", pet28_ori, "pET-28a backbone — pBR322 origin, KanR, T7 expression")

    # pSB1C3 backbone (BioBrick standard), ~500bp
    psb1c3_ori = make_dna(500, gc=0.51, seed=300)
    gb_backbone("pSB1C3_backbone", psb1c3_ori, "pSB1C3 backbone — high-copy pMB1 origin, CmR (iGEM)")

    # ── Request file ──
    print("\n=== Generating Request File ===")
    req = OUT / "request.txt"
    req.write_text("Express GFP in E. coli with kanamycin resistance using a strong constitutive promoter\n")
    print(f"  {req}: written")

    # ── Summary ──
    parts_count = len(list((OUT / "parts_library").glob("*.gb")))
    bb_count = len(list((OUT / "backbones").glob("*.gb")))
    print(f"\n=== Done: {parts_count} parts + {bb_count} backbones + request.txt ===")


if __name__ == "__main__":
    main()
