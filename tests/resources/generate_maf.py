import csv
import gzip
import random
import string
import sys
from typing import Dict

COLUMN_HEADERS = [
    "Hugo_Symbol",
    "Entrez_Gene_Id",
    "Center",
    "NCBI_Build",
    "Chromosome",
    "Start_Position",
    "End_Position",
    "Strand",
    "Variant_Classification",
    "Variant_Type",
    "Reference_Allele",
    "Tumor_Seq_Allele1",
    "Tumor_Seq_Allele2",
    "dbSNP_RS",
    "dbSNP_Val_Status",
    "Tumor_Sample_Barcode",
    "Matched_Norm_Sample_Barcode",
    "Match_Norm_Seq_Allele1",
    "Match_Norm_Seq_Allele2",
    "Tumor_Validation_Allele1",
    "Tumor_Validation_Allele2",
    "Match_Norm_Validation_Allele1",
    "Match_Norm_Validation_Allele2",
    "Verification_Status",
    "Validation_Status",
    "Mutation_Status",
    "Sequencing_Phase",
    "Sequence_Source",
    "Validation_Method",
    "Score",
    "BAM_File",
    "Sequencer",
    "Tumor_Sample_UUID",
    "Matched_Norm_Sample_UUID",
    "HGVSc",
    "HGVSp",
    "HGVSp_Short",
    "Transcript_ID",
    "Exon_Number",
    "t_depth",
    "t_ref_count",
    "t_alt_count",
    "n_depth",
    "n_ref_count",
    "n_alt_count",
    "all_effects",
    "Allele",
    "Gene",
    "Feature",
    "Feature_type",
    "One_Consequence",
    "Consequence",
    "cDNA_position",
    "CDS_position",
    "Protein_position",
    "Amino_acids",
    "Codons",
    "Existing_variation",
    "DISTANCE",
    "TRANSCRIPT_STRAND",
    "SYMBOL",
    "SYMBOL_SOURCE",
    "HGNC_ID",
    "BIOTYPE",
    "CANONICAL",
    "CCDS",
    "ENSP",
    "SWISSPROT",
    "TREMBL",
    "UNIPARC",
    "RefSeq",
    "SIFT",
    "PolyPhen",
    "EXON",
    "INTRON",
    "DOMAINS",
    "GMAF",
    "AFR_MAF",
    "AMR_MAF",
    "ASN_MAF",
    "EAS_MAF",
    "EUR_MAF",
    "SAS_MAF",
    "AA_MAF",
    "EA_MAF",
    "CLIN_SIG",
    "SOMATIC",
    "PUBMED",
    "MOTIF_NAME",
    "MOTIF_POS",
    "HIGH_INF_POS",
    "MOTIF_SCORE_CHANGE",
    "IMPACT",
    "PICK",
    "VARIANT_CLASS",
    "TSL",
    "HGVS_OFFSET",
    "PHENO",
    "ExAC_AF",
    "ExAC_AF_Adj",
    "ExAC_AF_AFR",
    "ExAC_AF_AMR",
    "ExAC_AF_EAS",
    "ExAC_AF_FIN",
    "ExAC_AF_NFE",
    "ExAC_AF_OTH",
    "ExAC_AF_SAS",
    "nontcga_ExAC_AF",
    "nontcga_ExAC_AF_Adj",
    "nontcga_ExAC_AF_AFR",
    "nontcga_ExAC_AF_AMR",
    "nontcga_ExAC_AF_EAS",
    "nontcga_ExAC_AF_FIN",
    "nontcga_ExAC_AF_NFE",
    "nontcga_ExAC_AF_OTH",
    "nontcga_ExAC_AF_SAS",
    "GENE_PHENO",
    "CONTEXT",
    "tumor_bam_uuid",
    "normal_bam_uuid",
    "case_id",
    "GDC_FILTER",
    "COSMIC",
    "hotspot",
    "callers",
]


def generate_maf(filename: str, count: int):
    with gzip.open(filename, mode="wt") as writer:
        write_file_header(writer)
        write_body(writer, count)


def write_file_header(writer):
    writer.writelines(
        [
            f"#version gdc-1.0.0\n",
            f"#annotation.spec gdc-1.0.0-aliquot-merged-masked\n",
            f"#contigs chr1,chr2,chr3,chr4,chr5,chr6,chr7,chr8,chr9,chr10,chr11\n",
            f"#sort.order BarcodesAndCoordinate\n",
            f"#filedate 20200315\n",
            f"#normal.aliquot {random_value(32)}\n",
            f"#tumor.aliquot {random_value(32)}\n",
        ]
    )


def write_body(writer, count):
    tsv = csv.DictWriter(writer, COLUMN_HEADERS, dialect=csv.excel_tab)
    tsv.writeheader()
    for _ in range(count):
        tsv.writerow(generate_row())


def generate_row() -> Dict[str, str]:
    def value():
        return random_value(random.randint(1, 10))  # nosec

    return {column: value() for column in COLUMN_HEADERS}


def random_value(length) -> str:
    return "".join(random.choices(string.ascii_letters, k=length))  # nosec


if __name__ == "__main__":
    # filename, number of entries
    generate_maf(sys.argv[1], int(sys.argv[2]))
