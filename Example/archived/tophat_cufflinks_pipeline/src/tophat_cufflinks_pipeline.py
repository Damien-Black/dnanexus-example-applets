#!/usr/bin/env python
#
# Copyright (C) 2013 DNAnexus, Inc.
#   This file is part of dnanexus-example-applets.
#   You may use this file under the terms of the Apache License, Version 2.0;
#   see the License.md file for more information.


# tophat_cufflinks_pipeline 0.0.1
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
import multiprocessing

@dxpy.entry_point('main')
def main(fastqs, reference, indexed_ref, gene_model, tophat_options="", cufflinks_options="", fastq_pairs=None):

    # The following line(s) initialize your data object inputs on the platform
    # into dxpy.DXDataObject instances that you can start using immediately.

    reference = dxpy.DXFile(reference)
    indexed_ref = dxpy.DXFile(indexed_ref)
    gene_model = dxpy.DXFile(gene_model)

    # The following line(s) download your file inputs to the local file system
    # using variable names for the filenames.

    dxpy.download_dxfile(reference.get_id(), "reference.fasta.fa.gz")
    dxpy.download_dxfile(indexed_ref.get_id(), "indexed_ref.tar.gz")
    dxpy.download_dxfile(gene_model.get_id(), "gene_model.gtf")

    # Fill in your application code here.

    subprocess.check_call("gunzip reference.fasta.fa.gz", shell=True)
    subprocess.check_call("tar xzf indexed_ref.tar.gz", shell=True)

    subprocess.check_call("ls -l", shell=True)

    # download and make lists of fastq filenames

    fq_filenames = []
    fq_pair_filenames = []
    if fastq_pairs != None:
        assert(len(fastqs) == len(fastq_pairs))
    for i in range(len(fastqs)):
        dxpy.download_dxfile(fastqs[i], str(i)+"_1.fq.gz")
        subprocess.check_call("gunzip "+str(i)+"_1.fq.gz", shell=True)
        fq_filenames.append(str(i)+"_1.fq")
        if fastq_pairs != None:
            dxpy.download_dxfile(fastq_pairs[i], str(i)+"_2.fq.gz")
            subprocess.check_call("gunzip "+str(i)+"_2.fq.gz", shell=True)
            fq_pair_filenames.append(str(i)+"_2.fq")

    fq_filenames = ",".join(fq_filenames)
    fq_pair_filenames = ",".join(fq_pair_filenames)

    num_cpus = multiprocessing.cpu_count()

    subprocess.check_call("ls -l", shell=True)
    print fq_filenames
    print tophat_options

    tophat_cmd = "tophat -p "+str(num_cpus)+" "+tophat_options+" -G gene_model.gtf reference.fasta "+fq_filenames+" "+fq_pair_filenames
    print "Running: "+tophat_cmd
    subprocess.check_call(tophat_cmd, shell=True)

    cufflinks_cmd = "cufflinks -p "+str(num_cpus)+" -G gene_model.gtf -o cufflinks_out "+cufflinks_options+" tophat_out/accepted_hits.bam"
    print "Running: "+cufflinks_cmd
    subprocess.check_call(cufflinks_cmd, shell=True)

    subprocess.check_call("ls -l", shell=True)

    subprocess.check_call("tar czf cufflinks_output.tar.gz cufflinks_out/", shell=True)

    # The following line(s) use the Python bindings to upload your file outputs
    # after you have created them on the local file system.  It assumes that you
    # have used the output field name for the filename for each output, but you
    # can change that behavior to suit your needs.

    mappings = dxpy.upload_local_file("tophat_out/accepted_hits.bam");
    cufflinks_out = dxpy.upload_local_file("cufflinks_output.tar.gz");

    # The following line fills in some basic dummy output and assumes
    # that you have created variables to represent your output with
    # the same name as your output fields.

    output = {}
    output["BAM_file"] = dxpy.dxlink(mappings)
    output["cufflinks_out"] = dxpy.dxlink(cufflinks_out)

    return output

dxpy.run()
