'''
Note that we can't use an existing Python wrapper (such as https://github.com/LoLei/spmf-py)
for SPMF, which is a Java jar file. The Python wrapper above isn't maintained and there
might be a bug in it as well.
'''

import os
import subprocess

# NOTE: This path is relative to this project's root dir
SPMF_JAR_FILE_PATH = os.path.join("libs/", "spmf.jar")

def run_spmf(alg_name, input_file, output_file, alg_args):
    '''
    Runs spmf (with the provided arguments) via a child process

    @param alg_name: string         Algorithm name to run (ex: FPClose)
    @param input_file: string       Input file pathname to read patterns from
    @param output_file: string      Output file pathname to write to
    @param alg_args: list(string)   Additional args needed by algorithm

    '''
    subproc_command = ["java", "-jar", SPMF_JAR_FILE_PATH, "run", alg_name, input_file, output_file]
    subproc_command.extend(alg_args)

    process = subprocess.Popen(subproc_command)
    process.communicate() # Wait for subprocess to end
    if process.returncode != 0:
        print("ERROR: %s did not execute correctly" % ' '.join(subproc_command))
        exit(1)
    print("Success")