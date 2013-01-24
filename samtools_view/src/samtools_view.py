#!/usr/bin/env python
# samtools_view 0.0.1
# Generated by dx-app-wizard.
#
# Basic execution pattern: Your app will run on a single machine from
# beginning to end.
#
# See http://wiki.dnanexus.com/Building-Your-First-DNAnexus-App for
# instructions on how to modify this file.
#
# DNAnexus Python Bindings (dxpy) documentation:
#   http://autodoc.dnanexus.com/bindings/python/current/

import os
import dxpy

import subprocess

@dxpy.entry_point('main')
def main(BAM, params, suffix='_view'):

    # The following line(s) initialize your data object inputs on the platform
    # into dxpy.DXDataObject instances that you can start using immediately.

    BAM = dxpy.DXFile(BAM)

    # The following line(s) download your file inputs to the local file system
    # using variable names for the filenames.

    dxpy.download_dxfile(BAM.get_id(), "input.bam")

    # The following line extracts the name from the file object so that
    # outputs can be named intelligently. It is not automatically generated by
    # the app wizard.

    name = BAM.describe()['name']

    # Fill in your application code here.

    subprocess.check_call("samtools index input.bam", shell=True)
    subprocess.check_call("samtools view input.bam %s > %s" % (params, name+suffix), shell=True)

    # The following line(s) use the Python bindings to upload your file outputs
    # after you have created them on the local file system.  It assumes that you
    # have used the output field name for the filename for each output, but you
    # can change that behavior to suit your needs.

    BAM = dxpy.upload_local_file(name+suffix);

    # The following line fills in some basic dummy output and assumes
    # that you have created variables to represent your output with
    # the same name as your output fields.

    output = {}
    output["BAM"] = dxpy.dxlink(BAM)

    return output

dxpy.run()
