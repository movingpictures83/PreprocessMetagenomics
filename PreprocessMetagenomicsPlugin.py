# Objective:
#   Prepare Metagenomics Data

# Step 1 - Rename the taxa

import pandas as pd
import os
import numpy as np


def shorten_names(abundance_df, samples_column="Unnamed: 0"):
    # Assume that samples column is unnamed


    columns = list(abundance_df.columns)
    columns.remove(samples_column)

    # Step 1 - remove unclassified bacteria
    columns_to_remove  =[]
    for column in columns:
        if column.split(";")[5]=="__" or column.split(";")[5]=="g__":
            columns_to_remove.append(column)
    abundance_df = abundance_df.drop(columns_to_remove, axis=1)

    # Step 2 - rename columns
    columns = list(abundance_df.columns)
    columns.remove(samples_column)

    rename_dict = {}
    taxa_count_dict = {}

    for column in columns:
        genus_name = column.split(";")[5].split("__")[1]
        if genus_name not in taxa_count_dict.keys():
            taxa_count_dict[genus_name] = 1
        else:
            taxa_count_dict[genus_name] += 1

        rename_dict[column] = genus_name + ".0" + str(taxa_count_dict[genus_name])
    abundance_df = abundance_df.rename(columns=rename_dict)
    abundance_df = abundance_df.rename(columns={samples_column:''})


    all_bacterial_names = list(rename_dict.values())
    print()
    #print("file {}".format(abundance_file))
    print("number of bacterias: {}".format(len(all_bacterial_names)))
    print("Columns are successfully renamed.")
    for element in all_bacterial_names:
        if all_bacterial_names.count(element)>1:
            print(element)
    return abundance_df

def normalize(abundance_df, samples_col="", toIndex=True):
    if toIndex:
        abundance_df.index = abundance_df[samples_col]
        del abundance_df[samples_col]
    samples = list(abundance_df.index)
    for sample in samples:
        abundance_df = abundance_df.apply(lambda row: row/sum(row), axis=1)
    return abundance_df

def combine_by_genus(abundance_df):
    taxa_list = list(abundance_df.columns)
    new_dict = {}
    new_dict[""] = []
    # Identify unique set of genus
    genus_set = []
    for t in taxa_list:
        genus = t.split(".")[0].strip("]").strip("[")
        if genus not in genus_set:
            genus_set.append(genus)
    # Create new combined dictionary:
    currently_added_genus = []
    for genus in genus_set:
        for taxa in taxa_list:
            current_taxa_genus = taxa.split(".")[0].strip("]").strip("[")
            if genus==current_taxa_genus:
                if genus not in currently_added_genus:
                    abundance_df[genus] = abundance_df[taxa]
                    currently_added_genus.append(genus)
                else:
                    abundance_df[genus] = abundance_df[genus] + abundance_df[taxa]
                pass
    abundance_df = abundance_df[genus_set]

    return  abundance_df

class PreprocessMetagenomicsPlugin:
    def input(self, inputfile):
        self.abundance_file = inputfile
        #abundance_file = "level-genus.csv"

    def run(self):
        pass

    def output(self, outputfile):
        output_abundance = outputfile+"_filtered.csv"#"abundance_filtered.csv"
        output_normalized = outputfile+"_normalized.csv"#"abundance_normalized.csv"
        abundance_df = pd.read_csv(self.abundance_file)
        # Step 1 - Shorten Names. If 2 of the same genus use X.01 and X.02
        abundance_df = shorten_names(abundance_df, "index")
        # # Step 2 - normalize
        # abundance_df = normalize(abundance_df)
        # abundance_df.to_csv("abundance/test.csv")
        # Step 3 - combine by genus
        abundance_df = combine_by_genus(abundance_df)
        abundance_df.to_csv(output_abundance, index=False)
        # Step 4 - normalized
        abundance_norm_df = normalize(abundance_df)
        abundance_norm_df.to_csv(output_normalized, index=True)
