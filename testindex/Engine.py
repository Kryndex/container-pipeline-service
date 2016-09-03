from NutsAndBolts import Environment, GlobalEnvironment
from sys import exit
from os import path
from glob import glob
import Validators
from Summary import Summary


class Engine:

    def __init__(self, indexd_location="./index.d", data_dump_directory="cccp-index-test"):

        self._success = False

        print "\nSetting up environment...\n"
        GlobalEnvironment.environment = Environment(data_dump_directory)

        print "\nChecking indexd directory\n"

        self._prepare_index_test_bench(indexd_location)

    def _prepare_index_test_bench(self, indexd_location):
        """Copies the indexd files into testbench so we can modify if needed without affecting originals"""

        if not path.exists(indexd_location):
            print ("\nInvalid indexd location specified.\n")
            exit(1)

        if not path.isdir(indexd_location):
            print "\nThe path specified must be a directory\n"
            exit(1)

        print "\nPreparing the test bench from the index.d files\n"
        potential_files = glob(indexd_location + "/*.yml")

        if len(potential_files) == 0 or (len(potential_files) == 1 and "index_template.yml" in potential_files):
            print "\nThe index.d format directory does not contain potential index files, exiting...\n"
            exit(1)

        GlobalEnvironment.environment.cleanup_index_testbench()

        for item in potential_files:
            if "index_template" not in item:
                if "/" in item:
                    file_name = path.split(item)[1]

                else:
                    file_name = item

                target_file = open(GlobalEnvironment.environment.indexd_test_bench + "/" + file_name, "w")
                target_file.write("Projects:\n")
                target_file.write(open(item, "r").read())

    def run(self):

        successlist = []

        for fl in glob(GlobalEnvironment.environment.indexd_test_bench + "/*.yml"):
            print "\nChecking the format"

            if Validators.IndexFormatValidator(fl).run():
                print "\nIndex format validated, moving to next step"
                print "Checking for correctness of provided values"

                if Validators.IndexProjectsValidator(fl).run():
                    successlist.append(True)

                else:
                    successlist.append(False)

            else:
                successlist.append(False)

        Summary.print_summary()

        if False in successlist:
            return False

        GlobalEnvironment.environment.teardown()

        return True