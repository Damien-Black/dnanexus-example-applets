#!/usr/bin/env python
#
# Copyright (C) 2013 DNAnexus, Inc.
#   This file is part of dnanexus-example-applets.
#   You may use this file under the terms of the Apache License, Version 2.0;
#   see the License.md file for more information.


# gatk_variant_annotator 0.0.1
# Generated by dx-app-wizard.
#
# Basic execution pattern: Your app will run on a single machine from
# beginning to end.
#
# See http://wiki.dnanexus.com/Developer-Tutorials/Intro-to-Building-Apps
# for instructions on how to modify this file.
#
# DNAnexus Python Bindings (dxpy) documentation:
#   http://autodoc.dnanexus.com/bindings/python/current/

import os
import dxpy

import subprocess

@dxpy.entry_point('main')
def main(input_vcf, reference, input_bam=None, annotation_vcf=None, comparison_vcf=None, dbsnp=None, genes=None, gatk_annotator_params='', snpeff_build_params='-gtf22 -v', snpeff_annotate_params='-v -onlyCoding true -i vcf -o vcf'):

    # The following line(s) initialize your data object inputs on the platform
    # into dxpy.DXDataObject instances that you can start using immediately.

    input_vcf = dxpy.DXFile(input_vcf)
    reference = dxpy.DXFile(reference)
    ref_name = reference.describe()['name'].replace(".gz", "")

    if genes != None:
        genes = dxpy.DXFile(genes)
        genes_name = genes.describe()['name']

    if annotation_vcf != None:
        annotation_vcf = dxpy.DXFile(annotation_vcf)
        annotation_name = annotation_vcf.describe()['name']

    if comparison_vcf != None:
        comparison_vcf = dxpy.DXFile(comparison_vcf)
        comparison_name = comparison_vcf.describe()['name']

    if dbsnp != None:
        print "dbsnp present"
        dbsnp = dxpy.DXFile(dbsnp)
        dbsnp_name = dbsnp.describe()['name']

    if input_bam != None:
        input_bam = dxpy.DXFile(input_bam)
        bam_name = input_bam.describe()['name']


    base_name = input_vcf.describe()['name'].replace(".vcf", '')
    vcf_name = input_vcf.describe()['name']

    # The following line(s) download your file inputs to the local file system
    # using variable names for the filenames.

    dxpy.download_dxfile(input_vcf.get_id(), "%s" % vcf_name)
    dxpy.download_dxfile(reference.get_id(), "%s.gz" % ref_name)
    if genes != None:
        dxpy.download_dxfile(genes.get_id(), "%s" % genes_name)
    if annotation_vcf != None:
        dxpy.download_dxfile(annotation_vcf.get_id(), "%s" % annotation_name)
    if comparison_vcf != None:
        dxpy.download_dxfile(comparison_vcf.get_id(), "%s" % comparison_name)
    if dbsnp != None:
        dxpy.download_dxfile(dbsnp.get_id(), "%s" % dbsnp_name)
    if input_bam != None:
        dxpy.download_dxfile(input_bam.get_id(), "%s" % bam_name)

    # Fill in your application code here.

    subprocess.check_call("gzip -d %s.gz" % ref_name, shell=True)

    if genes != None:
        subprocess.check_call("mv %s /snpEff_2_0_5/data/genomes/%s" % (ref_name, ref_name), shell=True)
        genes_file = open("/snpEff_2_0_5/snpEff.config", "a+")
        genes_file.write("\n%s.genome : Custom_species\n" % ref_name.replace(".fa", ""))
        genes_file.close()
        subprocess.check_call("mkdir /snpEff_2_0_5/data/%s" % ref_name.replace(".fa", ""), shell=True)
        subprocess.check_call("mv %s /snpEff_2_0_5/data/%s/%s" % (genes_name, ref_name.replace(".fa", ""), genes_name), shell=True)
        #Build the snpeff database
        subprocess.check_call("java -Xmx4g -jar /snpEff_2_0_5/snpEff.jar build -c /snpEff_2_0_5/snpEff.config %s %s" % (snpeff_build_params, ref_name.replace(".fa", "")), shell=True)
        # Produce snpeff annotation file
        subprocess.check_call("java -Xmx4g -jar /snpEff_2_0_5/snpEff.jar -c /snpEff_2_0_5/snpEff.config %s %s %s > snpeff.vcf" % (snpeff_annotate_params, ref_name.replace(".fa", ""), vcf_name), shell=True)
        ref_name = "/snpEff_2_0_5/data/genomes/%s"

    try:
        subprocess.check_call("tabix -p vcf %s" % dbsnp_name, shell=True)
    except:
        print "Tried tabix indexing dbsnp file and failed. Proceeding as though file is uncompressed VCF"


    annotate_command = "java -Xmx4g -jar /opt/jar/GenomeAnalysisTK.jar -T VariantAnnotator -R %s --variant %s -L %s -o %s_annotated.vcf %s" % (ref_name, vcf_name, vcf_name, base_name, gatk_annotator_params)
    if dbsnp != None:
        annotate_command += " --dbsnp %s" % dbsnp_name
    if input_bam != None:
        annotate_command += " -I %s" % input_bam
    if genes != None:
        annotate_command += " -A SnpEff --snpEffFile snpeff.vcf"
    if annotation_vcf != None:
        annotate_command += " -resource %s" % annotation_vcf
    if comparison_vcf != None:
        annotate_command += " -comp %s" % comparison_name

    subprocess.check_call(annotate_command, shell=True)

    # The following line(s) use the Python bindings to upload your file outputs
    # after you have created them on the local file system.  It assumes that you
    # have used the output field name for the filename for each output, but you
    # can change that behavior to suit your needs.

    annotated_variants = dxpy.upload_local_file("%s_annotated.vcf" % base_name);

    # The following line fills in some basic dummy output and assumes
    # that you have created variables to represent your output with
    # the same name as your output fields.

    output = {}
    output["annotated_variants"] = dxpy.dxlink(annotated_variants)

    return output

dxpy.run()
