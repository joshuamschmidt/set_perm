import pysetperm as psp
import numpy as np

# import pandas as pd
# used for all sub analyses
n_perms = 50000
cores = 4
annotations = psp.AnnotationSet(annotation_file='data/genes.txt', range_modification=2000)
function_sets = psp.FunctionSets(function_set_file='data/kegg.txt', min_set_size=10, annotation_obj=annotations)
# specific inputs
e_candidates = psp.Variants(variant_file='data/eastern_candidates.txt')
e_candidates.annotate_variants(annotation_obj=annotations)
e_background = psp.Variants(variant_file='data/eastern_background.txt.gz')
e_background.annotate_variants(annotation_obj=annotations)

c_candidates = psp.Variants(variant_file='data/central_candidates.txt')
c_background = psp.Variants(variant_file='data/central_background.txt.gz')

e_test_obj = psp.TestObject(e_candidates,
                            e_background,
                            annotations,
                            function_sets)

# permutations
e_permutations = psp.Permutation(e_input, n_perms, cores)

# distributions across permutations
e_per_set = psp.SetPerPerm(e_permutations,
                           annotations,
                           e_input,
                           cores)

# results tables
e_results = make_results_table(e_input, annotations, e_per_set)


def make_results_table(input_obj, annotation_obj, permutation_set_obj):
    out = annotation_obj.annotation_sets.groupby('id', as_index=False).agg({'name': pd.Series.unique})
    out = out[out['id'].isin(annotation_obj.annotation_array_ids)]
    out = out.join(input_obj.candidate_features_per_set.set_index('id'), on='id')
    out['mean_n_resample'] = permutation_set_obj.mean_per_set
    out['emp_p_e'] = permutation_set_obj.p_enrichment
    out['emp_p_d'] = permutation_set_obj.p_depletion
    out['fdr_e'] = psp.fdr_from_p_matrix(permutation_set_obj.set_n_per_perm, out['emp_p_e'], method='enrichment')
    out['fdr_d'] = psp.fdr_from_p_matrix(permutation_set_obj.set_n_per_perm, out['emp_p_d'], method='depletion')
    out['BH_fdr_e'] = psp.p_adjust_bh(out['emp_p_e'])
    out['BH_fdr_d'] = psp.p_adjust_bh(out['emp_p_d'])
    out = out.sort_values('emp_p_e')
    return out
